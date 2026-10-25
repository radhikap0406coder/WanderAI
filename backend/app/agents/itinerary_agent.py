import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.agents.state import TripPlannerState
from app.agents.llm_factory import get_llm
from app.data.destination_knowledge import classify_destination
from langchain_core.messages import SystemMessage, HumanMessage

def distribute_days_across_cities(cities: List[str], duration: int) -> List[str]:
    """Distributes total days across selected circuit cities logically."""
    if not cities:
        return ["Destination"] * duration
    n_cities = len(cities)
    if n_cities == 1:
        return [cities[0]] * duration
    if duration <= n_cities:
        return cities[:duration]

    alloc = [1] * n_cities
    rem = duration - n_cities
    # Prioritize gateway/arrival city, primary cultural hub, and final scenic hub
    priority_order = [0, 1, n_cities - 1] + list(range(2, n_cities - 1))
    p_idx = 0
    while rem > 0:
        alloc[priority_order[p_idx % len(priority_order)]] += 1
        rem -= 1
        p_idx += 1

    day_cities = []
    for c_idx, c in enumerate(cities):
        day_cities.extend([c] * alloc[c_idx])
    return day_cities[:duration]

def itinerary_agent_node(state: TripPlannerState) -> TripPlannerState:
    """
    Itinerary Generator Agent:
    Transforms research insights and route architecture into a realistic,
    day-by-day structured itinerary. Supports single cities, statewide regional circuits,
    and user-specified multi-city routes. Distinguishes intercity travel from sightseeing,
    incorporates origin arrival and departure, and prevents destination clustering bugs.
    """
    duration = max(1, int(state.get("duration_days", 5)))
    destination = state.get("destination", "Tokyo, Japan")
    origin = state.get("origin", "Indore, India")
    travelers = max(1, int(state.get("travelers_count", 2)))
    traveler_type = state.get("traveler_type", "Friends")
    budget_total = float(state.get("budget_total", 30000.0))
    currency = (state.get("currency") or "INR").upper()
    start_date_str = state.get("start_date")
    pref = state.get("preferences_profile", {})
    pace = pref.get("pace_level", "Balanced")

    dest_data = state.get("destination_data", {})
    research = state.get("research_data", {})
    spots = research.get("curated_spots", [])

    dest_classification = classify_destination(destination, duration_days=duration)
    dest_type = dest_data.get("destination_type") or dest_classification.get("type", "SINGLE_CITY")
    circuit_cities = dest_data.get("circuit_cities") or dest_classification.get("cities", [destination.split(",")[0].strip()])
    is_multi = (dest_type in ("STATE_REGION", "MULTI_CITY")) and len(circuit_cities) > 1

    logs = [{
        "agent": "Itinerary Generator",
        "status": "running",
        "message": f"Synthesizing {duration}-day {dest_type.replace('_', ' ').lower()} route across {', '.join(circuit_cities)} starting from {origin}...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]

    # Base date calculations
    if start_date_str:
        try:
            curr_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except Exception:
            curr_date = datetime.now() + timedelta(days=14)
    else:
        curr_date = datetime.now() + timedelta(days=14)

    # 1. Distribute days across circuit hubs
    day_cities = distribute_days_across_cities(circuit_cities, duration)
    origin_city = origin.split(",")[0].strip()

    # 2. Heuristic Day Builder (Guarantees multi-city logic even without LLM)
    days = []
    city_spot_usage: Dict[str, int] = {c: 0 for c in circuit_cities}

    for d in range(1, duration + 1):
        day_date = curr_date + timedelta(days=d - 1)
        date_label = f"Day {d} · {day_date.strftime('%a, %b %d')}"
        current_city = day_cities[d - 1]
        prev_city = day_cities[d - 2] if d > 1 else None

        # Determine travel leg & overnight stay
        if d == 1:
            travel_leg = f"{origin_city} to {current_city} (Arrival)"
            overnight_stay = current_city
            transit_tips = f"Arrival into {current_city} from {origin}. Transfer to your stay, check in, and enjoy relaxed afternoon/evening sights."
        elif current_city != prev_city:
            travel_leg = f"{prev_city} to {current_city} (Intercity Travel)"
            overnight_stay = current_city
            transit_tips = f"Intercity travel from {prev_city} to {current_city} (approx. 1–2 hours by scenic cab or state bus). Settle into your {current_city} accommodation."
        elif d == duration:
            travel_leg = f"Depart {current_city} & Return to {origin_city}"
            overnight_stay = "Return Journey"
            transit_tips = f"Final morning exploration in {current_city}. Check out and transfer to railway station/airport for your return journey to {origin_city}."
        else:
            travel_leg = None
            overnight_stay = current_city
            transit_tips = f"Local transport (auto-rickshaws, cabs, or walking) between {current_city} attractions."

        # Filter spots for this specific city
        matching_spots = [s for s in spots if s.get("city", "").lower() == current_city.lower() or current_city.lower() in s.get("name", "").lower()]
        if not matching_spots:
            matching_spots = spots

        u_idx = city_spot_usage.get(current_city, 0)
        num_m = len(matching_spots)
        s1 = matching_spots[u_idx % max(num_m, 1)] if num_m > 0 else {
            "name": f"{current_city} Historic Center",
            "lat": 0.0, "lng": 0.0, "category": "Culture", "cost": 15, "desc": f"Explore iconic landmarks and morning atmosphere in {current_city}."
        }
        s2 = matching_spots[(u_idx + 1) % max(num_m, 1)] if num_m > 1 else {
            "name": f"{current_city} Scenic Promenade & Bazaar",
            "lat": 0.0, "lng": 0.0, "category": "Sightseeing", "cost": 10, "desc": f"Afternoon walks and regional crafts in {current_city}."
        }
        city_spot_usage[current_city] = u_idx + 2

        # Cost calculations
        raw_c1 = float(s1.get("cost", 15))
        raw_c2 = float(s2.get("cost", 20))
        if currency == "INR":
            c1 = raw_c1 if raw_c1 >= 30 else round(raw_c1 * 85, 2)
            c2 = raw_c2 if raw_c2 >= 30 else round(raw_c2 * 85, 2)
            c3 = 600.0
        else:
            c1 = raw_c1 if raw_c1 < 100 else round(raw_c1 / 85, 2)
            c2 = raw_c2 if raw_c2 < 100 else round(raw_c2 / 85, 2)
            c3 = 35.0

        act_morning = {
            "time_slot": "Morning",
            "time": "09:00 - 12:30",
            "title": f"Arrival & {s1.get('name', 'Morning Exploration')}" if d == 1 else s1.get("name", "Morning Exploration"),
            "description": f"Depart from {origin_city}, arrive in {current_city}, check in, and visit {s1.get('name')}." if d == 1 else s1.get("desc", f"Discover landmarks and culture in {current_city}."),
            "location": f"{s1.get('name')}, {current_city}",
            "coordinates": [float(s1.get("lat", 0.0)), float(s1.get("lng", 0.0))],
            "category": s1.get("category", "Culture"),
            "estimated_cost": c1,
            "tips": "Start early to make the most of your arrival day." if d == 1 else "Arrive early to beat peak visitor queues."
        }

        act_afternoon = {
            "time_slot": "Afternoon",
            "time": "13:30 - 17:00",
            "title": f"Scenic Transfer & {s2.get('name', 'Afternoon Highlight')}" if (travel_leg and d > 1 and d < duration) else s2.get("name", "Afternoon Highlight"),
            "description": f"Enjoy the scenic drive from {prev_city} to {current_city}, followed by {s2.get('name')}." if (travel_leg and d > 1 and d < duration) else s2.get("desc", f"Explore key sights and natural vistas in {current_city}."),
            "location": f"{s2.get('name')}, {current_city}",
            "coordinates": [float(s2.get("lat", 0.0)), float(s2.get("lng", 0.0))],
            "category": s2.get("category", "Sightseeing"),
            "estimated_cost": c2,
            "tips": "Relax with local refreshments during your intercity transit." if travel_leg else "Take a 30-minute cafe pause between sightseeing blocks."
        }

        act_evening = {
            "time_slot": "Evening",
            "time": "18:00 - 21:00",
            "title": f"Dinner & Twilight Ambience in {current_city}",
            "description": f"Savor authentic regional cuisine and evening atmosphere in {current_city}." if d < duration else f"Farewell regional dinner in {current_city} before return journey to {origin_city}.",
            "location": f"Central District, {current_city}",
            "coordinates": [float(s1.get("lat", 0.0)), float(s1.get("lng", 0.0))],
            "category": "Dining",
            "estimated_cost": c3,
            "tips": "Try local culinary specialties recommended by locals."
        }

        day_total = act_morning["estimated_cost"] + act_afternoon["estimated_cost"] + act_evening["estimated_cost"]

        # Creative theme title
        if is_multi:
            day_theme = f"{current_city}: {s1.get('name', 'Exploration').split('&')[0].strip()} & Local Highlights"
            if travel_leg and d > 1 and d < duration:
                day_theme = f"Transit to {current_city}: {s2.get('name', 'Sights').split('&')[0].strip()}"
            elif d == 1:
                day_theme = f"Arrival in {current_city}: Sacred Ghats & Heritage Welcome"
            elif d == duration:
                day_theme = f"Farewell {current_city} & Return Journey to {origin_city}"
        else:
            day_theme = f"{current_city} Immersion: {s1.get('name', 'Highlights').split(' ')[0]} & Culture"

        day_summary = (
            f"Journey from {origin_city} to {current_city}, check into accommodation, and begin exploration." if d == 1 else
            (f"Travel from {prev_city} to {current_city}, check into hotel, and explore afternoon highlights." if travel_leg and d < duration else
             (f"Conclude your memorable journey across {current_city} and commence return travel to {origin_city}." if d == duration else
              f"Full day immersed in the culture, natural beauty, and gastronomy of {current_city}."))
        )

        days.append({
            "day_number": d,
            "date_label": date_label,
            "current_city": current_city,
            "overnight_stay": overnight_stay,
            "travel_leg": travel_leg,
            "theme": day_theme,
            "summary": day_summary,
            "transit_tips": transit_tips,
            "activities": [act_morning, act_afternoon, act_evening],
            "day_total_cost": round(day_total, 2)
        })

    # 3. LLM Enhancement if available (Google Gemini)
    llm = get_llm(state.get("api_key"), state.get("provider"))
    llm_succeeded = False
    if llm:
        try:
            prompt = f"""You are WanderAI's Senior Travel Route Architect and Itinerary Planner.
Create a realistic, high-fidelity {duration}-day journey.

TRIP CONTEXT:
- Starting Location (Origin): {origin}
- Destination Input: {destination}
- Destination Classification: {dest_type}
- Selected Circuit Destinations/Cities: {', '.join(circuit_cities)}
- Duration: {duration} days ({max(1, duration - 1)} nights)
- Travelers: {travelers} ({traveler_type})
- Travel Pace: {pace}
- Group Budget: {currency} {budget_total:,.0f} (Combined total budget for all travelers)
- Core Themes: {', '.join(pref.get('core_themes', ['Culture', 'Sightseeing', 'Scenic Nature']))}

ROUTING & DESTINATION RULES:
1. DESTINATION TYPE & GEOGRAPHY:
   - State-level destinations (e.g. "Uttarakhand", "Himachal Pradesh", "Rajasthan"): This requires planning across suitable, distinct cities or tourist destinations along a logical circuit: {', '.join(circuit_cities)}.
   - Every itinerary day MUST identify a REAL, specific city or tourist destination in 'current_city' (e.g., 'Haridwar', 'Rishikesh', 'Dehradun', 'Mussoorie'). Do NOT set the state name as the city!
   - Every activity MUST specify real, verified attractions that genuinely belong to that specific city (e.g. Har Ki Pauri in Haridwar, Triveni Ghat in Rishikesh, Robber's Cave in Dehradun, Kempty Falls in Mussoorie). Never invent fictitious attractions like 'State Historic Old Town & Central Square'.
   - The number of destinations covered should depend realistically on the available days: 1-2 hubs for 3 days; 2-3 hubs for 4-5 days; 3-4 hubs for 6-10 days ({', '.join(circuit_cities)}).
   - SINGLE CITY destinations (e.g. "Jaipur", "Dehradun"): All days must be anchored in that single city without adding extraneous cities.

2. LOGISTICS, INTERCITY TRAVEL & RETURN JOURNEY:
   - Day 1: Account for arrival travel from {origin} to {circuit_cities[0]}. Include check-in and relaxed afternoon/evening sights in {circuit_cities[0]}. Set 'travel_leg' to '{origin_city} to {circuit_cities[0]} (Arrival)'.
   - Intercity Travel Days: When changing destinations between circuit hubs, explicitly allocate travel time in 'transit_tips' and set 'travel_leg' (e.g. 'Haridwar to Rishikesh (Intercity Travel, approx. 45 mins)'). Schedule activities in the new destination.
   - Non-transit Days: Set 'travel_leg' to null.
   - Final Day (Day {duration}): Account for morning exploration, check-out, and the return journey back to {origin}. Set 'travel_leg' to 'Depart {circuit_cities[-1]} & Return to {origin_city}'. Set 'overnight_stay' to 'Return Journey'.

3. SCHEMA REQUIREMENTS:
Return a JSON array of exactly {duration} day objects with this format:
[
  {{
    "day_number": 1,
    "current_city": "Real City Name (e.g. '{circuit_cities[0]}')",
    "overnight_stay": "City where staying the night (e.g. '{circuit_cities[0]}')",
    "travel_leg": "Origin to First City on Day 1, or City A to City B on transit days, or null if staying in same city",
    "theme": "Engaging title for the day",
    "summary": "1-2 sentence overview of the day's progression",
    "transit_tips": "Practical transit advice for the day including intercity travel mode and approximate duration",
    "activities": [
      {{
        "time_slot": "Morning",
        "time": "09:00 - 12:30",
        "title": "Specific attraction or activity",
        "description": "Engaging description with practical context",
        "location": "Place name with city (e.g. 'Har Ki Pauri, Haridwar')",
        "category": "Sightseeing / Culture / Dining / Nature / Adventure",
        "estimated_cost": 200.0,
        "tips": "Helpful insider tip"
      }},
      {{
        "time_slot": "Afternoon",
        "time": "13:30 - 17:00",
        "title": "...",
        "description": "...",
        "location": "...",
        "category": "...",
        "estimated_cost": 150.0,
        "tips": "..."
      }},
      {{
        "time_slot": "Evening",
        "time": "18:00 - 21:00",
        "title": "...",
        "description": "...",
        "location": "...",
        "category": "Dining",
        "estimated_cost": 500.0,
        "tips": "..."
      }}
    ]
  }}
]

Respond ONLY with valid JSON."""

            response = llm.invoke([
                SystemMessage(content="You are an expert itinerary builder. Output pure JSON list only."),
                HumanMessage(content=prompt)
            ])
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed = json.loads(content)

            if isinstance(parsed, list) and len(parsed) == duration:
                for i, p_day in enumerate(parsed):
                    if p_day.get("current_city"):
                        days[i]["current_city"] = p_day["current_city"]
                    if p_day.get("overnight_stay"):
                        days[i]["overnight_stay"] = p_day["overnight_stay"]
                    if "travel_leg" in p_day:
                        days[i]["travel_leg"] = p_day["travel_leg"]
                    if p_day.get("transit_tips"):
                        days[i]["transit_tips"] = p_day["transit_tips"]
                    if p_day.get("theme"):
                        days[i]["theme"] = p_day["theme"]
                    if p_day.get("summary"):
                        days[i]["summary"] = p_day["summary"]

                    if "activities" in p_day and isinstance(p_day["activities"], list) and len(p_day["activities"]) == 3:
                        for act_idx, act in enumerate(p_day["activities"]):
                            days[i]["activities"][act_idx]["title"] = act.get("title", days[i]["activities"][act_idx]["title"])
                            days[i]["activities"][act_idx]["description"] = act.get("description", days[i]["activities"][act_idx]["description"])
                            days[i]["activities"][act_idx]["location"] = act.get("location", days[i]["activities"][act_idx]["location"])
                            days[i]["activities"][act_idx]["category"] = act.get("category", days[i]["activities"][act_idx]["category"])
                            days[i]["activities"][act_idx]["time"] = act.get("time", days[i]["activities"][act_idx]["time"])
                            days[i]["activities"][act_idx]["estimated_cost"] = float(act.get("estimated_cost", days[i]["activities"][act_idx]["estimated_cost"]))
                            days[i]["activities"][act_idx]["tips"] = act.get("tips", days[i]["activities"][act_idx]["tips"])

                        days[i]["day_total_cost"] = round(sum(a["estimated_cost"] for a in days[i]["activities"]), 2)
                llm_succeeded = True
        except Exception as e:
            print(f"[Itinerary Agent Warning] Gemini itinerary generation failed ({e}). Using smart heuristic route.")

    if llm_succeeded:
        provider_used = "Google Gemini"
        is_fallback = False
        fallback_reason = None
    else:
        provider_used = "WanderAI Smart Engine (Offline Fallback)"
        is_fallback = True
        fallback_reason = "Gemini API unavailable or offline mode"

    logs.append({
        "agent": "Itinerary Generator",
        "status": "completed",
        "message": f"Successfully constructed {duration}-day route spanning {len(circuit_cities)} destination hub(s) with intercity logistics ({provider_used}).",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "itinerary_draft": days,
        "provider_used": provider_used,
        "is_fallback": is_fallback,
        "fallback_reason": fallback_reason,
        "agent_logs": logs
    }
