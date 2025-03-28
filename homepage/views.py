from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Post
from django.http import JsonResponse
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
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from .models import ArtPrompt
import random


_ = load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# load_dotenv(ENV_PATH)


openai.api_key = os.getenv('openai_key')

User = get_user_model()


def home(request):
    context = {
       'posts': Post.objects.all() #The view is looping over 'posts'
    }
    return render(request, 'blog/home.html', context)

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect("post-list")
    else:
        form = PostForm()
    
    return render(request, "blog/post_form.html", {"form": form})

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

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

# def community(request):
#     return render(request, 'blog/community.html')

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

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        temperature=0.9,# randomness
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
    )

    generated_prompt = response["choices"][0]["message"]["content"]

    return JsonResponse({"prompt": generated_prompt})
