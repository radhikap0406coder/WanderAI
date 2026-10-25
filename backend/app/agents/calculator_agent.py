from datetime import datetime
from typing import Dict, Any, Tuple
from app.agents.state import TripPlannerState

INDIAN_CITIES = {
    "indore", "jaipur", "delhi", "new delhi", "mumbai", "bangalore", "bengaluru",
    "kolkata", "chennai", "hyderabad", "pune", "ahmedabad", "goa", "kerala",
    "varanasi", "agra", "udaipur", "jodhpur", "amritsar", "rishikesh", "manali",
    "shimla", "kochi", "surat", "lucknow", "bhopal", "patna", "vadodara", "nagpur",
    "chandigarh", "ujjain", "gwalior", "jabalpur", "mysore", "ooty", "pondicherry",
    "leh", "ladakh", "darjeeling", "gangtok", "munnar", "hampi", "alleppey",
    "uttarakhand", "dehradun", "haridwar", "mussoorie", "nainital", "kullu", "kasol",
    "dharamshala", "himachal", "himachal pradesh", "rajasthan", "kashmir", "sikkim",
    "meghalaya", "karnataka", "tamil nadu", "maharashtra", "gujarat", "uttar pradesh"
}

SE_ASIA_ME_LOCATIONS = {
    "bali", "indonesia", "thailand", "bangkok", "phuket", "krabi", "chiang mai", "pattaya",
    "singapore", "malaysia", "kuala lumpur", "penang", "langkawi", "vietnam", "hanoi",
    "da nang", "ho chi minh", "hoi an", "dubai", "uae", "united arab emirates", "abu dhabi", "sharjah",
    "sri lanka", "colombo", "kandy", "nepal", "kathmandu", "pokhara", "maldives", "male",
    "qatar", "doha", "oman", "muscat", "cambodia", "siem reap", "phnom penh", "philippines", "manila", "cebu"
}

USD_EXCHANGE_RATES = {
    "USD": 1.0,
    "INR": 85.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 150.0,
    "CAD": 1.38,
    "AUD": 1.52
}

def is_india_location(text: str) -> bool:
    """Checks if a location string points to an Indian destination or origin."""
    if not text:
        return False
    t = text.lower().strip()
    if "india" in t or "bharat" in t:
        return True
    return any(c in t for c in INDIAN_CITIES)

def is_se_asia_me_location(text: str) -> bool:
    """Checks if a location string points to Southeast Asia, South Asia, or Middle East."""
    if not text:
        return False
    t = text.lower().strip()
    return any(loc in t for loc in SE_ASIA_ME_LOCATIONS)

def convert_currency(amount_usd: float, target_currency: str) -> float:
    """Converts a USD benchmark amount into target currency."""
    rate = USD_EXCHANGE_RATES.get(target_currency.upper(), 1.0)
    return round(amount_usd * rate, 2)

