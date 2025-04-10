from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Feedback
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
        self.assertEqual(str(self.post), 'Test Post')


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

        self.assertEqual(self.post.title, 'Test Post')

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
        response = self.client.get(reverse('report-post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PostReportForm)  # Ensure the form is present

        response = self.client.post(reverse('report-post', args=[self.post.id]), {
            'category': 'spam',  # Example category
            'description': 'Inappropriate content'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post-detail', kwargs={'pk': self.post.id}))


class GuestPostTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post_create_url = reverse('post-create')
        self.post_update_url = reverse('post-update', kwargs={'pk': 1})
        self.post_delete_url = reverse('post-delete', kwargs={'pk': 1})

    def test_guest_post_create(self):
        response = self.client.get(self.post_create_url)
        self.assertRedirects(response, '/login/?next=/post/new/')

    def test_guest_post_update(self):
        post = Post.objects.create(author=self.user, title="Test Post", content="Some content")
        url = reverse('post-update', kwargs={'pk': post.pk})
        response = self.client.get(url)
        self.assertRedirects(response, f'/login/?next={url}')

    def test_guest_post_delete(self):
        post = Post.objects.create(author=self.user, title="Test Post", content="Some content")
        url = reverse('post-delete', kwargs={'pk': post.pk})
        response = self.client.get(url)
        self.assertRedirects(response, f'/login/?next={url}')

        self.assertRedirects(response, f'/login/?next={url}')



class PostUpdatePermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        self.post = Post.objects.create(author=self.user, title="Test Post", content="Some content")

    def test_author_can_update_post(self):
        url = reverse('post-update', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {'title': 'Updated title', 'content': 'Updated content'})
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated title')

    def test_other_user_cannot_update_post(self):
        self.client.logout()
        self.client.login(username='otheruser', password='12345')
        url = reverse('post-update', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_author_can_delete_post(self):
        url = reverse('post-delete', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_other_user_cannot_delete_post(self):
        self.client.logout()
        self.client.login(username='otheruser', password='12345')
        url = reverse('post-delete', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)


class PostLikeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.post = Post.objects.create(author=self.user, title="Test Post", content="Some content")

    def test_like_post(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('post_like', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertIn(self.user, self.post.likes.all())

        self.assertRedirects(response, reverse('post-detail', kwargs={'pk': self.post.pk}))


class PostCommentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.post = Post.objects.create(author=self.user, title="Test Post", content="Some content")

    def test_comment_on_post(self):
        self.assertEqual(self.post.comments.count(), 0)

        response = self.client.post(reverse('post-comment', kwargs={'pk': self.post.pk}), {
            'body': 'This is a test comment'
        })

        self.assertEqual(response.status_code, 200)

        self.post.refresh_from_db()

        self.assertEqual(self.post.comments.count(), 1)


class FeedbackTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.home_url = reverse('blog-home')

    def test_authenticated_user_can_submit_feedback(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.home_url, {
            'subject': 'Site Feedback',
            'message': 'Loving the platform!',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Feedback.objects.count(), 1)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.subject, 'Site Feedback')
        self.assertEqual(feedback.message, 'Loving the platform!')
        self.assertEqual(feedback.user, self.user)

    def test_authenticated_user_submits_invalid_feedback(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.home_url, {
            'subject': '',  # Missing required field
            'message': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'subject', 'This field is required.')
        self.assertFormError(response, 'form', 'message', 'This field is required.')
        self.assertEqual(Feedback.objects.count(), 0)

    def test_guest_cannot_submit_feedback(self):
        response = self.client.post(self.home_url, {
            'subject': 'Trying as guest',
            'message': 'This should not go through.',
        })

        # Should redirect to login page
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(Feedback.objects.count(), 0)