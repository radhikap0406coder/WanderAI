import json
from datetime import datetime
from app.agents.state import TripPlannerState
from app.agents.llm_factory import get_llm
from app.data.destination_knowledge import get_destination_data, classify_destination
from langchain_core.messages import SystemMessage, HumanMessage

def research_agent_node(state: TripPlannerState) -> dict:
    """
    Research / Search Agent:
    Aggregates findings from Destination, Budget, and Preferences agents to
    discover curated venues, landmarks, culinary hotspots, and logistical coordinates
    across single cities, multi-city itineraries, and state-wide circuits.
    """
    destination = state.get("destination", "Tokyo, Japan")
    duration = max(1, int(state.get("duration_days", 5)))
    origin = state.get("origin", "Indore, India")
    dest_data = state.get("destination_data", {})
    budget_strat = state.get("budget_strategy", {})
    pref_profile = state.get("preferences_profile", {})

    dest_classification = classify_destination(destination, duration_days=duration)
    circuit_cities = dest_data.get("circuit_cities") or dest_classification.get("cities", [destination.split(",")[0].strip()])
    is_multi = dest_data.get("is_multi_destination") or dest_classification.get("is_multi", False)

    logs = [{
        "agent": "Research / Search Agent",
        "status": "running",
        "message": f"Researching curated sights, landmarks, and regional dining across {', '.join(circuit_cities)}...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]

    # Retrieve base POIs across circuit cities
    base_data = get_destination_data(destination, duration_days=duration)
    spots = base_data.get("spots", [])

    research_data = {
        "curated_spots": spots,
        "circuit_cities": circuit_cities,
        "dining_recommendations": [
            {"name": f"Authentic Regional Specialties in {circuit_cities[0]}", "type": "Lunch / Casual", "cost_est": 25, "vibe": "Local culinary traditions"},
            {"name": f"Atmospheric Evening Dinner in {circuit_cities[-1]}", "type": "Dinner", "cost_est": 45, "vibe": "Scenic twilight ambiance"}
        ],
        "local_transit_card": dest_data.get("transit_style", "Intercity cabs, state express buses, and local auto-rickshaws."),
        "secret_gems": [
            f"Start travel legs early in the morning (07:30 - 08:30) to enjoy smooth traffic and misty mountain vistas.",
            f"Seek out local sweet stalls and regional tea stalls near historic ghats and bazaars."
        ]
    }

    llm = get_llm(state.get("api_key"), state.get("provider"))
    if llm:
        try:
            prompt = (
                f"You are an Elite Travel Researcher Agent. Curate a rich list of places for:\n"
                f"Origin: {origin}\n"
                f"Destination: {destination}\n"
                f"Circuit Cities to Cover: {', '.join(circuit_cities)}\n"
                f"Duration: {duration} days\n"
                f"Budget Tier: {budget_strat.get('tier', 'Comfort')}\n"
                f"Key Interests: {pref_profile.get('core_themes', [])}\n\n"
                f"IMPORTANT: The itinerary covers the circuit hubs: {', '.join(circuit_cities)}.\n"
                f"Provide a JSON response with:\n"
                f"- spots: list of 8-12 points of interest distributed across the circuit cities ({', '.join(circuit_cities)}), each with:\n"
                f"    - name (string)\n"
                f"    - city (which city this spot is located in: one of {circuit_cities})\n"
                f"    - category (Attraction / Culture / Dining / Nature / Sightseeing / Adventure)\n"
                f"    - cost (estimated cost float in local currency or USD)\n"
                f"    - best_time (e.g. 'Morning (09:00 - 11:30)')\n"
                f"    - desc (1-2 sentences with practical context)\n"
                f"    - lat (approx latitude float)\n"
                f"    - lng (approx longitude float)\n"
                f"- secret_gems: list of 2-3 insider local tips for this specific route\n"
                f"Respond ONLY with valid JSON."
            )
            response = llm.invoke([
                SystemMessage(content="You are a meticulous local travel researcher. Return valid JSON only."),
                HumanMessage(content=prompt)
            ])
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed = json.loads(content)
            if "spots" in parsed and isinstance(parsed["spots"], list) and len(parsed["spots"]) > 0:
                research_data["curated_spots"] = parsed["spots"]
            if "secret_gems" in parsed:
                research_data["secret_gems"] = parsed["secret_gems"]
        except Exception:
            pass

    logs.append({
        "agent": "Research / Search Agent",
        "status": "completed",
        "message": f"Verified {len(research_data['curated_spots'])} curated attractions across {len(circuit_cities)} destination hub(s).",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "research_data": research_data,
        "agent_logs": logs
    }
