import uuid
from datetime import datetime
from app.agents.state import TripPlannerState

def final_planner_agent_node(state: TripPlannerState) -> TripPlannerState:
    """
    Final Planner Agent:
    Synthesizes and packages the end-to-end travel dossier:
    interactive map markers, seasonal packing checklist, local survival guide,
    and verified itinerary into a unified responsive response structure.
    """
    destination = state.get("destination", "Tokyo, Japan")
    origin = state.get("origin", "New York, USA")
    duration = int(state.get("duration_days", 5))
    currency = state.get("currency", "USD")
    travelers_count = int(state.get("travelers_count", 2))
    traveler_type = state.get("traveler_type", "Couple")
    
    dest_data = state.get("destination_data", {})
    budget_strat = state.get("budget_strategy", {})
    pref_profile = state.get("preferences_profile", {})
    research = state.get("research_data", {})
    itinerary = state.get("itinerary_draft", [])
    breakdown = state.get("budget_breakdown", {})

    logs = [{
        "agent": "Final Planner",
        "status": "running",
        "message": f"Compiling final multi-agent dossier, generating map waypoints, and packing checklist...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]

    trip_id = f"trip_{uuid.uuid4().hex[:8]}"
    base_coords = dest_data.get("coordinates", [35.6762, 139.6503])

    # 1. Map Markers Extraction
    map_markers = []
    marker_id = 1
    for day in itinerary:
        d_num = day.get("day_number", 1)
        for act in day.get("activities", []):
            coords = act.get("coordinates", [0.0, 0.0])
            # If coordinates are 0,0, offset slightly around destination base coordinates
            if coords == [0.0, 0.0] or not coords:
                lat_offset = (hash(act.get("title", "")) % 20 - 10) * 0.003
                lng_offset = (hash(act.get("location", "")) % 20 - 10) * 0.003
                coords = [round(base_coords[0] + lat_offset, 5), round(base_coords[1] + lng_offset, 5)]
                act["coordinates"] = coords
            
            map_markers.append({
                "id": f"marker_{marker_id}",
                "day": d_num,
                "title": act.get("title", f"Stop {marker_id}"),
                "description": act.get("description", ""),
                "category": act.get("category", "Sightseeing"),
                "coordinates": coords,
                "time_slot": act.get("time_slot", "Morning")
            })
            marker_id += 1

    # 2. Intelligent Packing Checklist
    packing_checklist = [
        {
            "category": "Documents & Logistics",
            "items": [
                "Passport / Valid Photo ID & Photocopies",
                "Travel medical insurance policy & offline copies",
                "Flight boarding passes & hotel confirmation vouchers",
                "Local currency in cash + zero-foreign-transaction-fee credit card",
                "International Driving Permit (if renting a car/scooter)"
            ]
        },
        {
            "category": "Travel Tech & Electronics",
            "items": [
                "Universal travel power adapter with surge protector",
                "High-capacity portable power bank (10,000+ mAh) for all-day navigation",
                "Noise-cancelling headphones for flights & train transit",
                "Offline downloaded Google / Apple Maps for the destination",
                "eSIM profile activated on smartphone"
            ]
        },
        {
            "category": "Clothing & Footwear",
            "items": [
                "Ergonomic, well-broken-in walking shoes (10,000 - 18,000 daily steps)",
                "Breathable lightweight moisture-wicking layers",
                "Packable waterproof rain jacket or compact travel umbrella",
                "1 smart-casual evening outfit for upscale dinners & theater",
                "Modest attire covering shoulders/knees for sacred shrines and historic temples"
            ]
        },
        {
            "category": "Health & Destination Essentials",
            "items": [
                "Compact first-aid kit (band-aids, blister cushions, pain relief, motion sickness pills)",
                "Prescription medications in original containers with doctor note",
                "Refillable insulated water bottle",
                "Sun protection (SPF 50+ sunscreen, polarized sunglasses, sun hat)",
                "Hand sanitizer & pocket tissues"
            ]
        }
    ]

    title = f"{duration}-Day {destination.split(',')[0]} {pref_profile.get('core_themes', ['Discovery'])[0]} Escape"

    final_payload = {
        "trip_id": trip_id,
        "title": title,
        "destination": destination,
        "origin": origin,
        "duration_days": duration,
        "dates": f"{duration} Days Exploration",
        "travelers_count": travelers_count,
        "traveler_type": traveler_type,
        "currency": currency,
        "total_budget": float(breakdown.get("total_budget", state.get("budget_total", 0.0))),
        "estimated_cost": float(breakdown.get("estimated_total_cost", 0.0)),
        "vibe_summary": dest_data.get("tagline", f"An unforgettable journey across {destination}."),
        "climate_guide": dest_data.get("climate_overview", "Favorable sightseeing climate throughout the journey."),
        "local_customs": dest_data.get("cultural_guidelines", [
            "Greet locals warmly and observe monument photography rules.",
            "Always keep digital and paper backups of essential travel documents."
        ]),
        "emergency_contacts": (
            dest_data.get("emergency_contacts")
            or dest_data.get("emergency")
            or {
                "police": "100 / 112" if (currency == "INR" or "india" in destination.lower()) else "112 / 911",
                "ambulance": "102 / 108" if (currency == "INR" or "india" in destination.lower()) else "112 / 911",
                "tourist_helpline": "1363" if (currency == "INR" or "india" in destination.lower()) else "112"
            }
        ),
        "itinerary": itinerary,
        "budget_breakdown": breakdown,
        "map_markers": map_markers,
        "packing_checklist": packing_checklist,
        "dining_recommendations": research.get("dining_recommendations", []),
        "recommended_places": research.get("curated_spots", []),
        "secret_gems": research.get("secret_gems", []),
        "transportation": breakdown.get("transport_mode") or state.get("transport_mode", "Recommended Intercity Transit"),
        "accommodation": state.get("accommodation_type", "Hotel / Boutique Stay"),
        "travel_tips": dest_data.get("safety_tips", [
            "Keep emergency contact numbers saved offline.",
            "Use metered taxis or verified ride-hailing applications.",
            "Stay aware of your surroundings in crowded tourist landmarks."
        ]),
        "preferences_profile": pref_profile,
        "budget_strategy": budget_strat,
        "provider": state.get("provider_used") or ("Google Gemini" if state.get("provider") != "mock" else "WanderAI Smart Engine (Offline Fallback)"),
        "is_fallback": bool(state.get("is_fallback", False)),
        "fallback_reason": state.get("fallback_reason", "")
    }

    logs.append({
        "agent": "Final Planner",
        "status": "completed",
        "message": f"Travel dossier completely assembled! {len(itinerary)} days, {len(map_markers)} geo-waypoints, ready for frontend.",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # Combine all accumulated logs so response has full history
    all_accumulated_logs = list(state.get("agent_logs", [])) + logs
    final_payload["agent_logs"] = all_accumulated_logs
    
    return {
        "final_trip_plan": final_payload,
        "agent_logs": logs
    }
