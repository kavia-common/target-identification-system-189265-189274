from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from .models import Target, Source, Indicator, Association


class HealthTests(APITestCase):
    def test_health(self):
        url = reverse("Health")  # Make sure the URL is named
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})


class APICRUDTests(APITestCase):
    def setUp(self):
        self.source = Source.objects.create(name="SRC1", type="osint", url="https://src1.example.com")
        self.target = Target.objects.create(
            name="Target A", description="First", status="new", priority=5, tags="alpha,beta", confidence=0.6
        )
        self.ind1 = Indicator.objects.create(type="keyword", value="secret", score=0.7, source=self.source)
        self.ind2 = Indicator.objects.create(type="pattern", value=".*abc.*", score=0.4, source=self.source)
        self.assoc1 = Association.objects.create(target=self.target, indicator=self.ind1, weight=0.8, rationale="r", analyst_notes="n")
        self.assoc2 = Association.objects.create(target=self.target, indicator=self.ind2, weight=0.3, rationale="r2", analyst_notes="n2")

    def test_sources_crud(self):
        # list
        resp = self.client.get("/api/sources/")
        self.assertEqual(resp.status_code, 200)
        # create
        payload = {"name": "SRC2", "type": "humint", "url": "https://src2.example.com", "metadata": {"k": "v"}}
        resp = self.client.post("/api/sources/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        sid = resp.data["id"]
        # retrieve
        resp = self.client.get(f"/api/sources/{sid}/")
        self.assertEqual(resp.status_code, 200)
        # update
        resp = self.client.patch(f"/api/sources/{sid}/", {"type": "other"}, format="json")
        self.assertEqual(resp.status_code, 200)
        # delete
        resp = self.client.delete(f"/api/sources/{sid}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_targets_crud(self):
        # create
        payload = {"name": "Target B", "description": "Second", "status": "under_review", "priority": 2, "tags": "x,y", "confidence": 0.2}
        resp = self.client.post("/api/targets/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        tid = resp.data["id"]
        # retrieve and list
        self.assertEqual(self.client.get(f"/api/targets/{tid}/").status_code, 200)
        self.assertEqual(self.client.get("/api/targets/").status_code, 200)
        # update
        resp = self.client.patch(f"/api/targets/{tid}/", {"priority": 10}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["priority"], 10)
        # delete
        resp = self.client.delete(f"/api/targets/{tid}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_indicators_crud(self):
        payload = {"type": "feature", "value": "v1", "score": 0.9, "source": self.source.id}
        resp = self.client.post("/api/indicators/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        iid = resp.data["id"]
        self.assertEqual(self.client.get(f"/api/indicators/{iid}/").status_code, 200)
        self.assertEqual(self.client.patch(f"/api/indicators/{iid}/", {"score": 0.5}, format="json").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/indicators/{iid}/").status_code, status.HTTP_204_NO_CONTENT)

    def test_associations_crud(self):
        payload = {"target": self.target.id, "indicator": self.ind1.id, "weight": 0.4, "rationale": "r", "analyst_notes": "n"}
        resp = self.client.post("/api/associations/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        aid = resp.data["id"]
        self.assertIn("target_name", resp.data)
        self.assertEqual(self.client.get(f"/api/associations/{aid}/").status_code, 200)
        self.assertEqual(self.client.patch(f"/api/associations/{aid}/", {"weight": 0.6}, format="json").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/associations/{aid}/").status_code, status.HTTP_204_NO_CONTENT)

    def test_filters_and_search(self):
        # search targets by name
        resp = self.client.get("/api/targets/?search=Target")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data["count"], 1)
        # filter by status, range and ordering
        resp = self.client.get("/api/targets/?status=new&priority_min=1&confidence_max=0.7&ordering=-priority")
        self.assertEqual(resp.status_code, 200)
        # indicators by filter
        resp = self.client.get(f"/api/indicators/?type=keyword&source={self.source.id}&score_min=0.5")
        self.assertEqual(resp.status_code, 200)

    def test_score_endpoint(self):
        resp = self.client.get(f"/api/targets/{self.target.id}/score/")
        self.assertEqual(resp.status_code, 200)
        # expected = 0.7*0.8 + 0.4*0.3 = 0.56 + 0.12 = 0.68
        self.assertAlmostEqual(resp.data["score"], 0.68, places=5)

    def test_promote_endpoint(self):
        resp = self.client.post(f"/api/targets/{self.target.id}/promote/", {"status": "confirmed"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "confirmed")
        # invalid
        resp = self.client.post(f"/api/targets/{self.target.id}/promote/", {"status": "invalid"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
