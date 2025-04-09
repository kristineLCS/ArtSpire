from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post
from .forms import PostReportForm



class PostModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.post = Post.objects.create(
            author=cls.user,
            title='Test Post',
            content='This is a test post'
        )

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post')
        self.assertEqual(self.post.author.username, 'testuser')

    def test_post_str_method(self):
        self.assertEqual(str(self.post), 'Test Post')  # Adjust if __str__ uses a different format


class PostViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.post = Post.objects.create(author=self.user, title='Test Post', content='Some content')

    def test_post_list_view(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_create_post_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('post-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')

        response = self.client.post(reverse('post-create'), {
            'title': 'New title',
            'content': 'Hello World',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertTrue(Post.objects.filter(title='New title').exists())


    def test_post_detail_view(self):
        url = reverse('post-detail', args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
    

    def test_update_post_view(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('post-update', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')

        self.assertEqual(self.post.title, 'Test Post')  # Check the original

        response = self.client.post(url, {
            'title': 'Updated title',
            'content': 'Updated text',
        })
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertEqual(self.post.title, 'Updated title')

    def test_delete_post_view(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('post-delete', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_confirm_delete.html')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())



    def test_report_post(self):
        # First, get the report post form to ensure it's rendered correctly
        response = self.client.get(reverse('report-post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PostReportForm)  # Ensure the form is present

        # Now submit the form with valid data
        response = self.client.post(reverse('report-post', args=[self.post.id]), {
            'category': 'spam',  # Example category
            'description': 'Inappropriate content'
        })
        
        # Since the form submission is successful, it should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post-detail', kwargs={'pk': self.post.id}))


class GuestPostTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post_create_url = reverse('post-create')  # Update with your post create URL
        self.post_update_url = reverse('post-update', kwargs={'pk': 1})  # Replace with an actual post ID for testing
        self.post_delete_url = reverse('post-delete', kwargs={'pk': 1})  # Replace with an actual post ID for testing

    def test_anonymous_user_post_create(self):
        response = self.client.get(self.post_create_url)
        self.assertRedirects(response, '/login/?next=/post/create/')  # Adjust this based on your login URL

    def test_anonymous_user_post_update(self):
        post = Post.objects.create(author=self.user, title="Test Post", content="Some content")
        url = reverse('post-update', kwargs={'pk': post.pk})
        response = self.client.get(url)
        self.assertRedirects(response, f'/login/?next={url}')  # Redirect to login

    def test_anonymous_user_post_delete(self):
        post = Post.objects.create(author=self.user, title="Test Post", content="Some content")
        url = reverse('post-delete', kwargs={'pk': post.pk})
        response = self.client.get(url)
        self.assertRedirects(response, f'/login/?next={url}')  # Redirect to login

        self.assertRedirects(response, f'/login/?next={url}')  # Adjust based on your login URL



