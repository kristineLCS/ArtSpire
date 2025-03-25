from django.urls import path
from . import views
from .views import (
    animal_prompts, 
    character_prompts, 
    space_prompts, 
    nature_prompts, 
    emotions_prompts, 
    food_prompts, 
    fantasy_prompts, 
    worlds_prompts, 
    abstract_prompts, 
    alternate_prompts, 
    whimsical_prompts, 
    specific_prompts
)

urlpatterns = [
    path('animal/', animal_prompts, name='animal_prompts'),
    path('character/', character_prompts, name='character_prompts'),
    path('space/', space_prompts, name='space_prompts'),
    path('nature/', nature_prompts, name='nature_prompts'),
    path('emotions/', emotions_prompts, name='emotions_prompts'),
    path('food/', food_prompts, name='food_prompts'),
    path('fantasy/', fantasy_prompts, name='fantasy_prompts'),
    path('worlds/', worlds_prompts, name='worlds_prompts'),
    path('abstract/', abstract_prompts, name='abstract_prompts'),
    path('alternate/', alternate_prompts, name='alternate_prompts'),
    path('whimsical/', whimsical_prompts, name='whimsical_prompts'),
    path('specific/', specific_prompts, name='specific_prompts'),

]