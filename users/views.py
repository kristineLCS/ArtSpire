from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from homepage.models import Post

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST) #UserRegisterForm instead of UserCreationForm
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'The account {username} was created successfully, now you can login.')
            return redirect('login')
    else:
        form = UserRegisterForm() #UserRegisterForm instead of UserCreationForm
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    posts = Post.objects.filter(author=user)  # Filter posts by the 'author' field

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            
            messages.success(request, f'Your account has been updated') #Changes here
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user': user,
        'posts': posts,
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)