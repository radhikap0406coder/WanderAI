import unittest
import json
import uuid
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from app.main import app
import app.db.database as db
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token


class TestAuthAndTripPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        db.init_db()

    def setUp(self):
        self.test_email = f"traveler_{uuid.uuid4().hex[:6]}@wanderai.test"
        self.test_password = "SecurePassword123!"
        self.test_name = "Aria Stark"

    def test_01_password_hashing(self):
        hashed = hash_password(self.test_password)
        self.assertNotEqual(hashed, self.test_password)
        self.assertTrue(verify_password(self.test_password, hashed))
        self.assertFalse(verify_password("WrongPassword!", hashed))

    def test_02_jwt_token_creation_and_decoding(self):
        user_id = "user_test_123"
        token = create_access_token(user_id, "test@wanderai.com")
        self.assertIsInstance(token, str)
        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("sub"), user_id)
        self.assertEqual(payload.get("email"), "test@wanderai.com")

    def test_03_user_registration_success(self):
        res = self.client.post("/api/auth/register", json={
            "full_name": self.test_name,
            "email": self.test_email,
            "password": self.test_password,
        })
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["user"]["email"], self.test_email.lower())
        self.assertEqual(data["user"]["full_name"], self.test_name)
        self.assertNotIn("password", data["user"])
        self.assertNotIn("password_hash", data["user"])

    def test_04_duplicate_email_registration_fails(self):
        # First registration
        email = f"dup_{uuid.uuid4().hex[:6]}@wanderai.test"
        res1 = self.client.post("/api/auth/register", json={
            "full_name": "Original User",
            "email": email,
            "password": "Password123!",
        })
        self.assertEqual(res1.status_code, 200)

        # Duplicate registration
        res2 = self.client.post("/api/auth/register", json={
            "full_name": "Duplicate User",
            "email": email,
            "password": "Password123!",
        })
        self.assertEqual(res2.status_code, 400)
        self.assertIn("already exists", res2.json().get("detail", "").lower())

    def test_05_short_password_rejected(self):
        res = self.client.post("/api/auth/register", json={
            "full_name": "Short Pass",
            "email": f"short_{uuid.uuid4().hex[:6]}@test.com",
            "password": "short",
        })
        self.assertEqual(res.status_code, 422)

    def test_06_login_success_and_failure(self):
        email = f"login_{uuid.uuid4().hex[:6]}@wanderai.test"
        pwd = "ValidPass1234!"
        reg = self.client.post("/api/auth/register", json={
            "full_name": "Login Tester",
            "email": email,
            "password": pwd,
        })
        self.assertEqual(reg.status_code, 200)

        # Valid login
        login_ok = self.client.post("/api/auth/login", json={
            "email": email,
            "password": pwd,
        })
        self.assertEqual(login_ok.status_code, 200)
        self.assertIn("access_token", login_ok.json())

        # Invalid password
        login_bad = self.client.post("/api/auth/login", json={
            "email": email,
            "password": "WrongPassword999!",
        })
        self.assertEqual(login_bad.status_code, 401)
        self.assertIn("invalid email or password", login_bad.json().get("detail", "").lower())

    def test_07_auth_me_endpoint(self):
        email = f"me_{uuid.uuid4().hex[:6]}@wanderai.test"
        pwd = "ValidPass1234!"
        reg = self.client.post("/api/auth/register", json={
            "full_name": "Me Tester",
            "email": email,
            "password": pwd,
        })
        token = reg.json()["access_token"]

        # Call /api/auth/me with bearer token
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.json()
        self.assertEqual(me_data["email"], email.lower())
        self.assertEqual(me_data["full_name"], "Me Tester")

    def test_08_complete_itinerary_persistence_and_user_ownership(self):
        # 1. Register User A
        email_a = f"usera_{uuid.uuid4().hex[:6]}@wanderai.test"
        reg_a = self.client.post("/api/auth/register", json={
            "full_name": "User A",
            "email": email_a,
            "password": "PasswordUserA123!",
        })
        token_a = reg_a.json()["access_token"]
        user_a_id = reg_a.json()["user"]["id"]

        # 2. Register User B
        email_b = f"userb_{uuid.uuid4().hex[:6]}@wanderai.test"
        reg_b = self.client.post("/api/auth/register", json={
            "full_name": "User B",
            "email": email_b,
            "password": "PasswordUserB123!",
        })
        token_b = reg_b.json()["access_token"]

        # 3. Create a comprehensive 5-day Jaipur trip with full itinerary
        trip_id = f"trip_test_{uuid.uuid4().hex[:8]}"
        trip_payload = {
            "trip_id": trip_id,
            "title": "5-Day Jaipur Heritage & Culinary Expedition",
            "destination": "Jaipur, India",
            "origin": "Indore, India",
            "duration_days": 5,
            "dates": "5 Days Exploration",
            "travelers_count": 4,
            "traveler_type": "Friends",
            "currency": "INR",
            "vibe_summary": "Royal palaces and colorful bazaars",
            "budget_breakdown": {
                "total_budget": 25000.0,
                "estimated_total_cost": 47208.0,
                "variance": -22208.0,
                "shortfall": 22208.0,
                "status": "Budget Shortfall",
                "per_person": 11802.0,
                "per_person_per_day": 2360.4,
                "categories": {
                    "accommodation": {"name": "Lodging", "allocated_amount": 16000.0},
                    "transportation": {"name": "Intercity Transport", "allocated_amount": 6000.0},
                }
            },
            "itinerary": [
                {
                    "day_number": 1,
                    "date_label": "Day 1 · Welcome to Jaipur",
                    "theme": "Pink City Arrival & Old City Walk",
                    "summary": "Arrive from Indore, check into hotel, explore Hawa Mahal",
                    "activities": [
                        {
                            "time_slot": "Morning",
                            "time": "09:00 - 12:00",
                            "title": "Arrival & City Center Check-in",
                            "description": "Settle in and refresh after the journey.",
                            "location": "Jaipur City Center",
                            "category": "Logistics",
                            "estimated_cost": 0.0,
                            "tips": "Pre-book auto-rickshaw to hotel"
                        },
                        {
                            "time_slot": "Afternoon",
                            "time": "14:00 - 17:00",
                            "title": "Hawa Mahal & Old City Bazaars",
                            "description": "Marvel at the Palace of Winds and stroll Johari Bazaar.",
                            "location": "Hawa Mahal",
                            "category": "Culture",
                            "estimated_cost": 200.0,
                            "tips": "Great vantage point from Wind View Cafe across the street"
                        },
                        {
                            "time_slot": "Evening",
                            "time": "19:00 - 21:30",
                            "title": "Dinner at Laxmi Mishthan Bhandar (LMB)",
                            "description": "Authentic Rajasthani thali and pyaaz kachori.",
                            "location": "Johari Bazaar",
                            "category": "Dining",
                            "estimated_cost": 1800.0,
                            "tips": "Try the special Rajasthani sweets"
                        }
                    ],
                    "day_total_cost": 2000.0,
                    "transit_tips": "Short auto-rickshaw hop"
                }
            ],
            "map_markers": [
                {"id": "marker_1", "day": 1, "title": "Hawa Mahal", "coordinates": [26.9239, 75.8267]}
            ],
            "packing_checklist": [
                {"category": "Documents", "items": ["Govt Photo ID", "Train E-Tickets"]}
            ],
            "trip_request": {
                "origin": "Indore, India",
                "destination": "Jaipur, India",
                "duration_days": 5,
                "travelers_count": 4,
                "budget_total": 25000.0
            }
        }

        # 4. Save trip to database under User A's ownership
        db.save_trip(trip_payload, user_id=user_a_id)

        # 5. Verify direct database storage contains the complete itinerary
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT user_id, full_data FROM trips WHERE id = ?", (trip_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["user_id"], user_a_id)
            stored_json = json.loads(row["full_data"])
            self.assertIn("itinerary", stored_json)
            self.assertEqual(len(stored_json["itinerary"]), 1)
            self.assertEqual(stored_json["itinerary"][0]["activities"][1]["title"], "Hawa Mahal & Old City Bazaars")
            self.assertEqual(stored_json["budget_breakdown"]["total_budget"], 25000.0)
            self.assertEqual(stored_json["budget_breakdown"]["estimated_total_cost"], 47208.0)

        # 6. User A fetches the trip via API -> Success with full itinerary
        res_a = self.client.get(f"/api/trips/{trip_id}", headers={"Authorization": f"Bearer {token_a}"})
        self.assertEqual(res_a.status_code, 200)
        data_a = res_a.json()
        self.assertEqual(data_a["trip_id"], trip_id)
        self.assertEqual(len(data_a["itinerary"]), 1)
        self.assertEqual(data_a["itinerary"][0]["activities"][0]["title"], "Arrival & City Center Check-in")

        # 7. User A lists their trips -> Trip appears in list
        my_trips = self.client.get("/api/auth/my-trips", headers={"Authorization": f"Bearer {token_a}"})
        self.assertEqual(my_trips.status_code, 200)
        trip_ids = [t["id"] for t in my_trips.json().get("trips", [])]
        self.assertIn(trip_id, trip_ids)

        # 8. User B attempts to access User A's trip -> MUST BE 404 (User Isolation!)
        res_b = self.client.get(f"/api/trips/{trip_id}", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(res_b.status_code, 404, "User B should not have access to User A's trip!")

        # 9. Guest attempts to access User A's private trip -> MUST BE 404
        res_guest = self.client.get(f"/api/trips/{trip_id}")
        self.assertEqual(res_guest.status_code, 404, "Guest should not have access to User A's private trip!")

        # 10. User B attempts to delete User A's trip -> MUST BE 404
        del_b = self.client.delete(f"/api/trips/{trip_id}", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(del_b.status_code, 404, "User B should not be able to delete User A's trip!")

        # 11. User A deletes their own trip -> Success
        del_a = self.client.delete(f"/api/trips/{trip_id}", headers={"Authorization": f"Bearer {token_a}"})
        self.assertEqual(del_a.status_code, 200)
        self.assertEqual(del_a.json().get("status"), "success")

        # 12. Confirm trip is deleted from database
        del_check = self.client.get(f"/api/trips/{trip_id}", headers={"Authorization": f"Bearer {token_a}"})
        self.assertEqual(del_check.status_code, 404)


if __name__ == "__main__":
    unittest.main()
