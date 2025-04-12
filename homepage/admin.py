from django.contrib import admin
from .models import Post, Comment, Feedback, PostReport, WeeklyChallenge
from .forms import WeeklyChallengeForm

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Feedback)
@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reporter', 'category', 'created_at', 'status')
    list_filter = ('category', 'created_at')
    search_fields = ('post__title', 'reporter__username')


class WeeklyChallengeAdmin(admin.ModelAdmin):
    form = WeeklyChallengeForm
    list_display = ('challenge_text', 'updated_at')

admin.site.register(WeeklyChallenge, WeeklyChallengeAdmin)
