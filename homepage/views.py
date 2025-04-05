from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Post, Comment 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import openai
import os
from dotenv import load_dotenv, find_dotenv
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView,
    UpdateView,
    DeleteView,
)
from .forms import PostForm, CommentForm, FeedbackForm, PostReportForm
from django.contrib.auth.decorators import login_required
import json

_ = load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# load_dotenv(ENV_PATH)


openai.api_key = os.getenv('openai_key')

User = get_user_model()


def home(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit feedback.")
            return redirect('login')
        
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)  # Don’t save to DB yet
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('blog-home')
    else:
        form = FeedbackForm()

    context = {
        'form': form,
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']

    posts = Post.objects.filter(is_active=True)



class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return user.posts.order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)

        stuff = get_object_or_404(Post, id=self.kwargs['pk'])
        total_likes = stuff.total_likes()
        context["total_likes"] = total_likes
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'image']  # Make sure 'image' is here
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self): # Function to make sure logged in user can only edit their posts and not another user's post
        post = self.get_object()
        return self.request.user == post.author
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = "/" # redirecting the user back to the homepage after deleting a Post successfully


    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


@login_required
def LikeView(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))


@login_required
def post_comment(request, pk):

    if request.method == "POST":
        print("➡️ Received a POST request")  # Debugging: Check if the view is hit
        print("📩 Request POST Data:", request.POST)


        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)  # Don't save yet
            comment.post = post  # Associate with the post
            comment.name = request.user.username  # Assign the logged-in user's name
            comment.save()  # Now save the comment

            
            print("✅ Comment Saved Successfully:", comment.body)
            
            # Return JSON response for JavaScript to update UI dynamically
            return JsonResponse({
                "success": True,
                "comment_id": comment.id,  # Include comment ID for edit/delete buttons
                "name": comment.name,
                "date_added": comment.date_added.strftime("%d %b %Y, %H:%M"),
                "body": comment.body,
            })
        else:
            print("❌ Form Errors:", form.errors)  # Print form errors for debugging
            return JsonResponse({'success': False, 'error': 'Invalid form data'})

    print("⛔ Received a non-POST request")  # Debugging: If the request isn't POST
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
@csrf_exempt  # Or use a proper decorator
def delete_comment(request, comment_id):
    if request.method == "POST":
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            if comment.name != request.user.username:
                return JsonResponse({"success": False, "error": "You cannot delete this comment."})
            
            comment.delete()
            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})



@login_required
@csrf_exempt 
# same as def edit_comment
def update_comment(request, comment_id):
    if request.method == "POST":
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            if comment.name != request.user.username:
                return JsonResponse({"success": False, "error": "You cannot edit this comment."})
            
            data = json.loads(request.body)
            comment.body = data.get("body", "")
            comment.save()

            return JsonResponse({"success": True, "body": comment.body, "date_added": comment.date_added.strftime("%d %b %Y, %H:%M")})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def report_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.post = post
            report.save()
            messages.success(request, "Your report has been submitted. Thank you for keeping the community safe.")
            return redirect('post-detail', pk=pk)
    else:
        form = PostReportForm()

    return render(request, 'blog/report_post.html', {'form': form, 'post': post})

def daily_challenge(request, category):
    """ Renders category page without pre-loading a prompt. """
    return render(request, "blog/category_template.html", {"category": category})


def get_prompt(request):
    """Fetches a short and creative generated prompt when the button is clicked."""
    category = request.GET.get("category", "").strip()
    
    print(f" Raw category received: {category}")  # Debugging print

    # If category is empty or invalid, return an error
    if not category:
        return JsonResponse({"error": "No category received."}, status=400)

    # Normalize category names
    category_map = {
        "fantasy-mythology": "fantasy & mythology",
        "tiny-worlds": "tiny worlds",
        "abstract-surreal": "abstract / surreal",
        "alternate-universe": "alternate universe",
    }
    
    category = category_map.get(category, category)  # Convert if in map | Is a dictionary that maps certain category names like fantasy-mythology to a more readable format like fantasy & mythology
    print(f" Category after mapping: {category}")  # Debugging print

    # System instruction for GPT. Be STRICT and CONCISE.
    system_instruction = (
        "You are an expert art prompt generator. **Always generate prompts that match the given category**. "
        "Never include themes outside of the category. Be concise and creative  (no more than 30 words)."
        "Avoid repetition in phrasing of prompts whenever the generate prompt button is clicked. "
        "Do not use the same prompt opening when generating a prompt. "
        "Ensure each prompt is completely unique and inspiring."
    )

    # User message
    user_prompt = f"Generate a **brand-new, category-specific** art prompt for **{category.upper()}**."

    response = openai.chat.completions.create(
        model="gpt-4o-mini", 
        temperature=0.9,  # randomness
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
    )

    generated_prompt = response.choices[0].message.content
    return JsonResponse({"prompt": generated_prompt})
