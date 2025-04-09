from django import forms
from .models import Post, Comment, Feedback, PostReport

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment  # Link form to the Comment model
        fields = ["body"] # Only allow users to submit the 'body' field
        widgets = {
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Write a comment..."}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message']


class PostReportForm(forms.ModelForm):
    category = forms.ChoiceField(choices=PostReport.REPORT_CATEGORIES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta:
        model = PostReport
        fields = ['category', 'description']
