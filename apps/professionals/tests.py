import uuid

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment

from .models import Professional


class ProfessionalAPITestCase(APITestCase):
    def setUp(self):
        from rest_framework_simplejwt.tokens import RefreshToken

        self.user = User.objects.create_user(username="testuser", password="password")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.list_url = reverse("professional-list")
        self.valid_payload = {
            "social_name": "Dr. House",
            "profession": "Diagnostician",
            "address": "Princeton-Plainsboro Teaching Hospital",
            "contact": "18005550199",
        }

    def test_create_professional_success(self):
        response = self.client.post(self.list_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Professional.objects.count(), 1)
        self.assertEqual(Professional.objects.get().social_name, "Dr. House")

    def test_create_professional_invalid_name(self):
        payload = self.valid_payload.copy()
        payload["social_name"] = "A"
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("social_name", response.data["message"])
        self.assertEqual(Professional.objects.count(), 0)

    def test_create_professional_empty_contact(self):
        payload = self.valid_payload.copy()
        payload["contact"] = " "
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contact", response.data["message"])
        self.assertEqual(Professional.objects.count(), 0)

    def test_create_professional_missing_data(self):
        payload = {"social_name": "Dr. Silva"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profession", response.data["message"])

    def test_list_professionals(self):
        Professional.objects.create(**self.valid_payload)
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(
                response.data["results"]
                if "results" in response.data
                else response.data
            ),
            1,
        )

    def test_retrieve_professional(self):
        professional = Professional.objects.create(**self.valid_payload)
        url = reverse("professional-detail", args=[professional.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["social_name"], "Dr. House")

    def test_update_professional(self):
        professional = Professional.objects.create(**self.valid_payload)
        url = reverse("professional-detail", args=[professional.id])
        updated_payload = self.valid_payload.copy()
        updated_payload["social_name"] = "Dr. Gregory House"
        response = self.client.put(url, updated_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        professional.refresh_from_db()
        self.assertEqual(professional.social_name, "Dr. Gregory House")

    def test_delete_professional(self):
        professional = Professional.objects.create(**self.valid_payload)
        url = reverse("professional-detail", args=[professional.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Professional.objects.count(), 0)

    def test_unauthenticated_access(self):
        self.client.credentials()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_professional_duplicate_name(self):
        Professional.objects.create(**self.valid_payload)
        payload = self.valid_payload.copy()
        payload["contact"] = "+1-555-0000"
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("social_name", response.data["message"])

    def test_create_professional_duplicate_contact(self):
        Professional.objects.create(**self.valid_payload)
        payload = self.valid_payload.copy()
        payload["social_name"] = "Dr. Wilson"
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contact", response.data["message"])

    def test_retrieve_professional_not_found(self):
        url = reverse("professional-detail", args=[uuid.uuid4()])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "Profissional não encontrado(a).")
        self.assertEqual(response.data["code"], "NotFound")

    def test_create_professional_invalid_phone_format(self):
        payload = self.valid_payload.copy()
        payload["contact"] = "telefone-invalido"
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contact", response.data["message"])

    def test_create_professional_phone_cleaning_logic(self):
        payload = self.valid_payload.copy()
        payload["social_name"] = "Dr. Clean"
        payload["contact"] = "(11) 98888-7777"
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        professional = Professional.objects.get(social_name="Dr. Clean")
        self.assertEqual(professional.contact, "11988887777")

    def test_delete_professional_with_appointments_error(self):
        professional = Professional.objects.create(**self.valid_payload)
        from django.utils import timezone

        Appointment.objects.create(
            professional=professional, date=timezone.now() + timezone.timedelta(days=1)
        )
        url = reverse("professional-detail", args=[professional.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_key = "message" if "message" in response.data else "error"
        self.assertIn(
            "Não é possível remover este profissional",
            response.data.get(error_key, str(response.data)),
        )
