import operator
from typing import TypedDict, Annotated, List, Dict, Any, Optional

class TripPlannerState(TypedDict, total=False):
    # User Inputs
    origin: str
    destination: str
    start_date: Optional[str]
    duration_days: int
    budget_total: float
    currency: str
    travelers_count: int
    traveler_type: str
    adults_count: Optional[int]
    children_count: Optional[int]
    is_per_person_budget: Optional[bool]
    transport_mode: Optional[str]
    interests: List[str]
    accommodation_type: str
    pace: str
    notes: Optional[str]
    api_key: Optional[str]
    provider: Optional[str]

    # Pipeline Artifacts produced by Agents
    destination_data: Dict[str, Any]
    budget_strategy: Dict[str, Any]
    preferences_profile: Dict[str, Any]
    research_data: Dict[str, Any]
    itinerary_draft: List[Dict[str, Any]]
    budget_breakdown: Dict[str, Any]
    final_trip_plan: Dict[str, Any]
    provider_used: Optional[str]
    is_fallback: Optional[bool]
    fallback_reason: Optional[str]
    
    # Progress & Execution Logs - accumulated automatically via LangGraph reducer
    agent_logs: Annotated[List[Dict[str, Any]], operator.add]
