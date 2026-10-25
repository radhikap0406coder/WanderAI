import time
import json
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.models.request import TripPlanRequest, ChatRequest
from app.models.user import UserRegisterRequest, UserLoginRequest, UserResponse, AuthResponse
from app.graph.trip_graph import trip_graph
from app.data.destination_knowledge import DESTINATIONS_DATA
from app.db.database import (
    save_trip,
    get_trip,
    list_trips,
    delete_trip,
    create_user,
    get_user_by_email,
    get_user_by_id,
)
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.services.chat_service import generate_chat_reply


app = FastAPI(
    title="WanderAI - AI Trip Planner",
    description="Intelligent AI Trip Planner API with Complete Itinerary Persistence & Authentication",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP Bearer for optional/required token authentication
security = HTTPBearer(auto_error=False)


# --------------------------------------------------
# AUTHENTICATION DEPENDENCIES
# --------------------------------------------------

async def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Extracts and verifies JWT token from Authorization header or cookie.
    Raises 401 if unauthenticated.
    """
    token = None
    if creds and creds.credentials:
        token = creds.credentials
    elif "wanderai_token" in request.cookies:
        token = request.cookies.get("wanderai_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """
    Extracts user if valid authentication is present; returns None for guests.
    """
    token = None
    if creds and creds.credentials:
        token = creds.credentials
    elif "wanderai_token" in request.cookies:
        token = request.cookies.get("wanderai_token")

    if not token:
        return None

    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        return None

    return get_user_by_id(payload["sub"])


# --------------------------------------------------
# HELPER: Prepare complete trip data before saving
# --------------------------------------------------

def prepare_trip_for_saving(
    plan: dict,
    request_data: dict,
    execution_time: float,
    user_id: Optional[str] = None,
) -> dict:
    """
    Combines the original user request with the complete
    generated multi-agent dossier before database saving.
    """
    if not isinstance(plan, dict) or not plan:
        raise ValueError("The trip planner returned an empty plan.")

    saved_plan = dict(plan)

    # Ensure every saved trip has a unique ID.
    if not saved_plan.get("trip_id"):
        saved_plan["trip_id"] = f"trip_{uuid.uuid4().hex[:8]}"

    # Associate user ownership
    saved_plan["user_id"] = user_id

    # Preserve the original request parameters separately.
    saved_plan["trip_request"] = dict(request_data)

    # Fill missing basic fields without overwriting generated data.
    defaults = {
        "title": f"Trip to {request_data.get('destination', 'Destination')}",
        "origin": request_data.get("origin", ""),
        "destination": request_data.get("destination", ""),
        "start_date": request_data.get("start_date"),
        "duration_days": request_data.get("duration_days", 5),
        "travelers_count": request_data.get("travelers_count", 2),
        "traveler_type": request_data.get("traveler_type", "Travelers"),
        "currency": request_data.get("currency", "USD"),
        "agent_logs": [],
    }

    for key, value in defaults.items():
        if saved_plan.get(key) is None:
            saved_plan[key] = value

    # Always ensure estimated_cost and total_budget strictly match the budget_breakdown
    budget = saved_plan.get("budget_breakdown", {})
    if isinstance(budget, dict) and budget.get("estimated_total_cost") is not None:
        saved_plan["estimated_cost"] = float(budget.get("estimated_total_cost", 0.0))
        saved_plan["total_budget"] = float(budget.get("total_budget", saved_plan.get("total_budget", 0.0)))

    # Record actual provider used and fallback status
    actual_provider = plan.get("provider") or (
        "Google Gemini" if settings.GEMINI_API_KEY and request_data.get("provider") != "mock" else "WanderAI Smart Engine (Offline Fallback)"
    )
    saved_plan["provider"] = actual_provider
    saved_plan["is_fallback"] = bool(plan.get("is_fallback", False))
    if plan.get("fallback_reason"):
        saved_plan["fallback_reason"] = plan["fallback_reason"]

    # Keep all submitted preferences available in the saved record.
    for key, value in request_data.items():
        if key not in ("provider", "is_fallback"):
            saved_plan.setdefault(key, value)

    saved_plan["execution_time_seconds"] = round(execution_time, 2)
    saved_plan.setdefault("created_at", datetime.now().isoformat())

    return saved_plan


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
async def health_check():
    has_gemini = bool(settings.GEMINI_API_KEY)
    return {
        "status": "online",
        "provider": "Google Gemini" if has_gemini else "WanderAI Smart Engine",
        "features": {
            "gemini_available": has_gemini,
            "authentication": True,
            "database": "SQLite 3",
        },
    }


# --------------------------------------------------
# USER AUTHENTICATION ENDPOINTS
# --------------------------------------------------

@app.post("/api/auth/register", response_model=AuthResponse)
async def register(req: UserRegisterRequest, response: Response):
    """
    Registers a new user account with hashed password.
    """
    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    pw_hash = hash_password(req.password)
    user = create_user(
        full_name=req.full_name,
        email=req.email,
        password_hash=pw_hash,
    )

    token = create_access_token(user_id=user["id"], email=user["email"])

    # Set HTTP-only cookie for secure browser sessions
    response.set_cookie(
        key="wanderai_token",
        value=token,
        httponly=True,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "created_at": user["created_at"],
        },
    }


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(req: UserLoginRequest, response: Response):
    """
    Authenticates user credentials and returns JWT bearer token + cookie.
    """
    user = get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user_id=user["id"], email=user["email"])

    response.set_cookie(
        key="wanderai_token",
        value=token,
        httponly=True,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "created_at": user["created_at"],
        },
    }


@app.post("/api/auth/logout")
async def logout(response: Response):
    """
    Logs out the user and clears the session cookie.
    """
    response.delete_cookie(key="wanderai_token", samesite="lax")
    return {"status": "success", "message": "Logged out successfully"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns the authenticated user's profile.
    """
    return {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "created_at": user["created_at"],
    }


@app.get("/api/auth/my-trips")
async def get_my_trips(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns all saved trip summaries owned by the authenticated user.
    """
    trips = list_trips(user_id=user["id"])
    return {"trips": trips}


# --------------------------------------------------
# FEATURED DESTINATIONS
# --------------------------------------------------

@app.get("/api/destinations/featured")
async def get_featured_destinations():
    featured = []
    for key, data in DESTINATIONS_DATA.items():
        featured.append({
            "id": key,
            "name": data["name"],
            "country": data["country"],
            "tagline": data["tagline"],
            "description": data["description"],
            "image_url": data["image_url"],
            "recommended_duration": data["recommended_duration"],
            "popular_interests": data["popular_interests"],
            "coordinates": data["coordinates"],
        })
    return {"destinations": featured}


# --------------------------------------------------
# SAVED TRIP DATABASE ENDPOINTS
# --------------------------------------------------

@app.get("/api/trips")
async def get_saved_trips(
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Returns saved trip summaries.
    If authenticated, returns the user's private trips.
    If guest, returns guest trips.
    """
    user_id = user["id"] if user else None
    trips = list_trips(user_id=user_id)
    return {"trips": trips}


@app.get("/api/trips/{trip_id}")
async def get_saved_trip_by_id(
    trip_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Returns the complete saved itinerary.
    Enforces user isolation: users can only view their own trips.
    """
    user_id = user["id"] if user else None
    trip = get_trip(trip_id, user_id=user_id)

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found or you do not have permission to access it.",
        )

    return trip


@app.delete("/api/trips/{trip_id}")
async def remove_saved_trip(
    trip_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Deletes a saved trip from SQLite.
    Enforces ownership: only the owner can delete their trip.
    """
    user_id = user["id"] if user else None
    success = delete_trip(trip_id, user_id=user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Trip not found, already deleted, or permission denied.",
        )

    return {
        "status": "success",
        "message": "Trip deleted successfully",
    }


# --------------------------------------------------
# CHAT ASSISTANT
# --------------------------------------------------

@app.post("/api/chat")
async def chat_with_wanderai(req: ChatRequest):
    """Travel chat assistant with Gemini and fallback."""
    history_dicts = [
        {"role": message.role, "content": message.content}
        for message in (req.history or [])
    ]

    reply_obj = generate_chat_reply(
        message=req.message,
        history=history_dicts,
        trip_context=req.trip_context,
        provider="auto",
        api_key_override=req.api_key,
    )

    return reply_obj


# --------------------------------------------------
# TRIP PLANNING STAGE LABELS
# --------------------------------------------------

STAGE_LABELS = {
    "destination_agent": "Analyzing Destination & Climate",
    "budget_agent": "Evaluating Budget & Allocations",
    "preferences_agent": "Customizing Travel Preferences",
    "research_agent": "Discovering Sights & Local Dining",
    "itinerary_generator": "Crafting Day-by-Day Schedule",
    "budget_calculator": "Calculating Estimated Expenses",
    "final_planner": "Finalizing Complete Itinerary",
}


def build_initial_state(req: TripPlanRequest) -> dict:
    """Converts the user's request into the LangGraph input."""
    return {
        "origin": req.origin,
        "destination": req.destination,
        "start_date": req.start_date,
        "duration_days": req.duration_days,
        "budget_total": req.budget_total,
        "currency": req.currency,
        "travelers_count": req.travelers_count,
        "traveler_type": req.traveler_type,
        "adults_count": req.adults_count,
        "children_count": req.children_count,
        "is_per_person_budget": req.is_per_person_budget,
        "transport_mode": req.transport_mode,
        "interests": req.interests,
        "accommodation_type": req.accommodation_type,
        "pace": req.pace,
        "notes": req.notes,
        "api_key": req.api_key,
        "provider": req.provider or "auto",
        "agent_logs": [],
    }


def build_request_data(req: TripPlanRequest) -> dict:
    """Returns user inputs without saving a private API key."""
    if hasattr(req, "model_dump"):
        return req.model_dump(exclude={"api_key"})
    return req.dict(exclude={"api_key"})


# --------------------------------------------------
# STANDARD TRIP PLANNING ENDPOINT
# --------------------------------------------------

@app.post("/api/plan-trip")
async def plan_trip_sync(
    req: TripPlanRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Generates a complete itinerary with AI, saves the result to SQLite with user ownership, and returns to frontend.
    """
    start_time = time.time()
    initial_state = build_initial_state(req)
    request_data = build_request_data(req)
    user_id = user["id"] if user else None

    try:
        result = trip_graph.invoke(initial_state)
        generated_plan = result.get("final_trip_plan")

        if not isinstance(generated_plan, dict) or not generated_plan:
            raise HTTPException(
                status_code=500,
                detail="The trip planner did not generate a final itinerary.",
            )

        prepared_plan = prepare_trip_for_saving(
            plan=generated_plan,
            request_data=request_data,
            execution_time=time.time() - start_time,
            user_id=user_id,
        )

        # Save the complete generated plan to SQLite
        save_trip(prepared_plan, user_id=user_id)

        return prepared_plan

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate trip plan: {str(exc)}",
        ) from exc


# --------------------------------------------------
# STREAMING TRIP PLANNING ENDPOINT
# --------------------------------------------------

@app.post("/api/plan-trip/stream")
async def plan_trip_stream(
    req: TripPlanRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Streams progress messages and sends the final itinerary
    and saving the complete plan to SQLite with user ownership.
    """
    initial_state = build_initial_state(req)
    request_data = build_request_data(req)
    user_id = user["id"] if user else None

    async def event_generator():
        start_time = time.time()

        yield (
            "data: "
            + json.dumps({
                "type": "init",
                "message": f"Planning your dream vacation to {req.destination}...",
            })
            + "\n\n"
        )

        try:
            latest_plan = None

            async for chunk in trip_graph.astream(initial_state):
                for node_name, node_output in chunk.items():
                    step_title = STAGE_LABELS.get(
                        node_name,
                        "Planning Travel Step",
                    )

                    # Stream friendly progress logs.
                    logs = node_output.get("agent_logs", [])

                    for log in logs:
                        clean_log = {
                            "step": step_title,
                            "status": log.get("status", "completed"),
                            "message": (
                                log.get("message", "")
                                .replace("Agent: ", "")
                                .replace("LangGraph", "AI")
                            ),
                            "timestamp": log.get("timestamp", ""),
                        }

                        yield (
                            "data: "
                            + json.dumps({
                                "type": "log",
                                "node": node_name,
                                "log": clean_log,
                            })
                            + "\n\n"
                        )

                    if "final_trip_plan" in node_output:
                        latest_plan = node_output["final_trip_plan"]

                await asyncio.sleep(0.04)

            if not isinstance(latest_plan, dict) or not latest_plan:
                yield (
                    "data: "
                    + json.dumps({
                        "type": "error",
                        "message": "Could not finalize trip plan",
                    })
                    + "\n\n"
                )
                return

            # Prepare basic fields and preserve original request parameters
            latest_plan = prepare_trip_for_saving(
                plan=latest_plan,
                request_data=request_data,
                execution_time=time.time() - start_time,
                user_id=user_id,
            )



            # Clean logs for the user-facing response.
            if "agent_logs" in latest_plan:
                cleaned_logs = []
                for log in latest_plan["agent_logs"]:
                    agent_name = log.get("agent", "")
                    cleaned_logs.append({
                        "step": (
                            agent_name.replace("Agent", "").strip()
                            or "Trip Planning"
                        ),
                        "status": log.get("status", "completed"),
                        "message": (
                            log.get("message", "")
                            .replace("Agent: ", "")
                            .replace("LangGraph", "AI")
                        ),
                        "timestamp": log.get("timestamp", ""),
                    })
                latest_plan["agent_logs"] = cleaned_logs

            # Save complete itinerary in SQLite 
            save_trip(latest_plan, user_id=user_id)

            yield (
                "data: "
                + json.dumps({
                    "type": "complete",
                    "data": latest_plan,
                })
                + "\n\n"
            )

        except Exception as exc:
            yield (
                "data: "
                + json.dumps({
                    "type": "error",
                    "message": str(exc),
                })
                + "\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# --------------------------------------------------
# EXPORT ITINERARY AS MARKDOWN
# --------------------------------------------------

@app.post("/api/export/markdown")
async def export_trip_markdown(payload: dict):
    """Exports a generated itinerary as Markdown."""
    destination = payload.get("destination", "Trip")
    duration = payload.get("duration_days", 5)
    currency = payload.get("currency", "USD")
    itinerary = payload.get("itinerary", [])
    budget = payload.get("budget_breakdown", {})
    checklist = payload.get("packing_checklist", [])

    lines = [
        f"# Travel Itinerary: {payload.get('title', destination)}",
        f"**Destination:** {destination} | **Origin:** {payload.get('origin', 'N/A')}",
        (
            f"**Duration:** {duration} days | "
            f"**Travelers:** {payload.get('travelers_count', 2)} "
            f"({payload.get('traveler_type', 'Travelers')})"
        ),
        f"**Vibe:** {payload.get('vibe_summary', '')}",
        "\n---\n",
        "## Financial Breakdown",
        f"- **Target Budget:** {currency} {budget.get('total_budget', 0):,.2f}",
        f"- **Estimated Expenditure:** {currency} {budget.get('estimated_total_cost', 0):,.2f}",
        (
            f"- **Variance:** {currency} {budget.get('variance', 0):+,.2f} "
            f"({budget.get('status', 'N/A')})"
        ),
        (
            f"- **Estimated Daily Spend per Person:** {currency} "
            f"{budget.get('per_person_per_day', 0):,.2f}"
        ),
        "\n### Category Allocations:",
    ]

    for category in budget.get("categories", {}).values():
        lines.append(
            f"- **{category.get('name', 'Category')}:** "
            f"{currency} {category.get('allocated_amount', 0):,.2f} "
            f"({category.get('percentage', 0)}%) — "
            f"{category.get('description', '')}"
        )

    lines.append("\n---\n## Day-by-Day Schedule\n")

    for day in itinerary:
        city_suffix = f" [{day.get('current_city')}]" if day.get("current_city") else ""
        lines.append(f"### {day.get('date_label', '')} — {day.get('theme', '')}{city_suffix}")
        if day.get("travel_leg"):
            lines.append(f"**Travel Leg:** {day.get('travel_leg')}")
        if day.get("overnight_stay"):
            lines.append(f"**Overnight Stay:** {day.get('overnight_stay')}")
        lines.append(f"*{day.get('summary', '')}*\n")

        for activity in day.get("activities", []):
            lines.append(
                f"- **{activity.get('time_slot', '')} "
                f"({activity.get('time', '')}):** "
                f"{activity.get('title', '')}"
            )
            lines.append(f"  {activity.get('description', '')}")
            lines.append(
                f"  Location: {activity.get('location', '')} | "
                f"Estimated Cost: {currency} "
                f"{activity.get('estimated_cost', 0):,.2f}"
            )

            if activity.get("tips"):
                lines.append(f"  Tip: {activity['tips']}")

        lines.append(
            f"**Day Total:** {currency} {day.get('day_total_cost', 0):,.2f} | "
            f"Transit: {day.get('transit_tips', '')}\n"
        )

    lines.append("\n---\n## Packing Checklist\n")

    for group in checklist:
        lines.append(f"### {group.get('category', 'General')}")
        for item in group.get("items", []):
            lines.append(f"- [ ] {item}")
        lines.append("")

    return PlainTextResponse(
        "\n".join(lines),
        media_type="text/markdown",
    )


# --------------------------------------------------
# SERVE BUILT FRONTEND IF AVAILABLE
# --------------------------------------------------

frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
dist_path = frontend_dir / "dist"
static_dir = dist_path if dist_path.exists() and (dist_path / "index.html").exists() else frontend_dir

if static_dir.exists() and (static_dir / "index.html").exists():
    app.mount(
        "/",
        StaticFiles(directory=str(static_dir), html=True),
        name="static",
    )
