from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    PostListView, 
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    LikeView,
    post_comment,
    delete_comment,
    update_comment
)

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('posts', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('comment/<int:comment_id>/edit/', update_comment, name='update-comment'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('like/<int:pk>', LikeView, name='post_like'),
    path("post/<int:pk>/comment/", post_comment, name="post-comment"),  
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete-comment'),
    path('comment/update/<int:comment_id>/', update_comment, name='comment-update'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/report/', views.report_post, name='report-post'),
    path("challenge/<str:category>/", views.daily_challenge, name="daily_challenge"),
    path("get_prompt/", views.get_prompt, name="get_prompt"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)