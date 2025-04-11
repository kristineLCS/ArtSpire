from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from homepage.models import Post
from cloudinary.uploader import destroy
from django.core import mail


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'The account {username} was created successfully, now you can login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    posts = Post.objects.filter(author=user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()

            # Check if "Clear current image" was selected
            if 'clear_image' in request.POST:
                if p_form.instance.image:
                    public_id = p_form.instance.image.public_id
                    destroy(public_id)  # Deletes from Cloudinary
                    p_form.instance.image = None
                p_form.instance.image = None

            p_form.save()

            messages.success(request, 'Your account has been updated')
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