def estimate_intercity_transport(
    origin: str,
    destination: str,
    travelers: int,
    currency: str,
    accommodation_style: str,
    group_budget: float
) -> Tuple[float, str, str]:
    """
    Calculates realistic round-trip transportation between origin and destination
    for all travelers, taking into account distance, geography, and budget tier.
    Returns (total_transport, mode_name, description).
    """
    orig_clean = origin.lower().strip()
    dest_clean = destination.lower().strip()
    
    # 1. Same city departure
    orig_city = orig_clean.split(",")[0].strip()
    dest_city = dest_clean.split(",")[0].strip()
    if orig_city and dest_city and (orig_city == dest_city or orig_city in dest_clean or dest_city in orig_clean):
        return (0.0, "Local Departure (Same City)", "Origin and destination are in the same city. No intercity transit required.")

    is_orig_india = is_india_location(origin)
    is_dest_india = is_india_location(destination) or (
        currency == "INR" and not is_se_asia_me_location(destination) and not any(k in dest_clean for k in ["usa", "japan", "france", "uk", "italy", "bali", "singapore", "dubai", "thailand"])
    )

    # 2. Domestic India Route (e.g. Indore -> Jaipur, Indore -> Uttarakhand, Delhi -> Goa)
    if is_orig_india and is_dest_india:
        budget_per_person = group_budget / max(travelers, 1)
        is_luxury = "luxury" in accommodation_style.lower()
        is_comfort = "comfort" in accommodation_style.lower() or "boutique" in accommodation_style.lower()

        if is_luxury and budget_per_person >= 14000:
            mode_name = "Domestic Flight (Round-Trip)"
            round_trip_pp = 7500.0  # ₹7,500 round-trip per person
        elif (is_comfort or budget_per_person >= 7500) and not ("budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower()):
            mode_name = "Express Train (3AC/2AC) / AC Volvo Bus (Round-Trip)"
            round_trip_pp = 2200.0  # ₹2,200 round-trip per person
        else:
            mode_name = "Express Train (Sleeper) / Deluxe Semi-Sleeper Bus (Round-Trip)"
            round_trip_pp = 1500.0  # ₹1,500 round-trip per person

        if currency != "INR":
            round_trip_pp = (round_trip_pp / 85.0) * USD_EXCHANGE_RATES.get(currency, 1.0)

        round_trip_pp = round(round_trip_pp, 2)
        total_transport = round(round_trip_pp * travelers, 2)
        desc = (
            f"Estimated round-trip fare (~{currency} {round_trip_pp:,.0f}/person) for {travelers} traveler(s). "
            f"Live train/flight fares vary based on booking date and seat availability."
        )
        return (total_transport, f"{mode_name} (Estimated)", desc)

    # 3. India to Southeast Asia / Middle East / South Asia (e.g. India to Bali, Thailand, Dubai, Singapore)
    is_se_asia_route = (
        (is_orig_india and is_se_asia_me_location(destination))
        or (is_se_asia_me_location(origin) and is_dest_india)
        or (is_se_asia_me_location(destination) and currency == "INR")
    )
    if is_se_asia_route:
        if "luxury" in accommodation_style.lower():
            usd_flight_pp = 520.0  # ~₹44,200 round-trip full-service / premium airline
        elif "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
            usd_flight_pp = 320.0  # ~₹27,200 round-trip low-cost carrier (AirAsia / Scoot / VietJet)
        else:
            usd_flight_pp = 380.0  # ~₹32,300 round-trip standard economy (IndiGo / Batik / Singapore Air)

        flight_pp = convert_currency(usd_flight_pp, currency)
        total_transport = round(flight_pp * travelers, 2)
        desc = (
            f"Estimated round-trip economy airfare (~{currency} {flight_pp:,.0f}/person) for {travelers} traveler(s). "
            f"Actual airfare depends on travel dates, airline, and booking lead time."
        )
        return (
            total_transport,
            "International Economy Flights (Estimated)",
            desc
        )

    # 4. Long-Haul International Flights (e.g. India to USA/Europe, USA to Japan, Europe to Bali)
    is_international = (
        (is_orig_india != is_dest_india)
        or is_se_asia_me_location(destination)
        or any(k in (orig_clean + dest_clean) for k in [
            "tokyo", "paris", "rome", "bali", "london", "new york", "los angeles", "sydney", "toronto", "berlin", "barcelona"
        ])
    )
    if is_international:
        if "luxury" in accommodation_style.lower():
            usd_flight_pp = 1500.0
        elif "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
            usd_flight_pp = 750.0
        else:
            usd_flight_pp = 950.0

        flight_pp = convert_currency(usd_flight_pp, currency)
        total_transport = round(flight_pp * travelers, 2)
        desc = (
            f"Estimated long-haul international round-trip airfare (~{currency} {flight_pp:,.0f}/person) for {travelers} traveler(s). "
            f"Live flight prices fluctuate with seasonal demand, airlines, and booking lead time."
        )
        return (
            total_transport,
            "Long-Haul International Flights (Estimated)",
            desc
        )

    # 5. Domestic routes outside India (e.g. NYC to Miami, Paris to Nice)
    usd_fare_pp = 250.0
    if "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
        usd_fare_pp = 130.0
    elif "luxury" in accommodation_style.lower():
        usd_fare_pp = 500.0

    fare_pp = convert_currency(usd_fare_pp, currency)
    total_transport = round(fare_pp * travelers, 2)
    desc = f"Estimated domestic round-trip transit (~{currency} {fare_pp:,.0f}/person) between {origin} and {destination}."
    return (
        total_transport,
        "Domestic Transit / Flight (Estimated)",
        desc
    )

def calculator_agent_node(state: TripPlannerState) -> TripPlannerState:
    """
    Budget Calculator Agent:
    Itemizes realistic, currency-accurate expenses across intercity transportation,
    lodging, dining, local transit, regional transfers, experiences, and emergency buffer.
    Guarantees strict mathematical consistency:
    - total estimated cost = sum of categories
    - cost per person = total estimated cost ÷ travelers
    - cost per person per day = cost per person ÷ duration
    - variance = total group budget - total estimated cost
    - shortfall and remaining budget are non-negative
    """
    raw_budget = float(state.get("budget_total", 30000.0))
    currency = (state.get("currency") or "INR").upper()
    duration = max(1, int(state.get("duration_days", 5)))
    travelers = max(1, int(state.get("travelers_count", 2)))
    traveler_type = state.get("traveler_type", "Couple")
    accommodation_style = state.get("accommodation_type", "Comfort Hotel (3-Star)")
    origin = state.get("origin", "Indore, India")
    destination = state.get("destination", "Jaipur, India")
    itinerary = state.get("itinerary_draft", [])
    
    # CRITICAL BUDGET RULE:
    # The budget entered by the user is the total budget for the ENTIRE group,
    # unless explicitly flagged as per-person.
    is_per_person = bool(state.get("is_per_person_budget", False))
    if is_per_person:
        budget_total = round(raw_budget * travelers, 2)
    else:
        budget_total = round(raw_budget, 2)

    dest_is_india = is_india_location(destination) or (
        currency == "INR" and not is_se_asia_me_location(destination) and not any(
            k in destination.lower() for k in ["usa", "japan", "france", "uk", "italy", "bali", "singapore", "dubai", "thailand"]
        )
    )
    dest_is_se_asia = is_se_asia_me_location(destination)

    logs = [{
        "agent": "Budget Calculator",
        "status": "running",
        "message": f"Calculating realistic group travel expenses for {travelers} traveler(s) over {duration} days against {currency} {budget_total:,.2f} total group budget...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]

    # -------------------------------------------------------------
    # 1. Round-Trip Intercity Transportation (Origin <-> Destination)
    # -------------------------------------------------------------
    transport_total, transport_mode, transport_desc = estimate_intercity_transport(
        origin=origin,
        destination=destination,
        travelers=travelers,
        currency=currency,
        accommodation_style=accommodation_style,
        group_budget=budget_total
    )

    # -------------------------------------------------------------
    # 2. Accommodation Estimation (Room-Nights Calculation)
    # -------------------------------------------------------------
    if "solo" in traveler_type.lower():
        rooms = 1
    elif "couple" in traveler_type.lower():
        rooms = 1
    elif "family" in traveler_type.lower():
        rooms = 1 if travelers <= 3 else max(1, (travelers + 1) // 2)
    else:  # Friends or Group
        rooms = max(1, (travelers + 1) // 2)

    nights = max(1, duration - 1)

    if dest_is_india:
        indian_rates = {
            "Budget / Hostel": 1200.0,
            "Hostel": 1000.0,
            "Budget Hotel": 1800.0,
            "Comfort Hotel (3-Star)": 3200.0,
            "Boutique / 4-Star": 5500.0,
            "Luxury 5-Star": 14000.0,
            "Luxury Resort (5-Star)": 15500.0,
            "Vacation Rental": 4500.0
        }
        base_nightly = 3200.0
        for k, v in indian_rates.items():
            if k.lower() in accommodation_style.lower():
                base_nightly = v
                break
        
        if currency != "INR":
            base_nightly = (base_nightly / 85.0) * USD_EXCHANGE_RATES.get(currency, 1.0)
    elif dest_is_se_asia:
        se_asia_rates = {
            "Budget / Hostel": 25.0,
            "Hostel": 20.0,
            "Budget Hotel": 40.0,
            "Comfort Hotel (3-Star)": 55.0,
            "Boutique / 4-Star": 75.0,
            "Luxury 5-Star": 190.0,
            "Luxury Resort (5-Star)": 220.0,
            "Vacation Rental": 90.0
        }
        base_nightly_usd = 75.0
        for k, v in se_asia_rates.items():
            if k.lower() in accommodation_style.lower():
                base_nightly_usd = v
                break
        base_nightly = convert_currency(base_nightly_usd, currency)
    else:
        usd_rates = {
            "Budget / Hostel": 45.0,
            "Hostel": 40.0,
            "Budget Hotel": 85.0,
            "Comfort Hotel (3-Star)": 140.0,
            "Boutique / 4-Star": 220.0,
            "Luxury 5-Star": 520.0,
            "Luxury Resort (5-Star)": 600.0,
            "Vacation Rental": 190.0
        }
        base_nightly_usd = 140.0
        for k, v in usd_rates.items():
            if k.lower() in accommodation_style.lower():
                base_nightly_usd = v
                break
        base_nightly = convert_currency(base_nightly_usd, currency)

    base_nightly = round(base_nightly, 2)
    total_accommodation = round(base_nightly * nights * rooms, 2)

    # -------------------------------------------------------------
    # 3. Dining & Gastronomy Estimation
    # -------------------------------------------------------------
    if dest_is_india:
        if "luxury" in accommodation_style.lower():
            daily_food_pp = 2800.0
        elif "boutique" in accommodation_style.lower() or "4-star" in accommodation_style.lower():
            daily_food_pp = 1600.0
        elif "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
            daily_food_pp = 500.0
        else:  # Comfort 3-Star
            daily_food_pp = 950.0

        if currency != "INR":
            daily_food_pp = (daily_food_pp / 85.0) * USD_EXCHANGE_RATES.get(currency, 1.0)
    elif dest_is_se_asia:
        if "luxury" in accommodation_style.lower():
            daily_food_pp_usd = 75.0
        elif "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
            daily_food_pp_usd = 15.0
        elif "boutique" in accommodation_style.lower():
            daily_food_pp_usd = 30.0
        else:
            daily_food_pp_usd = 22.0
        daily_food_pp = convert_currency(daily_food_pp_usd, currency)
    else:
        if "luxury" in accommodation_style.lower():
            daily_food_pp_usd = 180.0
        elif "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
            daily_food_pp_usd = 35.0
        elif "boutique" in accommodation_style.lower():
            daily_food_pp_usd = 110.0
        else:
            daily_food_pp_usd = 70.0
        daily_food_pp = convert_currency(daily_food_pp_usd, currency)

    daily_food_pp = round(daily_food_pp, 2)
    total_dining = round(daily_food_pp * duration * travelers, 2)

    # -------------------------------------------------------------
    # 4. Local City & Intercity Regional Transportation
    # -------------------------------------------------------------
    if dest_is_india:
        daily_transit_pp = 220.0
        if "luxury" in accommodation_style.lower():
            daily_transit_pp = 650.0
        elif "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
            daily_transit_pp = 150.0

        if currency != "INR":
            daily_transit_pp = (daily_transit_pp / 85.0) * USD_EXCHANGE_RATES.get(currency, 1.0)
    elif dest_is_se_asia:
        daily_transit_pp_usd = 10.0
        if "luxury" in accommodation_style.lower():
            daily_transit_pp_usd = 25.0
        elif "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
            daily_transit_pp_usd = 6.0
        daily_transit_pp = convert_currency(daily_transit_pp_usd, currency)
    else:
        daily_transit_pp_usd = 18.0
        if "luxury" in accommodation_style.lower():
            daily_transit_pp_usd = 45.0
        elif "budget" in accommodation_style.lower() or "hostel" in accommodation_style.lower():
            daily_transit_pp_usd = 10.0
        daily_transit_pp = convert_currency(daily_transit_pp_usd, currency)

    daily_transit_pp = round(daily_transit_pp, 2)
    total_local_transit = round(daily_transit_pp * duration * travelers, 2)

    # Detect intercity transfers across circuit cities
    unique_cities = []
    for day in itinerary:
        c = day.get("current_city")
        if c and c not in unique_cities:
            unique_cities.append(c)

    intercity_legs = max(0, len(unique_cities) - 1)
    if intercity_legs > 0:
        # Group intercity transfer cost (per vehicle leg for all travelers)
        if dest_is_india or currency == "INR":
            leg_transfer_cost = 1400.0  # Shared cab / private taxi / state bus transfer for the group
            if currency != "INR":
                leg_transfer_cost = (leg_transfer_cost / 85.0) * USD_EXCHANGE_RATES.get(currency, 1.0)
        else:
            leg_transfer_cost = convert_currency(25.0, currency)
        intercity_transfer_total = round(intercity_legs * leg_transfer_cost, 2)
        total_transit = round(total_local_transit + intercity_transfer_total, 2)
        transit_desc = f"Local city transit + {intercity_legs} intercity regional transfer(s) across {', '.join(unique_cities)} for {travelers} traveler(s)"
    else:
        total_transit = total_local_transit
        transit_desc = f"City transit, cabs, auto-rickshaws & metro across {duration} days"

    # -------------------------------------------------------------
    # 5. Sightseeing & Activities (Monument Entries & Tours)
    # -------------------------------------------------------------
    itinerary_act_cost = 0.0
    for day in itinerary:
        for act in day.get("activities", []):
            if act.get("category") != "Dining":
                itinerary_act_cost += float(act.get("estimated_cost", 0.0))

    if itinerary_act_cost > 0:
        total_activities = round(itinerary_act_cost * travelers, 2)
    else:
        if dest_is_india:
            act_pp_total = 600.0
            if currency != "INR":
                act_pp_total = (act_pp_total / 85.0) * USD_EXCHANGE_RATES.get(currency, 1.0)
        elif dest_is_se_asia:
            act_pp_total = convert_currency(25.0, currency)
        else:
            act_pp_total = convert_currency(160.0, currency)
        total_activities = round(act_pp_total * travelers, 2)

    # -------------------------------------------------------------
    # 6. Miscellaneous & Contingency Buffer (Emergency / Tips / Shopping)
    # -------------------------------------------------------------
    subtotal_core = round(transport_total + total_accommodation + total_dining + total_transit + total_activities, 2)
    min_buffer = 1200.0 if currency == "INR" else convert_currency(20.0, currency)
    total_buffer = round(max(subtotal_core * 0.05, min_buffer), 2)

    # -------------------------------------------------------------
    # 7. Total Estimated Group Cost & Strict Mathematical Consistency
    # -------------------------------------------------------------
    total_estimated = round(
        transport_total + total_accommodation + total_dining + total_transit + total_activities + total_buffer,
        2
    )

    per_person_total = round(total_estimated / travelers, 2)
    per_person_day = round(per_person_total / duration, 2)

    variance = round(budget_total - total_estimated, 2)
    shortfall = max(0.0, round(total_estimated - budget_total, 2))
    remaining_budget = max(0.0, round(budget_total - total_estimated, 2))
    status = "Within Budget" if variance >= 0 else "Budget Shortfall"

    # -------------------------------------------------------------
    # 8. Category Breakdown Dict
    # -------------------------------------------------------------
    categories = {
        "transportation": {
            "name": "Round-Trip Intercity Transportation",
            "allocated_amount": transport_total,
            "percentage": round((transport_total / total_estimated) * 100, 1) if total_estimated > 0 else 0.0,
            "description": f"{transport_mode}: {origin} ⇄ {destination} for {travelers} traveler(s)"
        },
        "accommodation": {
            "name": "Lodging & Accommodations",
            "allocated_amount": total_accommodation,
            "percentage": round((total_accommodation / total_estimated) * 100, 1) if total_estimated > 0 else 0.0,
            "description": f"{rooms} room(s) for {nights} night(s) ({accommodation_style})"
        },
        "dining": {
            "name": "Dining & Gastronomy",
            "allocated_amount": total_dining,
            "percentage": round((total_dining / total_estimated) * 100, 1) if total_estimated > 0 else 0.0,
            "description": f"All meals & local specialties for {travelers} traveler(s) over {duration} days"
        },
        "local_transit": {
            "name": "Local & Regional Transportation",
            "allocated_amount": total_transit,
            "percentage": round((total_transit / total_estimated) * 100, 1) if total_estimated > 0 else 0.0,
            "description": transit_desc
        },
        "activities": {
            "name": "Attractions & Experiences",
            "allocated_amount": total_activities,
            "percentage": round((total_activities / total_estimated) * 100, 1) if total_estimated > 0 else 0.0,
            "description": f"Admission tickets, landmark entries & sightseeing for {travelers} traveler(s)"
        },
        "contingency": {
            "name": "Emergency Contingency Buffer",
            "allocated_amount": total_buffer,
            "percentage": round((total_buffer / total_estimated) * 100, 1) if total_estimated > 0 else 0.0,
            "description": "5% cushion for spontaneous treats, tips, shopping & emergencies"
        }
    }

    # -------------------------------------------------------------
    # 9. Realistic Saving Tips & Practical Trade-offs
    # -------------------------------------------------------------
    dest_name_short = destination.split(",")[0].strip()
    dest_lower = destination.lower()
    if shortfall > 0:
        if "uttarakhand" in dest_lower or (len(unique_cities) > 1 and dest_is_india):
            saving_tips = [
                f"Regional Transit Optimization: Use Uttarakhand Transport Corporation (UTC) express buses or shared Sumos between Haridwar, Rishikesh, and Dehradun to save up to 60% compared to private taxis.",
                f"Lodging Trade-Off: Opt for verified ashram guesthouses, dharamsalas, or family rooms in Haridwar and Rishikesh instead of 3/4-star hotels to save ₹1,000–₹2,000 per night.",
                f"Authentic Local Dining: Mix seated restaurants with famous local sweet hubs and pure vegetarian thali stalls (e.g. Mohan Ji Poori Wale in Haridwar, Chotiwala in Rishikesh).",
                f"Trip Duration: Shortening the circuit from {duration} days to {max(2, duration - 1)} or {max(2, duration - 2)} days easily bridges the {currency} {shortfall:,.0f} gap without sacrificing key highlights."
            ]
        elif dest_is_se_asia:
            saving_tips = [
                f"Flight Timing: Book round-trip flights 6–8 weeks early or set fare alerts on budget carriers (e.g. AirAsia, Scoot, VietJet) to save up to 25% on airfare.",
                f"Villa / Suite Sharing: For {travelers} travelers, booking a shared multi-bedroom private villa in {dest_name_short} is often 30–40% cheaper per person than multiple hotel rooms.",
                f"Local Warungs & Cafes: Mix international dining with authentic local warungs and beachside cafes to enjoy classic dishes for under {currency} {convert_currency(4.0, currency):,.0f} per meal.",
                f"Trip Duration: Adjusting the journey from {duration} days to {max(2, duration - 1)} days comfortably trims {currency} {shortfall:,.0f} from the overall group spend."
            ]
        elif dest_is_india:
            saving_tips = [
                f"Transportation Trade-Off: Opt for 3AC / Sleeper class trains or semi-sleeper AC buses to save substantially compared to flights.",
                f"Lodging Optimization: Book verified budget heritage havelis, guest houses, or family suites instead of 4-star properties to save up to 35% on room rates.",
                f"Authentic Local Dining: Savor regional thalis and street food hubs for authentic culinary delights at a fraction of hotel dining rates.",
                f"Adjust Duration: Shortening the trip from {duration} days to {max(2, duration - 1)} days easily bridges the {currency} {shortfall:,.0f} gap without sacrificing quality."
            ]
        else:
            saving_tips = [
                f"Flight Alerts: Monitor economy flight deals and book during mid-week windows to trim international airfare expenses.",
                f"Central Transit Passes: Use city multi-day transit passes (metro/bus) rather than metered cabs or ride-shares.",
                f"Lunch Specials: Enjoy fine dining at lunch set-menu prices and casual bistro dinners to reduce food expenses by 30%.",
                f"Adjust Duration: Shortening the trip from {duration} days to {max(2, duration - 1)} days comfortably closes the {currency} {shortfall:,.0f} shortfall."
            ]
    else:
        saving_tips = [
            "Book key monument and exhibition tickets online in advance to bypass queues and surge ticketing fees.",
            "Hire authorized registered local docent guides at landmark forts for deep cultural storytelling.",
            "Take advantage of lunch set menus or thalis at heritage restaurants for fine dining at lower rates."
        ]

    upgrades = [
        "Reserve a sunset rooftop dinner table overlooking illuminated palace fortresses.",
        "Indulge in an experiential cultural village dinner or heritage puppet dinner show.",
        "Upgrade to a boutique heritage haveli room with traditional courtyard architecture."
    ]

    breakdown_result = {
        "total_budget": budget_total,
        "estimated_total_cost": total_estimated,
        "currency": currency,
        "variance": variance,
        "status": status,
        "shortfall": shortfall,
        "remaining_budget": remaining_budget,
        "per_person": per_person_total,
        "per_person_per_day": per_person_day,
        "travelers_count": travelers,
        "duration_days": duration,
        "rooms_count": rooms,
        "nights_count": nights,
        "transport_mode": transport_mode,
        "categories": categories,
        "saving_tips": saving_tips,
        "luxury_upgrades": upgrades
    }

    logs.append({
        "agent": "Budget Calculator",
        "status": "completed",
        "message": f"Calculated realistic total estimate of {currency} {total_estimated:,.2f} ({status}, {currency} {abs(variance):,.2f} {'shortfall' if variance < 0 else 'surplus'}).",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "budget_breakdown": breakdown_result,
        "agent_logs": logs
    }
