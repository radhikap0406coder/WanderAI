from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentLog(BaseModel):
    agent: str
    status: str # "running" | "completed" | "info"
    message: str
    timestamp: str

class Activity(BaseModel):
    time_slot: str # "Morning" | "Afternoon" | "Evening"
    time: str # "09:00 - 11:30"
    title: str
    description: str
    location: str
    coordinates: List[float] = Field(default_factory=lambda: [0.0, 0.0])
    category: str # "Attraction" | "Dining" | "Culture" | "Nature" | "Nightlife"
    estimated_cost: float
    tips: Optional[str] = ""

class DayPlan(BaseModel):
    day_number: int
    date_label: str
    theme: str
    summary: str
    activities: List[Activity]
    day_total_cost: float
    transit_tips: str

class BudgetCategory(BaseModel):
    name: str
    allocated_amount: float
    percentage: float
    description: str

class BudgetBreakdown(BaseModel):
    total_budget: float
    estimated_total_cost: float
    currency: str
    variance: float
    status: str # "Under Budget" | "On Budget" | "Over Budget"
    per_person_per_day: float
    categories: Dict[str, BudgetCategory]
    saving_tips: List[str]
    luxury_upgrades: List[str]

class PackingGuide(BaseModel):
    category: str
    items: List[str]

class MapMarker(BaseModel):
    id: str
    day: int
    title: str
    description: str
    category: str
    coordinates: List[float] # [lat, lng]
    time_slot: str

class TripPlanResponse(BaseModel):
    trip_id: str
    title: str
    destination: str
    origin: str
    duration_days: int
    dates: str
    travelers_count: int
    traveler_type: str
    currency: str
    vibe_summary: str
    climate_guide: str
    local_customs: List[str]
    emergency_contacts: Dict[str, str]
    itinerary: List[DayPlan]
    budget_breakdown: BudgetBreakdown
    map_markers: List[MapMarker]
    packing_checklist: List[PackingGuide]
    agent_logs: List[AgentLog]
    execution_time_seconds: float
