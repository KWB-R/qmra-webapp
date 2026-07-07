from django.test import TestCase
from django.urls import reverse

from qmra.user.models import User


class TestLoginView(TestCase):
    def test_successful_login_redirects_with_notice_flag(self):
        User.objects.create_user("test-user", "test-user@example.com", "password")

        response = self.client.post(
            reverse("login"),
            {"username": "test-user", "password": "password"},
        )

        self.assertRedirects(
            response,
            f"{reverse('index')}?isLogin=1",
            fetch_redirect_response=False,
        )
