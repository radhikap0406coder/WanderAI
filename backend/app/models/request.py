from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TripPlanRequest(BaseModel):
    origin: str = Field(default="New York, USA", description="City of origin")
    destination: str = Field(..., description="Target travel destination or dream vibe")
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    duration_days: int = Field(default=5, ge=1, le=14, description="Trip duration in days")
    budget_total: float = Field(default=2500.0, ge=100.0, description="Total budget in chosen currency")
    currency: str = Field(default="USD", description="Currency code (USD, EUR, GBP, INR, JPY, etc.)")
    travelers_count: int = Field(default=2, ge=1, le=20, description="Number of travelers")
    traveler_type: str = Field(default="Couple", description="Traveler profile: Solo, Couple, Family, Friends")
    adults_count: Optional[int] = Field(default=None, description="Number of adults (for families)")
    children_count: Optional[int] = Field(default=None, description="Number of children (for families)")
    is_per_person_budget: bool = Field(default=False, description="True if budget is per-person, False if group total")
    transport_mode: Optional[str] = Field(default=None, description="Preferred intercity travel mode (Train, Flight, Bus, Drive)")
    interests: List[str] = Field(
        default_factory=lambda: ["Culture & History", "Culinary & Dining", "Sightseeing"],
        description="Key interests or focus themes"
    )
    accommodation_type: str = Field(
        default="Boutique / 4-Star",
        description="Hostel, Budget Hotel, Boutique / 4-Star, Luxury 5-Star, Vacation Rental"
    )
    pace: str = Field(default="Balanced", description="Relaxed, Balanced, Fast-Paced")
    notes: Optional[str] = Field(default="", description="Specific requirements, dietary restrictions, mobility notes")
    
    # Optional client-side API key configuration
    api_key: Optional[str] = Field(default=None, description="User-supplied API key (Gemini / OpenAI)")
    provider: Optional[str] = Field(default="auto", description="Provider choice: gemini, openai, groq, auto")

class QuickDestination(BaseModel):
    id: str
    name: str
    country: str
    description: str
    tagline: str
    image_url: str
    recommended_duration: int
    popular_interests: List[str]
    coordinates: List[float] # [lat, lng]

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message text")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Recent conversation turns")
    trip_context: Optional[Dict[str, Any]] = Field(default=None, description="Active trip or preferences context")
    provider: Optional[str] = Field(default="auto", description="LLM provider: gemini, openai, groq, auto")
    api_key: Optional[str] = Field(default=None, description="Optional API key override")