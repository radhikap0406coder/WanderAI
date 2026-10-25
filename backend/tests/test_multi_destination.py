import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.data.destination_knowledge import (
    classify_destination,
    parse_multi_city,
    get_destination_data,
    STATE_REGION_REGISTRY,
    DESTINATIONS_DATA
)
from app.agents.itinerary_agent import distribute_days_across_cities
from app.graph.trip_graph import trip_graph

class TestMultiDestinationPlanning(unittest.TestCase):
    """
    Comprehensive tests for WanderAI Multi-Destination and State-Level Trip Planning.
    Verifies:
      Case 1: Indore -> Uttarakhand / uttrakhand (10 days, 6 friends, ₹1,20,000 group budget)
      Case 2: Indore -> Uttarakhand (3 days, smaller number of destinations)
      Case 3: Indore -> Jaipur (3 days, single city focus)
      Case 4: Indore -> Dehradun (4 days, single city focus)
      Case 5: Multi-city input ("Dehradun, Mussoorie, and Rishikesh", 5 days)
    """

    def test_01_classification_and_spelling_variants(self):
        """Test destination classification across single cities, state/region, aliases, and explicit multi-city."""
        # Single cities (must remain SINGLE_CITY even if inside a state)
        self.assertEqual(classify_destination("Jaipur")["type"], "SINGLE_CITY")
        self.assertEqual(classify_destination("Dehradun")["type"], "SINGLE_CITY")
        self.assertEqual(classify_destination("Rishikesh")["type"], "SINGLE_CITY")
        self.assertEqual(classify_destination("Mussoorie")["type"], "SINGLE_CITY")
        self.assertEqual(classify_destination("Haridwar")["type"], "SINGLE_CITY")
        self.assertEqual(classify_destination("Paris")["type"], "SINGLE_CITY")

        # States and regions with standard and spelling variations
        self.assertEqual(classify_destination("Uttarakhand")["type"], "STATE_REGION")
        self.assertEqual(classify_destination("uttrakhand")["type"], "STATE_REGION")
        self.assertEqual(classify_destination("uttaranchal")["type"], "STATE_REGION")
        self.assertEqual(classify_destination("Uttarakhand, India")["type"], "STATE_REGION")
        self.assertEqual(classify_destination("Himachal Pradesh")["type"], "STATE_REGION")
        self.assertEqual(classify_destination("himachal")["type"], "STATE_REGION")
        self.assertEqual(classify_destination("Rajasthan")["type"], "STATE_REGION")
        self.assertEqual(classify_destination("Kerala")["type"], "STATE_REGION")

        # Explicit multi-city
        self.assertEqual(classify_destination("Dehradun, Mussoorie, and Rishikesh")["type"], "MULTI_CITY")
        self.assertEqual(classify_destination("Delhi - Agra - Jaipur")["type"], "MULTI_CITY")
        self.assertEqual(classify_destination("Goa and Mumbai")["type"], "MULTI_CITY")

        # Multi-city parsing
        cities = parse_multi_city("Dehradun, Mussoorie, and Rishikesh")
        self.assertEqual(cities, ["Dehradun", "Mussoorie", "Rishikesh"])

    def test_02_uttarakhand_circuit_selection_by_duration(self):
        """Test that state-level planning adapts circuit hubs to duration."""
        # 3 days in Uttarakhand -> 2 hubs (Haridwar, Rishikesh)
        data_3d = get_destination_data("Uttarakhand", duration_days=3)
        self.assertEqual(data_3d["destination_type"], "STATE_REGION")
        self.assertEqual(data_3d["circuit_cities"], ["Haridwar", "Rishikesh"])

        # 4-5 days in Uttarakhand -> 3 hubs (Haridwar, Rishikesh, Dehradun)
        data_5d = get_destination_data("Uttarakhand", duration_days=5)
        self.assertEqual(data_5d["circuit_cities"], ["Haridwar", "Rishikesh", "Dehradun"])

        # 7-10 days in Uttarakhand / uttrakhand -> 4 hubs (Haridwar, Rishikesh, Dehradun, Mussoorie)
        data_10d = get_destination_data("uttrakhand", duration_days=10)
        self.assertEqual(data_10d["destination_type"], "STATE_REGION")
        self.assertEqual(data_10d["circuit_cities"], ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"])

    def test_03_day_distribution_across_circuit(self):
        """Test day distribution algorithm across cities."""
        # 10 days across 4 hubs
        cities_10d = distribute_days_across_cities(
            ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"], 10
        )
        self.assertEqual(len(cities_10d), 10)
        self.assertEqual(cities_10d, [
            "Haridwar", "Haridwar", "Haridwar",
            "Rishikesh", "Rishikesh", "Rishikesh",
            "Dehradun", "Dehradun",
            "Mussoorie", "Mussoorie"
        ])

        # 3 days in single city Jaipur
        cities_jaipur = distribute_days_across_cities(["Jaipur"], 3)
        self.assertEqual(cities_jaipur, ["Jaipur", "Jaipur", "Jaipur"])

        # 3 days in Uttarakhand (2 hubs)
        cities_uk_3d = distribute_days_across_cities(["Haridwar", "Rishikesh"], 3)
        self.assertEqual(cities_uk_3d, ["Haridwar", "Haridwar", "Rishikesh"])

        # 4 days in Dehradun
        cities_ddn_4d = distribute_days_across_cities(["Dehradun"], 4)
        self.assertEqual(cities_ddn_4d, ["Dehradun", "Dehradun", "Dehradun", "Dehradun"])

    def test_04_full_workflow_case1_uttrakhand_10days(self):
        """
        User Problem Test: Origin Indore, Destination 'uttrakhand' (spelt without middle 'a'),
        10 days, 6 friends, total group budget ₹1,20,000.
        Verifies:
          - Classified as STATE_REGION, NOT single city.
          - Circuit covers real destinations: Haridwar, Rishikesh, Dehradun, Mussoorie.
          - Daily itinerary covers multiple destinations.
          - Daily attractions are real, location-specific places (NO 'Uttrakhand Historic Old Town').
          - Intercity travel legs link the circuit hubs.
          - Fallback status and provider are clearly tracked.
        """
        initial_state = {
            "origin": "indore",
            "destination": "uttrakhand",
            "duration_days": 10,
            "start_date": "2026-11-08",
            "budget_total": 120000.0,
            "currency": "INR",
            "traveler_type": "Friends",
            "travelers_count": 6,
            "accommodation_type": "Budget / Hostel",
            "pace": "Relaxed",
            "interests": ["Culture & History", "Nature & Outdoors", "Scenic Photography"],
            "notes": "",
            "provider": "mock",
            "agent_logs": []
        }

        result = trip_graph.invoke(initial_state)
        plan = result.get("final_trip_plan")
        self.assertIsNotNone(plan)

        # 1. Destination classification & circuit hubs
        dest_data = result.get("destination_data", {})
        self.assertEqual(dest_data.get("destination_type"), "STATE_REGION")
        circuit = dest_data.get("circuit_cities", [])
        self.assertEqual(circuit, ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"])

        # 2. Daily itinerary verification
        itinerary = plan.get("itinerary", [])
        self.assertEqual(len(itinerary), 10)
        visited_cities = [day.get("current_city") for day in itinerary]
        unique_visited = set(visited_cities)
        self.assertEqual(unique_visited, {"Haridwar", "Rishikesh", "Dehradun", "Mussoorie"})

        # Confirm sequential city progression
        self.assertEqual(visited_cities[:3], ["Haridwar", "Haridwar", "Haridwar"])
        self.assertEqual(visited_cities[3:6], ["Rishikesh", "Rishikesh", "Rishikesh"])
        self.assertEqual(visited_cities[6:8], ["Dehradun", "Dehradun"])
        self.assertEqual(visited_cities[8:], ["Mussoorie", "Mussoorie"])

        # 3. Intercity travel legs
        self.assertIn("indore to Haridwar", itinerary[0].get("travel_leg", ""))
        self.assertIn("Haridwar to Rishikesh", itinerary[3].get("travel_leg", ""))
        self.assertIn("Rishikesh to Dehradun", itinerary[6].get("travel_leg", ""))
        self.assertIn("Dehradun to Mussoorie", itinerary[8].get("travel_leg", ""))
        self.assertIn("Return to indore", itinerary[9].get("travel_leg", ""))

        # 4. No fabricated attractions: verify real landmark names
        for day in itinerary:
            city = day.get("current_city")
            for act in day.get("activities", []):
                title = act.get("title", "")
                loc = act.get("location", "")
                # Must NOT contain generic fabricated strings
                self.assertNotIn("Uttrakhand Historic Old Town", title)
                self.assertNotIn("Central Square", title)
                # Location must mention the day's city
                self.assertTrue(city in loc or city in title, f"Activity {title} ({loc}) should belong to {city}")

        # 5. Check provider tracking & fallback transparency
        self.assertTrue(plan.get("is_fallback"))
        self.assertIn("Fallback", plan.get("provider", ""))

        # 6. Budget calculations
        budget = plan.get("budget_breakdown", {})
        self.assertEqual(budget.get("total_budget"), 120000.0)
        self.assertEqual(budget.get("travelers_count"), 6)
        self.assertEqual(budget.get("duration_days"), 10)

    def test_05_full_workflow_case2_uttarakhand_3days(self):
        """
        Case 2: Indore -> Uttarakhand, 3 days.
        Must prioritize a smaller number of destinations (Haridwar & Rishikesh).
        """
        initial_state = {
            "origin": "indore",
            "destination": "Uttarakhand",
            "duration_days": 3,
            "start_date": "2026-11-08",
            "budget_total": 40000.0,
            "currency": "INR",
            "traveler_type": "Couple",
            "travelers_count": 2,
            "accommodation_type": "Budget Hotel",
            "pace": "Moderate",
            "interests": ["Culture", "Nature"],
            "notes": "",
            "provider": "mock",
            "agent_logs": []
        }

        result = trip_graph.invoke(initial_state)
        plan = result.get("final_trip_plan")
        dest_data = result.get("destination_data", {})

        self.assertEqual(dest_data.get("destination_type"), "STATE_REGION")
        circuit = dest_data.get("circuit_cities", [])
        self.assertEqual(circuit, ["Haridwar", "Rishikesh"])

        itinerary = plan.get("itinerary", [])
        self.assertEqual(len(itinerary), 3)
        visited_cities = {day.get("current_city") for day in itinerary}
        self.assertEqual(visited_cities, {"Haridwar", "Rishikesh"})

    def test_06_full_workflow_case3_jaipur_3days(self):
        """
        Case 3: Indore -> Jaipur, 3 days.
        Must remain strictly Jaipur-focused (single city).
        """
        initial_state = {
            "origin": "indore",
            "destination": "Jaipur",
            "duration_days": 3,
            "start_date": "2026-11-08",
            "budget_total": 25000.0,
            "currency": "INR",
            "traveler_type": "Couple",
            "travelers_count": 2,
            "accommodation_type": "Boutique Hotel",
            "pace": "Relaxed",
            "interests": ["Culture", "Food"],
            "notes": "",
            "provider": "mock",
            "agent_logs": []
        }

        result = trip_graph.invoke(initial_state)
        plan = result.get("final_trip_plan")
        dest_data = result.get("destination_data", {})

        self.assertEqual(dest_data.get("destination_type"), "SINGLE_CITY")
        self.assertEqual(dest_data.get("circuit_cities"), ["Jaipur"])

        itinerary = plan.get("itinerary", [])
        self.assertEqual(len(itinerary), 3)
        for day in itinerary:
            self.assertEqual(day.get("current_city"), "Jaipur")

    def test_07_full_workflow_case4_dehradun_4days(self):
        """
        Case 4: Indore -> Dehradun, 4 days.
        Must remain strictly Dehradun-focused (single city).
        """
        initial_state = {
            "origin": "indore",
            "destination": "Dehradun",
            "duration_days": 4,
            "start_date": "2026-11-08",
            "budget_total": 30000.0,
            "currency": "INR",
            "traveler_type": "Couple",
            "travelers_count": 2,
            "accommodation_type": "Budget Hotel",
            "pace": "Moderate",
            "interests": ["Nature"],
            "notes": "",
            "provider": "mock",
            "agent_logs": []
        }

        result = trip_graph.invoke(initial_state)
        plan = result.get("final_trip_plan")
        dest_data = result.get("destination_data", {})

        self.assertEqual(dest_data.get("destination_type"), "SINGLE_CITY")
        self.assertEqual(dest_data.get("circuit_cities"), ["Dehradun"])

        itinerary = plan.get("itinerary", [])
        self.assertEqual(len(itinerary), 4)
        for day in itinerary:
            self.assertEqual(day.get("current_city"), "Dehradun")

    def test_08_full_workflow_case5_explicit_multi_city(self):
        """
        Case 5: Multi-city input: "Dehradun, Mussoorie, and Rishikesh", 5 days.
        Must preserve all 3 requested destinations.
        """
        initial_state = {
            "origin": "indore",
            "destination": "Dehradun, Mussoorie, and Rishikesh",
            "duration_days": 5,
            "start_date": "2026-11-08",
            "budget_total": 45000.0,
            "currency": "INR",
            "traveler_type": "Friends",
            "travelers_count": 3,
            "accommodation_type": "Budget Hotel",
            "pace": "Moderate",
            "interests": ["Nature", "Culture"],
            "notes": "",
            "provider": "mock",
            "agent_logs": []
        }

        result = trip_graph.invoke(initial_state)
        plan = result.get("final_trip_plan")
        dest_data = result.get("destination_data", {})

        self.assertEqual(dest_data.get("destination_type"), "MULTI_CITY")
        circuit = dest_data.get("circuit_cities", [])
        self.assertEqual(set(circuit), {"Dehradun", "Mussoorie", "Rishikesh"})

        itinerary = plan.get("itinerary", [])
        self.assertEqual(len(itinerary), 5)
        visited = {day.get("current_city") for day in itinerary}
        self.assertEqual(visited, {"Dehradun", "Mussoorie", "Rishikesh"})

if __name__ == "__main__":
    unittest.main()
