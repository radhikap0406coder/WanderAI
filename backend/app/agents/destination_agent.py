import json
from datetime import datetime
from app.agents.state import TripPlannerState
from app.agents.llm_factory import get_llm
from app.data.destination_knowledge import get_destination_data, classify_destination
from langchain_core.messages import SystemMessage, HumanMessage

def destination_agent_node(state: TripPlannerState) -> dict:
    """
    Destination Agent:
    Evaluates target location, whether it's a single city, multi-city route, or state/region,
    determines the logical circuit of destinations, climate, cultural customs, and transit style.
    """
    destination = state.get("destination", "Tokyo, Japan")
    duration = max(1, int(state.get("duration_days", 5)))
    origin = state.get("origin", "Indore, India")
    
    # Classify destination type (single city, state/region, multi-city)
    dest_classification = classify_destination(destination, duration_days=duration)
    base_data = get_destination_data(destination, duration_days=duration)

    circuit_cities = base_data.get("circuit_cities") or dest_classification.get("cities", [destination.split(",")[0].strip()])
    is_multi = base_data.get("is_multi_destination") or dest_classification.get("is_multi", False)
    dest_type = base_data.get("destination_type") or dest_classification.get("type", "SINGLE_CITY")

    logs = [{
        "agent": "Destination Agent",
        "status": "running",
        "message": f"Analyzing {dest_type.replace('_', ' ').lower()} destination '{destination}' (Circuit hubs: {', '.join(circuit_cities)})...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]

    destination_result = {
        "destination_name": base_data.get("name", destination),
        "destination_type": dest_type,
        "circuit_cities": circuit_cities,
        "is_multi_destination": is_multi,
        "country": base_data.get("country", "International"),
        "coordinates": base_data.get("coordinates", [30.0668, 78.3000] if is_multi else [35.6762, 139.6503]),
        "tagline": base_data.get("tagline", f"Experience the magic of {destination}"),
        "climate_overview": base_data.get("climate", "Pleasant seasonal conditions with comfortable sightseeing temps."),
        "cultural_guidelines": base_data.get("customs", [
            "Greet locals with respect and learn simple greetings.",
            "Always keep identification and emergency contacts accessible."
        ]),
        "emergency_contacts": base_data.get("emergency", {"emergency": "112 / 911"}),
        "prime_areas": base_data.get("prime_areas", circuit_cities),
        "transit_style": base_data.get("transit_style", "Local transit and official taxis.")
    }

    llm = get_llm(state.get("api_key"), state.get("provider"))
    if llm:
        try:
            prompt = (
                f"You are a Destination Specialist Travel Agent. Analyze this destination for a traveler:\n"
                f"Starting Departure: {origin}\n"
                f"Destination: {destination}\n"
                f"Destination Type: {dest_type}\n"
                f"Planned Circuit Hubs: {', '.join(circuit_cities)}\n"
                f"Duration: {duration} days\n"
                f"Traveler Profile: {state.get('traveler_type', 'Friends')}\n\n"
                f"If the destination is a state, province, or multi-city route, consider the entire region and circuit hubs ({', '.join(circuit_cities)}).\n"
                f"Provide a JSON response with keys:\n"
                f"- tagline (catchy, inspiring one-liner)\n"
                f"- climate_overview (seasonal weather insight)\n"
                f"- cultural_guidelines (list of 3-4 key etiquette rules)\n"
                f"- prime_areas (list of 3-5 primary hubs/areas: {circuit_cities})\n"
                f"- transit_style (best way to travel between these destinations)\n"
                f"Respond ONLY with valid JSON."
            )
            response = llm.invoke([
                SystemMessage(content="You are a seasoned world traveler and destination analysis agent. Output pure JSON only."),
                HumanMessage(content=prompt)
            ])
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed = json.loads(content)
            destination_result.update({k: v for k, v in parsed.items() if v})
            # Ensure critical classification fields are preserved
            destination_result["destination_type"] = dest_type
            destination_result["circuit_cities"] = circuit_cities
            destination_result["is_multi_destination"] = is_multi
        except Exception:
            pass

    logs.append({
        "agent": "Destination Agent",
        "status": "completed",
        "message": f"Successfully synthesized regional intelligence for {destination_result['destination_name']} ({len(circuit_cities)} hub{'s' if len(circuit_cities)>1 else ''}).",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "destination_data": destination_result,
        "agent_logs": logs
    }
