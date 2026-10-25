
import os
from typing import Optional, List, Dict, Any

from app.config import settings
from app.data.destination_knowledge import DESTINATIONS_DATA


SYSTEM_INSTRUCTION = """You are WanderAI's friendly, insightful, and knowledgeable AI Travel Assistant.
Your goal is to help travelers discover incredible destinations, optimize daily itineraries, discover hidden culinary gems, manage their travel budget, and travel like a local.

Tone & Style:
\- Warm, enthusiastic, and concise.
\- Provide concrete, actionable recommendations (specific neighborhood spots, must-try dishes, timing hacks, budget guidance).
\- Structure responses cleanly using Markdown (bold highlights, bullet points).
\- Keep answers engaging and concise (2-4 short paragraphs or bulleted recommendations).
\- If the traveler provides or asks about their active trip context, tailor your answers directly to that destination, duration, budget, and travel style.
"""


def generate_chat_reply(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    trip_context: Optional[Dict[str, Any]] = None,
    provider: Optional[str] = "auto",
    api_key_override: Optional[str] = None
) -> Dict[str, str]:
    """
    Generates a conversational response using Google Gemini,
    with a graceful fallback to the built-in destination intelligence engine.
    """
    history = history or []
    provider = (provider or "auto").lower()

    # Build context-rich prompt
    context_str = ""

    if trip_context:
        dest = trip_context.get("destination") or "N/A"
        duration = trip_context.get("duration_days") or "5"
        budget = (
            trip_context.get("budget_total")
            or trip_context.get("budget_breakdown", {}).get(
                "total_budget", "N/A"
            )
        )
        currency = trip_context.get("currency") or "USD"
        party = trip_context.get("traveler_type") or "Travelers"
        pace = trip_context.get("pace") or "Balanced"
        notes = trip_context.get("notes") or ""

        context_str = (
            f"\n\n[Active Trip Context]\n"
            f"- Destination: {dest}\n"
            f"- Duration: {duration} Days\n"
            f"- Total Budget: {currency} {budget}\n"
            f"- Travel Party: {party}\n"
            f"- Pace: {pace}\n"
        )

        if notes:
            context_str += f"- Traveler Wishes / Dietary: {notes}\n"

        if trip_context.get("itinerary"):
            context_str += (
                f"- Planned Itinerary Days: "
                f"{len(trip_context['itinerary'])} days\n"
            )

    # 1. Attempt Google Gemini
    gemini_key = (
        api_key_override
        if provider == "gemini"
        else (
            settings.GEMINI_API_KEY
            or (
                api_key_override
                if (
                    provider == "auto"
                    and api_key_override
                    and api_key_override.startswith("AIza")
                )
                else ""
            )
        )
    )

    if not gemini_key and settings.GEMINI_API_KEY:
        gemini_key = settings.GEMINI_API_KEY

    if provider in ["gemini", "auto"] and gemini_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            full_system = SYSTEM_INSTRUCTION + context_str

            # Build conversation history
            contents = []

            for h in history[-8:]:
                role = "user" if h.get("role") == "user" else "model"

                contents.append(
                    types.Content(
                        role=role,
                        parts=[
                            types.Part.from_text(
                                text=h.get("content", "")
                            )
                        ],
                    )
                )

            # Add current user message
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=message)],
                )
            )

            config = types.GenerateContentConfig(
                system_instruction=full_system,
                temperature=0.6,
                max_output_tokens=800,
            )

            # Try available Gemini models in priority order
            for model_name in [
                "gemini-2.5-flash",
                "gemini-3.5-flash",
                "gemini-3.5-flash-lite",
                "gemini-2.5-pro",
            ]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config,
                    )

                    if response and response.text:
                        return {
                            "reply": response.text.strip(),
                            "provider": "Google Gemini",
                        }

                except Exception as inner_e:
                    print(f"[Gemini {model_name} notice]: {inner_e}")
                    continue

        except Exception as e:
            print(f"[Gemini Chat Error]: {e}")

    # 2. Graceful Fallback: Built-in Travel Knowledge Engine
    fallback_reply = _build_knowledge_reply(message, trip_context)

    return {
        "reply": fallback_reply,
        "provider": "WanderAI Smart Engine",
    }


