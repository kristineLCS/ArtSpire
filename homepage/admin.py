from django.contrib import admin
from .models import Post, Comment, Feedback, PostReport

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Feedback)
@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reporter', 'category', 'created_at', 'status')
    list_filter = ('category', 'created_at')
    search_fields = ('post__title', 'reporter__username')
