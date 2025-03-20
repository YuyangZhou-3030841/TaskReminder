from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, Task

class TaskSystemTest(TestCase):
    def setUp(self):
        # Initialising test clients and users
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone='+123456789012',
            password='testpass',
            region='Asia/Shanghai'
        )
        # Logging in test users
        self.client.login(username='testuser', password='testpass')
        # Create a test task
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task.',
            priority='medium',
            due_date=timezone.now() + timedelta(days=3),
            user=self.user
        )

    def test_home_view_status_and_template(self):
        """
        The test home page view returns status code 200 and is using the correct template.
        """
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'TaskSystemapp/home.html')

    def test_quick_add_task(self):
        """
        Test adding tasks quickly via AJAX, returning correct JSON data and deadlines.
        """
        url = reverse('quick_add_task')
        due_date = (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M")
        form_data = {
            'title': 'Quick Task',
            'due_date': due_date,
            'priority': 'high',
            'description': 'A quick added task',
        }
        response = self.client.post(url, form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('task_deadline', data)

    def test_detailed_add_task(self):
        """
        The test adds the task in detail via AJAX and returns the correct JSON data and deadline.
        """
        url = reverse('detailed_add_task')
        due_date = (timezone.now() + timedelta(days=6)).strftime("%Y-%m-%d %H:%M")
        form_data = {
            'title': 'Detailed Task',
            'due_date': due_date,
            'priority': 'low',
            'description': 'A detailed added task',
        }
        response = self.client.post(url, form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('task_deadline', data)

    def test_complete_task(self):
        """
        The test marks the task as complete and redirects back to the home page when the task status is updated.
        """
        url = reverse('complete_task', args=[self.task.id])
        response = self.client.get(url)
        # This view redirects back to the homepage
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_completed)

    def test_delete_task(self):
        """
        Test deleting a task, return JSON data after successful deletion, and make sure the task does not exist in the database.
        """
        url = reverse('delete_task', args=[self.task.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=self.task.id)

    def test_profile_view(self):
        """
        Test that the user profile view returns status code 200 with the correct template.
        """
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'TaskSystemapp/profile.html')

    def test_custom_login_view(self):
        """
        Test the login view and return an error message on incorrect credentials.
        """
        # Logging out the currently logged in user
        self.client.logout()
        url = reverse('login')
        # Submitting incorrect login information
        response = self.client.post(url, {'username': 'wrong', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect username or password")

    def test_register_view(self):
        """
        Test the registration view and jump to the login page after submitting the correct data.
        """
        self.client.logout()
        url = reverse('register')
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone': '+123456789099',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'region': 'Asia/Tokyo'
        }
        response = self.client.post(url, form_data)
        # Redirect to login page after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
