from django.contrib import admin
from .models import Recipe, Ingredient

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1

class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit', 'note', 'recipe')

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)