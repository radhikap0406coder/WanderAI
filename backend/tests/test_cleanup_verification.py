import sys
import uuid
import json
import unittest

sys.path.insert(0, 'backend')
from fastapi.testclient import TestClient
from app.main import app


class TestWanderAICleanup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_removed_analytics_endpoints_return_404(self):
        endpoints = [
            '/api/analytics/overview',
            '/api/analytics/destinations',
            '/api/analytics/budget',
            '/api/analytics/travelers',
            '/api/analytics/interests',
            '/api/analytics/itineraries',
            '/api/analytics/trends',
            '/api/analytics/export/csv',
            '/api/trips/test-id/analysis'
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 404, f"Expected 404 for removed endpoint {ep}, got {res.status_code}")

    def test_02_removed_analytics_files_return_404(self):
        for f in ['/analytics.html', '/analytics.js']:
            res = self.client.get(f)
            self.assertEqual(res.status_code, 404, f"Expected 404 for removed file {f}, got {res.status_code}")

    def test_03_index_html_has_no_map_or_analytics_or_quality(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        body = res.text
        self.assertNotIn('leaflet', body.lower(), "Found Leaflet in index.html")
        self.assertNotIn('analytics.html', body, "Found analytics.html in index.html")
        self.assertNotIn('data-tab="tab-map"', body, "Found tab-map in index.html")
        self.assertNotIn('data-tab="tab-analysis"', body, "Found tab-analysis in index.html")
        self.assertNotIn('id="tab-map"', body, "Found id=tab-map in index.html")
        self.assertNotIn('id="tab-analysis"', body, "Found id=tab-analysis in index.html")
        self.assertNotIn('dossier-quality-badge', body, "Found dossier-quality-badge in index.html")

    def test_04_app_js_has_no_map_or_analysis_functions(self):
        res = self.client.get('/app.js')
        self.assertEqual(res.status_code, 200)
        js = res.text
        self.assertNotIn('function renderMap', js, "Found renderMap in app.js")
        self.assertNotIn('function renderAnalysisReport', js, "Found renderAnalysisReport in app.js")
        self.assertNotIn('filterMapByDay', js, "Found filterMapByDay in app.js")
        self.assertNotIn('mapInstance', js, "Found mapInstance in app.js")

    def test_05_style_css_has_no_map_or_analysis_styles(self):
        res = self.client.get('/style.css')
        self.assertEqual(res.status_code, 200)
        css = res.text
        self.assertNotIn('.map-panel', css, "Found .map-panel in style.css")
        self.assertNotIn('.analysis-container', css, "Found .analysis-container in style.css")

    def test_06_health_endpoint(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get('status'), 'online')

    def test_07_user_registration_and_login(self):
        uid = uuid.uuid4().hex[:6]
        email = f'traveler_{uid}@wanderai.test'
        password = 'SuperSecurePassword123!'
        name = f'Traveler {uid}'

        # Register
        res = self.client.post('/api/auth/register', json={
            'full_name': name,
            'email': email,
            'password': password
        })
        self.assertEqual(res.status_code, 200, res.text)
        reg_data = res.json()
        token = reg_data['access_token']
        self.assertEqual(reg_data['user']['email'], email)

        # Login
        res = self.client.post('/api/auth/login', json={
            'email': email,
            'password': password
        })
        self.assertEqual(res.status_code, 200)

        # Wrong password
        res = self.client.post('/api/auth/login', json={
            'email': email,
            'password': 'WrongPassword123'
        })
        self.assertEqual(res.status_code, 401)

        # /api/auth/me
        res = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['email'], email)

    def test_08_saved_trips_endpoints(self):
        res = self.client.get('/api/trips')
        self.assertEqual(res.status_code, 200)
        self.assertIn('trips', res.json())

    def test_09_markdown_export(self):
        res = self.client.post('/api/export/markdown', json={
            'destination': 'Jaipur, India',
            'origin': 'Indore, India',
            'duration_days': 5,
            'currency': 'INR',
            'travelers_count': 4,
            'budget_breakdown': {'total_budget': 25000, 'estimated_total_cost': 29500}
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('# Travel Itinerary', res.text)

    def test_10_chat_assistant(self):
        res = self.client.post('/api/chat', json={
            'message': 'What are the best street foods in Jaipur?',
            'trip_context': {'destination': 'Jaipur, India', 'currency': 'INR'}
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('reply', res.json())

    def test_11_plan_trip_generation_and_persistence(self):
        plan_req = {
            'origin': 'Indore, India',
            'destination': 'Jaipur, India',
            'duration_days': 5,
            'budget_total': 25000.0,
            'currency': 'INR',
            'travelers_count': 4,
            'traveler_type': 'Friends',
            'provider': 'mock'
        }
        res = self.client.post('/api/plan-trip', json=plan_req)
        self.assertEqual(res.status_code, 200, res.text)
        trip_data = res.json()
        self.assertIn('itinerary', trip_data)
        self.assertEqual(len(trip_data['itinerary']), 5)
        self.assertEqual(trip_data['budget_breakdown']['total_budget'], 25000.0)
        self.assertIn('emergency_contacts', trip_data)
        self.assertGreater(len(trip_data['emergency_contacts']), 0)

        trip_id = trip_data.get('id') or trip_data.get('trip_id')
        self.assertIsNotNone(trip_id)

        # Retrieve saved trip
        res = self.client.get(f'/api/trips/{trip_id}')
        self.assertEqual(res.status_code, 200)
        retrieved = res.json()
        self.assertEqual(retrieved.get('id') or retrieved.get('trip_id'), trip_id)
        self.assertIn('emergency_contacts', retrieved)
        self.assertGreater(len(retrieved['emergency_contacts']), 0)


if __name__ == '__main__':
    unittest.main()

