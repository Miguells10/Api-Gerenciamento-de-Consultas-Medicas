from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.appointments.models import Appointment

from .models import Professional


class ProfessionalAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")

        # Obter token JWT para o usuário
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Configurar o cliente para incluir o cabeçalho Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.list_url = reverse("professional-list")
        self.valid_payload = {
            "social_name": "Dr. House",
            "profession": "Diagnostician",
            "address": "Princeton-Plainsboro Teaching Hospital",
            "contact": "+1-800-555-0199",
        }

    def test_create_professional_success(self):
        """Test creating a professional with valid data."""
        response = self.client.post(self.list_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Professional.objects.count(), 1)
        self.assertEqual(Professional.objects.get().social_name, "Dr. House")

    def test_create_professional_invalid_name(self):
        """Test creating a professional with a short social_name."""
        payload = self.valid_payload.copy()
        payload["social_name"] = "A"  # Invalid, < 2 chars
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("social_name", response.data)
        self.assertEqual(Professional.objects.count(), 0)

    def test_create_professional_empty_contact(self):
        """Test creating a professional with an empty contact."""
        payload = self.valid_payload.copy()
        payload["contact"] = " "  # Invalid, empty after strip
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contact", response.data)
        self.assertEqual(Professional.objects.count(), 0)

    def test_create_professional_missing_data(self):
        """Test creating a professional with missing required fields."""
        payload = {"social_name": "Dr. Silva"}  # Missing profession, address, contact
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profession", response.data)

    def test_list_professionals(self):
        """Test listing professionals."""
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
        """Test retrieving a single professional."""
        professional = Professional.objects.create(**self.valid_payload)
        url = reverse("professional-detail", args=[professional.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["social_name"], "Dr. House")

    def test_update_professional(self):
        """Test updating a professional's data."""
        professional = Professional.objects.create(**self.valid_payload)
        url = reverse("professional-detail", args=[professional.id])
        updated_payload = self.valid_payload.copy()
        updated_payload["social_name"] = "Dr. Gregory House"
        response = self.client.put(url, updated_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        professional.refresh_from_db()
        self.assertEqual(professional.social_name, "Dr. Gregory House")

    def test_delete_professional(self):
        """Test deleting a professional."""
        professional = Professional.objects.create(**self.valid_payload)
        url = reverse("professional-detail", args=[professional.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Professional.objects.count(), 0)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot list professionals."""
        # Limpar as credenciais para este teste específico
        self.client.credentials()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_professional_duplicate_name(self):
        """Test that creating a professional with a duplicate social_name fails."""
        Professional.objects.create(**self.valid_payload)
        payload = self.valid_payload.copy()
        payload["contact"] = "+1-555-0000"  # Different contact, same name
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("social_name", response.data)

    def test_create_professional_duplicate_contact(self):
        """Test that creating a professional with a duplicate contact fails."""
        Professional.objects.create(**self.valid_payload)
        payload = self.valid_payload.copy()
        payload["social_name"] = "Dr. Wilson"  # Different name, same contact
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contact", response.data)

    def test_delete_professional_with_appointments_error(self):
        """Test custom error message when deleting a professional with appointments."""
        professional = Professional.objects.create(**self.valid_payload)
        from django.utils import timezone

        Appointment.objects.create(
            professional=professional, date=timezone.now() + timezone.timedelta(days=1)
        )
        url = reverse("professional-detail", args=[professional.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Não é possível remover este profissional pois "
            "ele possui consultas agendadas.",
        )
