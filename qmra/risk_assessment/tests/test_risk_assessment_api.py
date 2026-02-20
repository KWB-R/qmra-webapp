"""test get, create, update, delete requests"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


class SourceInflowFitApiTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="alice", password="secret123")
        self.url = reverse("source-inflow-fit")

    def _upload(self, pathogen: str, csv_text: str):
        self.client.force_login(self.user)
        f = SimpleUploadedFile("sample.csv", csv_text.encode("utf-8"), content_type="text/csv")
        return self.client.post(self.url, {"pathogen": pathogen, "file": f})

    def test_fit_source_pathogen_distribution_success(self):
        csv_text = "Rotavirus\n1\n2\n3\n8\n9\n18\n"
        response = self._upload("Rotavirus", csv_text)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["pathogen"], "Rotavirus")
        self.assertIn("q025", payload)
        self.assertIn("q975", payload)
        self.assertIn("histogram", payload)
        self.assertGreaterEqual(payload["q975"], payload["q025"])

    def test_fit_source_pathogen_distribution_rejects_invalid_column(self):
        csv_text = "WrongColumn\n1\n2\n3\n4\n5\n"
        response = self._upload("Rotavirus", csv_text)

        self.assertEqual(response.status_code, 422)
        self.assertIn("column named", response.json()["error"])

    def test_fit_source_pathogen_distribution_rejects_non_integer_values(self):
        csv_text = "Rotavirus\n1.2\n2\n3\n4\n5\n"
        response = self._upload("Rotavirus", csv_text)

        self.assertEqual(response.status_code, 422)
        self.assertIn("integers", response.json()["error"])

    def test_fit_source_pathogen_distribution_requires_authentication(self):
        f = SimpleUploadedFile("sample.csv", b"Rotavirus\n1\n2\n3\n4\n5\n", content_type="text/csv")
        response = self.client.post(self.url, {"pathogen": "Rotavirus", "file": f})

        self.assertEqual(response.status_code, 302)
