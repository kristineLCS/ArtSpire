from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io



# REGISTRATION
class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_user_valid_data(self):
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_user_passwords_dont_match(self):
        response = self.client.post(self.register_url, {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password1': 'Testpass123!',
            'password2': 'Mismatch123!'
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', "The two password fields didn’t match.")
        self.assertFalse(User.objects.filter(username='newuser2').exists())

    def test_register_user_duplicate_username(self):
        User.objects.create_user(username='duplicate', email='dup@example.com', password='pass12345')
        response = self.client.post(self.register_url, {
            'username': 'duplicate',
            'email': 'other@example.com',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!'
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')



# LOGIN
class UserLoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(username='loginuser', email='login@example.com', password='testpass123')

    def test_login_with_valid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after login
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")
        self.assertFalse('_auth_user_id' in self.client.session)



# PASSWORD RESET
class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.reset_url = reverse('password_reset')
        self.reset_done_url = reverse('password_reset_done')
        self.reset_confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': 'dummy', 'token': 'dummy'})
        self.reset_complete_url = reverse('password_reset_complete')

    def test_password_reset_valid_email(self):
        response = self.client.post(self.reset_url, {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect to the password reset done page
        self.assertRedirects(response, self.reset_done_url)

    def test_password_reset_invalid_email(self):
        response = self.client.post(self.reset_url, {
            'email': 'nonexistent@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.reset_done_url)

    def test_password_reset_confirm_valid_token(self):
        # Create a password reset token
        response = self.client.post(self.reset_url, {
            'email': 'test@example.com'
        })
        token = response.context['token']

        confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': 'dummy', 'token': token})
        

# PROFILE UPDATE
class ProfileUpdateTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.url = reverse('profile')

    @staticmethod
    def get_test_image():
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(file, 'JPEG')
        file.name = 'test.jpg'
        file.seek(0)
        return file

    def test_get_profile_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

def test_clear_profile_picture(self):
    # Upload a valid image first
    image_file = self.get_test_image()
    image = SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")

    self.client.post(self.url, {
        'username': 'testuser',
        'email': 'test@example.com',
        'image': image
    })

    self.user.refresh_from_db()
    self.assertTrue(self.user.profile.image.public_id)

    response = self.client.post(self.url, {
        'username': 'testuser',
        'email': 'test@example.com',
        'image-clear': 'on'
    })

    self.user.refresh_from_db()
    self.assertEqual(self.user.profile.image.name, '')
