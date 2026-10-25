from langgraph.graph import StateGraph, START, END
from app.agents.state import TripPlannerState
from app.agents.destination_agent import destination_agent_node
from app.agents.budget_agent import budget_agent_node
from app.agents.preferences_agent import preferences_agent_node
from app.agents.research_agent import research_agent_node
from app.agents.itinerary_agent import itinerary_agent_node
from app.agents.calculator_agent import calculator_agent_node
from app.agents.final_planner_agent import final_planner_agent_node

def build_trip_planner_graph():
    """
    Constructs the LangGraph multi-agent orchestration workflow:
    
                     START
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
    Destination     Budget       Preferences
       Agent         Agent          Agent
        ↓              ↓              ↓
        └──────────────┼──────────────┘
                       ↓
               Research / Search
                       ↓
              Itinerary Generator
                       ↓
               Budget Calculator
                       ↓
                 Final Planner
                       ↓
                      END
    """
    workflow = StateGraph(TripPlannerState)

    # Add agent nodes
    workflow.add_node("destination_agent", destination_agent_node)
    workflow.add_node("budget_agent", budget_agent_node)
    workflow.add_node("preferences_agent", preferences_agent_node)
    workflow.add_node("research_agent", research_agent_node)
    workflow.add_node("itinerary_generator", itinerary_agent_node)
    workflow.add_node("budget_calculator", calculator_agent_node)
    workflow.add_node("final_planner", final_planner_agent_node)

    # Flow: START -> Destination, Budget, Preferences concurrently
    workflow.add_edge(START, "destination_agent")
    workflow.add_edge(START, "budget_agent")
    workflow.add_edge(START, "preferences_agent")

    # All three feed into Research / Search Agent
    workflow.add_edge("destination_agent", "research_agent")
    workflow.add_edge("budget_agent", "research_agent")
    workflow.add_edge("preferences_agent", "research_agent")

    # Research -> Itinerary Generator -> Budget Calculator -> Final Planner -> END
    workflow.add_edge("research_agent", "itinerary_generator")
    workflow.add_edge("itinerary_generator", "budget_calculator")
    workflow.add_edge("budget_calculator", "final_planner")
    workflow.add_edge("final_planner", END)

    return workflow.compile()

# Pre-compiled graph instance
trip_graph = build_trip_planner_graph()
