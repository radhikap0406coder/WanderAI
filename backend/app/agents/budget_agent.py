import json
from datetime import datetime
from app.agents.state import TripPlannerState
from app.agents.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

USD_EXCHANGE_RATES = {
    "USD": 1.0,
    "INR": 85.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 150.0,
    "CAD": 1.38,
    "AUD": 1.52
}

def budget_agent_node(state: TripPlannerState) -> dict:
    """
    Budget Agent:
    Calculates financial viability, daily allowances per person,
    optimal category allocations, and detects budget tier accurately in chosen currency.
    """
    raw_budget = float(state.get("budget_total", 2500.0))
    currency = (state.get("currency") or "USD").upper()
    duration = max(1, int(state.get("duration_days", 5)))
    travelers = max(1, int(state.get("travelers_count", 2)))
    accommodation_style = state.get("accommodation_type", "Boutique / 4-Star")
    is_per_person = bool(state.get("is_per_person_budget", False))

    if is_per_person:
        budget_total = round(raw_budget * travelers, 2)
    else:
        budget_total = round(raw_budget, 2)
    
    logs = [{
        "agent": "Budget Agent",
        "status": "running",
        "message": f"Formulating financial strategy for {currency} {budget_total:,.2f} total ({duration} days, {travelers} travelers)...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]

    daily_allowance = budget_total / duration
    per_person_per_day = daily_allowance / travelers

    # Determine Tier with currency-awareness
    if currency == "INR":
        if per_person_per_day < 900:
            tier = "Budget Backpacker"
            tier_desc = "Focused on value stays, delicious street food/casual eateries, and free public landmarks."
        elif per_person_per_day < 2800:
            tier = "Comfort Explorer"
            tier_desc = "Well-balanced trip with charming 3-star accommodations, seated bistros, and paid highlight attractions."
        elif per_person_per_day < 6500:
            tier = "Premium Boutique"
            tier_desc = "High comfort with boutique 4-star hotels, gourmet culinary tastings, guided tours, and comfortable transit."
        else:
            tier = "Ultra Luxury"
            tier_desc = "Premier 5-star luxury stays, royal heritage dining, private chauffeurs, and exclusive experiences."
    else:
        # Scale USD benchmark
        usd_rate = USD_EXCHANGE_RATES.get(currency, 1.0)
        equiv_usd_pp_day = per_person_per_day / usd_rate

        if equiv_usd_pp_day < 60:
            tier = "Budget Backpacker"
            tier_desc = "Focused on value stays, delicious street food/casual eateries, and free public landmarks."
        elif equiv_usd_pp_day < 180:
            tier = "Comfort Explorer"
            tier_desc = "Well-balanced trip with charming 3/4-star accommodations, seated bistros, and paid highlight attractions."
        elif equiv_usd_pp_day < 350:
            tier = "Premium Boutique"
            tier_desc = "High comfort with boutique 4-star hotels, gourmet culinary tastings, guided tours, and comfortable transit."
        else:
            tier = "Ultra Luxury"
            tier_desc = "Premier 5-star luxury stays, Michelin dining, private chauffeurs/VIP experiences, and premier lounges."

    allocations = {
        "transportation": {
            "percentage": 20.0,
            "target_amount": round(budget_total * 0.20, 2),
            "description": f"Round-trip intercity transit between origin and destination for {travelers} travelers."
        },
        "accommodation": {
            "percentage": 32.0,
            "target_amount": round(budget_total * 0.32, 2),
            "description": f"Lodging target for {accommodation_style} across {duration} days."
        },
        "dining": {
            "percentage": 25.0,
            "target_amount": round(budget_total * 0.25, 2),
            "description": f"Daily breakfasts, lunches, authentic dinners, and local cafe pauses for {travelers} people."
        },
        "activities": {
            "percentage": 10.0,
            "target_amount": round(budget_total * 0.10, 2),
            "description": "Museum tickets, landmark admissions, walking tours, and cultural shows."
        },
        "local_transit": {
            "percentage": 8.0,
            "target_amount": round(budget_total * 0.08, 2),
            "description": "Metro passes, regional transit, auto-rickshaws, and rideshares."
        },
        "contingency": {
            "percentage": 5.0,
            "target_amount": round(budget_total * 0.05, 2),
            "description": "Emergency buffer, spontaneous treats, tips, and souvenirs."
        }
    }

    strategy_result = {
        "budget_total": budget_total,
        "currency": currency,
        "daily_allowance": round(daily_allowance, 2),
        "per_person_per_day": round(per_person_per_day, 2),
        "tier": tier,
        "tier_description": tier_desc,
        "allocations": allocations
    }

    llm = get_llm(state.get("api_key"), state.get("provider"))
    if llm:
        try:
            prompt = (
                f"You are a Travel Financial Strategist. Review this trip budget:\n"
                f"Total Budget: {currency} {budget_total}\n"
                f"Days: {duration}\n"
                f"Travelers: {travelers}\n"
                f"Accommodation Preference: {accommodation_style}\n"
                f"Destination: {state.get('destination', 'Global')}\n\n"
                f"Provide a brief evaluation JSON with:\n"
                f"- tier (e.g. Budget, Comfort, Premium, Luxury)\n"
                f"- tier_description (1-2 sentences on what this enables)\n"
                f"Respond ONLY with valid JSON."
            )
            response = llm.invoke([
                SystemMessage(content="You are a travel budget consultant. Output pure JSON only."),
                HumanMessage(content=prompt)
            ])
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed = json.loads(content)
            if "tier" in parsed:
                strategy_result["tier"] = parsed["tier"]
            if "tier_description" in parsed:
                strategy_result["tier_description"] = parsed["tier_description"]
        except Exception:
            pass

    logs.append({
        "agent": "Budget Agent",
        "status": "completed",
        "message": f"Established '{strategy_result['tier']}' profile: {currency} {daily_allowance:,.0f}/day total allocation across {travelers} travelers.",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "budget_strategy": strategy_result,
        "agent_logs": logs
    }
