from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),

    # Main Flow: Parse → Preview → Save
    path('input-recipe/', views.input_recipe, name='input_recipe'),  
    path('preview/', views.save_parsed_recipe, name='save_parsed_recipe'),  # Preview scaled ingredients
    path('save-final/', views.finalize_recipe_save, name='finalize_recipe_save'),  # Final save to DB
    path('toggle-fractions/', views.toggle_fractions_view, name='toggle_fractions'),

    # My Recipes & Management (requires login)
    path('my-recipes/', views.my_recipes, name='my_recipes'),
    path('add-recipe/', views.add_recipe, name='add_recipe'),
    path('edit-recipe/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('delete-recipe/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
]
