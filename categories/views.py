from django.shortcuts import render

# Create your views here.
def animal_prompts(request):
    return render(request, 'blog/category-animal.html')

def character_prompts(request):
    return render(request, 'blog/category-character.html')

def space_prompts(request):
    return render(request, 'blog/category-space.html')

def nature_prompts(request):
    return render(request, 'blog/category-nature.html')

def emotions_prompts(request):
    return render(request, 'blog/category-emotions.html')

def food_prompts(request):
    return render(request, 'blog/category-food.html')

def fantasy_prompts(request):
    return render(request, 'blog/category-fantasy.html')

def worlds_prompts(request):
    return render(request, 'blog/category-worlds.html')

def abstract_prompts(request):
    return render(request, 'blog/category-abstract.html')

def alternate_prompts(request):
    return render(request, 'blog/category-alternate.html')

def whimsical_prompts(request):
    return render(request, 'blog/category-whimsical.html')

def specific_prompts(request):
    return render(request, 'blog/category-specific.html')