import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.agents.calculator_agent import (
    calculator_agent_node,
    estimate_intercity_transport,
    is_india_location
)
from app.agents.budget_agent import budget_agent_node
from app.services.chat_service import generate_chat_reply
from app.data.destination_knowledge import DESTINATIONS_DATA, get_destination_data

class TestWanderAIFixes(unittest.TestCase):

    def test_01_india_location_detection(self):
        """Test detection of Indian origins and destinations."""
        self.assertTrue(is_india_location("Indore, India"))
        self.assertTrue(is_india_location("Jaipur, India"))
        self.assertTrue(is_india_location("New Delhi, India"))
        self.assertTrue(is_india_location("Goa, India"))
        self.assertFalse(is_india_location("Tokyo, Japan"))
        self.assertFalse(is_india_location("Paris, France"))

    def test_02_intercity_transport_indore_to_jaipur(self):
        """Test realistic intercity round-trip transportation between Indore and Jaipur."""
        cost, mode, desc = estimate_intercity_transport(
            origin="Indore, India",
            destination="Jaipur, India",
            travelers=4,
            currency="INR",
            accommodation_style="Budget Hotel",
            group_budget=25000.0
        )
        self.assertGreater(cost, 4000.0, "Round trip transport for 4 people should exceed ₹4,000")
        self.assertLess(cost, 15000.0, "Budget train/bus shouldn't exceed ₹15,000")
        self.assertIn("Round-Trip", mode)

    def test_03_realistic_budget_indore_to_jaipur(self):
        """
        Critical Test: Verify Indore to Jaipur 5 days, 4 travelers, budget ₹25,000
        Must NOT produce under-estimated ₹4,153!
        Must realistically calculate total group cost > ₹28,000 and report shortfall.
        """
        state = {
            "origin": "Indore, India",
            "destination": "Jaipur, India",
            "duration_days": 5,
            "travelers_count": 4,
            "traveler_type": "Friends",
            "budget_total": 25000.0,
            "currency": "INR",
            "accommodation_type": "Budget Hotel",
            "agent_logs": []
        }
        res = calculator_agent_node(state)
        b = res["budget_breakdown"]

        # 1. Total budget must remain total group budget (₹25,000), NOT multiplied by 4
        self.assertEqual(b["total_budget"], 25000.0)

        # 2. Total estimated cost must be realistic (> ₹28,000)
        self.assertGreater(b["estimated_total_cost"], 28000.0, f"Expected realistic total cost > ₹28,000, got {b['estimated_total_cost']}")

        # 3. Must detect Budget Shortfall because ₹30k+ > ₹25k
        self.assertEqual(b["status"], "Budget Shortfall")
        self.assertGreater(b["shortfall"], 5000.0)

        # 4. Check category allocations
        cats = b["categories"]
        self.assertIn("transportation", cats)
        self.assertIn("accommodation", cats)
        self.assertIn("dining", cats)
        self.assertIn("local_transit", cats)
        self.assertIn("activities", cats)
        self.assertIn("contingency", cats)

        # 5. Check lodging: 4 friends require 2 rooms for 4 nights
        self.assertEqual(b["rooms_count"], 2)
        self.assertEqual(b["nights_count"], 4)
        self.assertGreater(cats["accommodation"]["allocated_amount"], 5000.0)

        # 6. Check dining: 4 people × 5 days
        self.assertGreater(cats["dining"]["allocated_amount"], 6000.0)

        # 7. Check per person metrics
        self.assertGreater(b["per_person"], 7000.0)
        self.assertGreater(b["per_person_per_day"], 1400.0)

        # 8. Check actionable trade-offs
        self.assertTrue(len(b["saving_tips"]) >= 3)

    def test_04_budget_agent_currency_tiers(self):
        """Test currency-aware tier determination in budget_agent."""
        # Indore to Jaipur: ₹25,000 for 4 people, 5 days => ₹1,250/person/day
        # In INR, ₹1,250 is Comfort Explorer, NOT Ultra Luxury!
        state_inr = {
            "budget_total": 25000.0,
            "currency": "INR",
            "duration_days": 5,
            "travelers_count": 4,
            "accommodation_type": "Budget Hotel",
            "destination": "Jaipur, India",
            "provider": "mock",
            "agent_logs": []
        }
        res_inr = budget_agent_node(state_inr)
        strat = res_inr["budget_strategy"]
        self.assertNotEqual(strat["tier"], "Ultra Luxury", "₹1,250/day in India must NOT be called Ultra Luxury!")
        self.assertEqual(strat["daily_allowance"], 5000.0)
        self.assertEqual(strat["per_person_per_day"], 1250.0)

    def test_05_jaipur_destination_knowledge(self):
        """Test Jaipur presence in destination knowledge base."""
        data = get_destination_data("Jaipur, India")
        self.assertEqual(data["name"], "Jaipur, India")
        self.assertEqual(data["country"], "India")
        self.assertEqual(data["currency"], "INR")
        self.assertTrue(any("Amber Fort" in s["name"] for s in data["spots"]))
        self.assertTrue(any("Hawa Mahal" in s["name"] for s in data["spots"]))

    def test_06_ai_chat_reply(self):
        """Test conversational AI chat service with trip context."""
        reply = generate_chat_reply(
            message="What are the top must-try local dishes in Jaipur?",
            trip_context={
                "destination": "Jaipur, India",
                "duration_days": 5,
                "currency": "INR",
                "travelers_count": 4,
                "budget_total": 25000
            },
            provider="smart_engine"
        )
        self.assertIn("reply", reply)
        self.assertIn("provider", reply)
        self.assertTrue(len(reply["reply"]) > 50)

    def test_07_international_budget_nyc_to_tokyo(self):
        """Test international travel budget calculation (NYC to Tokyo, 2 travelers, 5 days)."""
        state = {
            "origin": "New York, USA",
            "destination": "Tokyo, Japan",
            "duration_days": 5,
            "travelers_count": 2,
            "traveler_type": "Couple",
            "budget_total": 3500.0,
            "currency": "USD",
            "accommodation_type": "Comfort Hotel (3-Star)",
            "agent_logs": []
        }
        res = calculator_agent_node(state)
        b = res["budget_breakdown"]
        self.assertGreater(b["estimated_total_cost"], 2500.0)
        self.assertEqual(b["rooms_count"], 1)
        self.assertEqual(b["nights_count"], 4)

if __name__ == "__main__":
    unittest.main()