def _build_knowledge_reply(
    message: str,
    trip_context: Optional[Dict[str, Any]]
) -> str:
    """Smart contextual travel rules and destination insights when LLM is offline."""
    query = message.lower()

    # Identify destination
    target_dest_key = None
    dest_name = "your destination"

    if trip_context and trip_context.get("destination"):
        raw_dest = trip_context["destination"].lower()
        dest_name = trip_context["destination"]

        for k in DESTINATIONS_DATA.keys():
            if k in raw_dest:
                target_dest_key = k
                break

    if not target_dest_key:
        for k in DESTINATIONS_DATA.keys():
            if k in query:
                target_dest_key = k
                dest_name = DESTINATIONS_DATA[k]["name"]
                break

    dest_info = (
        DESTINATIONS_DATA.get(target_dest_key)
        if target_dest_key
        else None
    )

    # Topic 1: Food & Dining
    if any(
        w in query
        for w in [
            "food", "eat", "dining", "restaurant", "culinary",
            "dish", "breakfast", "dinner", "lunch"
        ]
    ):
        if dest_info:
            dining_spots = [
                s for s in dest_info.get("spots", [])
                if s.get("category") == "Dining"
            ]

            spots_text = "\n".join(
                [
                    f"- **{s['name']}**: {s['desc']} "
                    f"(Est. ~{dest_info['currency']} {s['cost']})"
                    for s in dining_spots[:3]
                ]
            )

            return (
                f"Here are top culinary highlights in **{dest_name}**:\n\n"
                f"{spots_text}\n\n"
                f"💡 **Local Dining Tip**: Look for smaller neighborhood "
                f"eateries where locals queue up — that's always where "
                f"you get the most authentic flavors at fair prices!"
            )

        return (
            f"Here are my top culinary strategies for **{dest_name}**:\n\n"
            f"- **Seek Out Morning Markets**: Fresh food stalls and "
            f"regional street food offer the best quality and value.\n"
            f"- **Ask Your Lodging Hosts**: Ask 'Where do you eat on "
            f"your day off?' instead of general recommendations.\n"
            f"- **Reserve Ahead**: For celebrated local dining spots, "
            f"book 2–3 weeks in advance to avoid long waits."
        )

    # Topic 2: Budget & Costs
    if any(
        w in query
        for w in [
            "budget", "cost", "expensive", "cheap",
            "money", "currency", "save"
        ]
    ):
        if dest_info:
            return (
                f"**Budget Insight for {dest_name}**:\n\n"
                f"- **Average Cost Tier**: "
                f"{dest_info.get('cost_tier', 'Moderate')}\n"
                f"- **Local Currency**: "
                f"{dest_info.get('currency', 'Local Currency')}\n"
                f"- **Best Saving Hack**: Take advantage of free temple "
                f"or museum morning hours, public transit day-passes, "
                f"and lunchtime set menus (which are often 40% cheaper "
                f"than dinner)!"
            )

        return (
            f"**Money-Saving Travel Tips for {dest_name}**:\n\n"
            f"- **Daily Transit Passes**: Metro or regional day-passes "
            f"usually pay for themselves in just 3 rides.\n"
            f"- **Lunch Menus**: High-end bistros often offer prix-fixe "
            f"lunch menus at half the dinner price.\n"
            f"- **Card vs. Cash**: Check foreign transaction fees on "
            f"your credit card and keep a small reserve of local "
            f"currency for small vendors."
        )

    # Topic 3: Packing & Weather
    if any(
        w in query
        for w in [
            "pack", "weather", "clothes", "climate",
            "rain", "season", "wear"
        ]
    ):
        if dest_info:
            climate = dest_info.get(
                "climate",
                "Temperate seasonal conditions."
            )

            return (
                f"**Climate & Packing Guide for {dest_name}**:\n\n"
                f"- **Forecast Insight**: {climate}\n"
                f"- **Essential Footwear**: Comfortable, broken-in "
                f"walking shoes (expect 12,000–18,000 steps daily).\n"
                f"- **Layers**: A lightweight breathable jacket, "
                f"compact umbrella, and travel adapter are essential.\n"
                f"- Check out the **Packing Checklist tab** on your "
                f"itinerary dashboard to mark items off as you pack!"
            )

        return (
            f"**Packing Strategy for {dest_name}**:\n\n"
            f"- **Capsule Wardrobe**: Stick to versatile neutral layers "
            f"you can mix and match.\n"
            f"- **Comfortable Walking Shoes**: The single most "
            f"important item for city exploration.\n"
            f"- **Tech Essentials**: Universal power plug adapter "
            f"and a 10,000mAh portable power bank."
        )

    # Topic 4: Sights & Activities
    if any(
        w in query
        for w in [
            "sights", "must see", "visit", "attraction",
            "things to do", "places"
        ]
    ):
        if dest_info:
            spots = dest_info.get("spots", [])[:4]

            spots_list = "\n".join(
                [
                    f"- **{s['name']}** "
                    f"({s.get('best_time', 'Daytime')}): {s['desc']}"
                    for s in spots
                ]
            )

            return (
                f"Here are must-experience highlights for "
                f"**{dest_name}**:\n\n"
                f"{spots_list}\n\n"
                f"Would you like to build these into a tailored "
                f"day-by-day itinerary? Use the **Plan a Trip** "
                f"builder above to get your custom schedule!"
            )

    # Topic 5: General greetings / Travel advice
    if any(
        w in query
        for w in ["hello", "hi", "hey", "help", "who are you"]
    ):
        return (
            f"Hello! 👋 I'm your **WanderAI Travel Assistant**.\n\n"
            f"I can help you with:\n"
            f"- **Curating destinations & sights** matching your vibe\n"
            f"- **Local food & restaurant picks**\n"
            f"- **Budget strategies & daily expense estimates**\n"
            f"- **Packing suggestions & seasonal weather advice**\n\n"
            f"Where are you dreaming of traveling next, or how can "
            f"I assist with your current plan?"
        )

    # General Helpful Travel Response
    return (
        f"Great travel question about **{dest_name}**! 🌍\n\n"
        f"To ensure a seamless trip, consider balancing high-energy "
        f"sightseeing in the morning with leisurely neighborhood "
        f"strolls and cafe visits in the afternoon.\n\n"
        f"If you'd like a full day-by-day schedule with real cost "
        f"breakdowns and an interactive map, click **Plan My Trip** "
        f"above to generate a complete custom itinerary!"
    )
