import json
from datetime import datetime
from app.agents.state import TripPlannerState
from app.agents.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def preferences_agent_node(state: TripPlannerState) -> dict:
    """
    Preferences Agent:
    Interprets user interests, travel cadence, traveler makeup (solo/couple/family),
    and custom notes into actionable itinerary curation guidelines.
    """
    interests = state.get("interests", ["Culture", "Dining", "Sightseeing"])
    pace = state.get("pace", "Balanced")
    traveler_type = state.get("traveler_type", "Couple")
    travelers_count = state.get("travelers_count", 2)
    notes = state.get("notes", "")

    logs = [{
        "agent": "Preferences Agent",
        "status": "running",
        "message": f"Tailoring experience profile for {traveler_type} travelers (Pace: {pace}, Interests: {', '.join(interests[:3])})...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]

    pace_descriptions = {
        "Relaxed": "1-2 primary sights per day with ample coffee pauses, scenic strolls, and zero morning rushes.",
        "Balanced": "2-3 well-spaced highlights daily, balancing marquee monuments with relaxed meals and wandering.",
        "Fast-Paced": "3-4 vibrant stops per day, early starts, optimized transit routes, and maximum coverage of iconic spots."
    }

    cohort_notes = {
        "Solo": "Includes lively cafes, social walking tours, safe transit, and reflective photo spots.",
        "Couple": "Features romantic sunset viewpoints, intimate dinner venues, and scenic leisurely walks.",
        "Family": "Selects kid-welcoming attractions, stroller-friendly paths, and regular refreshment breaks.",
        "Friends": "Emphasizes social food markets, interactive group activities, viewpoints, and evening nightlife."
    }

    pref_profile = {
        "pace_level": pace,
        "pace_guideline": pace_descriptions.get(pace, pace_descriptions["Balanced"]),
        "traveler_style": cohort_notes.get(traveler_type, f"Curated for {travelers_count} travelers."),
        "core_themes": interests if interests else ["Highlights", "Culture", "Local Dining"],
        "special_instructions": notes if notes else "Standard seamless travel curation."
    }

    llm = get_llm(state.get("api_key"), state.get("provider"))
    if llm:
        try:
            prompt = (
                f"You are a Luxury Travel Concierge & Personal Preferences Agent.\n"
                f"Traveler Type: {traveler_type} ({travelers_count} people)\n"
                f"Pace Preference: {pace}\n"
                f"Interests: {interests}\n"
                f"Special Notes: {notes}\n\n"
                f"Provide a JSON response with keys:\n"
                f"- pace_guideline (1 sentence on schedule rhythm)\n"
                f"- traveler_style (1 sentence tailored for this traveler composition)\n"
                f"- core_themes (list of refined thematic pillars)\n"
                f"Respond ONLY with valid JSON."
            )
            response = llm.invoke([
                SystemMessage(content="You are a personal travel stylist. Output pure JSON only."),
                HumanMessage(content=prompt)
            ])
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed = json.loads(content)
            pref_profile.update({k: v for k, v in parsed.items() if v})
        except Exception:
            pass

    logs.append({
        "agent": "Preferences Agent",
        "status": "completed",
        "message": f"Constructed personalized travel persona: {', '.join(pref_profile['core_themes'])}.",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "preferences_profile": pref_profile,
        "agent_logs": logs
    }
