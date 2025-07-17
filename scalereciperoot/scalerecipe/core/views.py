from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json

from .utils.parsers import parse_ingredient_line, parse_ingredients, parse_ingredients_text, parse_fraction_string
from .utils.scaler import scale_parsed_ingredients, convert_units, scale_ingredients_in_session, scale_ingredients
from .utils.formats import format_fraction, format_quantity

from .forms import RecipeForm
from .models import Recipe, Ingredient
from fractions import Fraction


def index(request):
    desired_servings = request.GET.get('servings')
    rounding_enabled = request.GET.get('round') == 'on'

    recipes = Recipe.objects.prefetch_related('ingredients').all()
    scaled_data = []
    for recipe in recipes:
        scaled_ingredients = scale_ingredients(recipe, desired_servings, rounding_enabled)
        scaled_data.append({
            'name': recipe.name,
            'original_servings': recipe.servings,
            'scaled_ingredients': scaled_ingredients
        })

    return render(request, 'core/index.html', {
        'scaled_data': scaled_data,
        'desired_servings': desired_servings,
        'rounding_enabled': rounding_enabled
    })

@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(user=request.user)
    return render(request, 'core/my_recipes.html', {'recipes': recipes})

@login_required
def add_recipe(request):
    form = RecipeForm(request.POST or None)
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.user = request.user
        recipe.save()
        return redirect('my_recipes')
    return render(request, 'core/recipe_form.html', {'form': form})
@login_required
def delete_recipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id, user=request.user)
    if request.method == 'POST':
        recipe.delete()
        return redirect('my_recipes')
    return render(request, 'core/confirm_delete.html', {'recipe': recipe})

@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = recipe.ingredients.all().order_by('id')
    
    if request.method == 'POST':
        action = request.POST.get("action", "")
        
        if action == "revert":
            # Reset to original servings
            recipe.servings = recipe.original_servings
            recipe.save()
            return redirect('edit_recipe', recipe_id=recipe.id)

        # Update basic recipe fields
        recipe.name = request.POST.get("recipe_name", recipe.name)
        recipe.original_servings = int(request.POST.get("original_servings", recipe.original_servings))
        recipe.servings = int(request.POST.get("desired_servings", recipe.servings))
        recipe.save()

        # Gather all ingredient inputs
        parsed_ingredients = []
        index = 0
        while f"name_{index}" in request.POST:
            name = request.POST.get(f"name_{index}", "").strip()
            quantity = request.POST.get(f"quantity_{index}", "").strip()
            unit = request.POST.get(f"unit_{index}", "").strip()
            notes = request.POST.get(f"notes_{index}", "").strip()
            if name:  # Skip empty rows
                parsed_ingredients.append({
                    'name': name,
                    'quantity': quantity,
                    'unit': unit,
                    'notes': notes,
                })
            index += 1

        # Clear and re-save ingredients
        recipe.ingredients.all().delete()
        for ing in parsed_ingredients:
            Ingredient.objects.create(
                recipe=recipe,
                name=ing['name'],
                quantity=ing['quantity'],
                unit=ing['unit'],
                notes=ing['notes'],
            )

        return redirect('my_recipes')

    # Initial GET render
    parsed_ingredients = list(recipe.ingredients.all())
    return render(request, 'core/edit_recipe.html', {
        'recipe': recipe,
        'parsed_ingredients': parsed_ingredients,
    })

@login_required
def input_recipe(request):
    ingredients_text = ''
    parsed_ingredients = []
    recipe_name = ''
    original_servings = ''
    desired_servings = ''
    use_nice_fractions = request.session.get('use_nice_fractions', True)

    if request.method == 'POST':
        action = request.POST.get('action')

        recipe_name = request.POST.get('name', '')
        original_servings = request.POST.get('original_servings', '')
        desired_servings = request.POST.get('desired_servings', '')
        ingredients_text = request.POST.get('ingredients', '')

        # Toggle nice fractions
        if 'toggle_nice' in request.POST:
            use_nice_fractions = not use_nice_fractions
            request.session['use_nice_fractions'] = use_nice_fractions

        if action in ['parse', 'save']:
            try:
                original = float(original_servings)
                desired = float(desired_servings)
            except ValueError:
                original = desired = 1

            parsed = parse_ingredients(ingredients_text)
            promote = desired > original

            # Scale ingredients
            parsed_ingredients = scale_parsed_ingredients(
                parsed, desired, original,
                promote_units=promote,
                rounding_enabled=use_nice_fractions
            )

            for ing in parsed_ingredients:
                if ing['quantity'] != '':
                    ing['quantity'] = format_fraction(ing['quantity']) if use_nice_fractions else round(ing['quantity'], 2)

            # Save to session
            request.session['recipe_data'] = {
                'name': recipe_name,
                'original_servings': original_servings,
                'desired_servings': desired_servings,
                'ingredients_text': ingredients_text,
            }
            request.session['parsed_ingredients'] = parsed_ingredients

            if action == 'save':
                return redirect('finalize_recipe_save')

    context = {
        'recipe_name': recipe_name,
        'original_servings': original_servings,
        'desired_servings': desired_servings,
        'ingredients_text': ingredients_text,
        'parsed_ingredients': parsed_ingredients,
        'use_nice_fractions': use_nice_fractions,
    }
    print(context)
    return render(request, 'core/input_recipe.html', context)

def save_parsed_recipe(request):
    if request.method == "POST":
        recipe_name = request.POST.get("recipe_name")
        original_servings = request.POST.get("original_servings")
        desired_servings = request.POST.get("desired_servings")
        ingredients_text = request.POST.get("ingredients", "")

        lines = ingredients_text.strip().split("\n")
        parsed_ingredients = [parse_ingredient_line(line) for line in lines if line.strip()]

        # Temporarily hold parsed data in session to preview before saving
        request.session["recipe_data"] = {
            "name": recipe_name,
            "original_servings": original_servings,
            "desired_servings": desired_servings,
        }
        request.session["parsed_ingredients"] = parsed_ingredients

        return render(request, "core/preview_scaled_recipe.html", {
            "recipe_name": recipe_name,
            "original_servings": original_servings,
            "desired_servings": desired_servings,
            "parsed_ingredients": parsed_ingredients,
        })
    return redirect("index")

@csrf_exempt
def toggle_fractions_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        use_nice = data.get("use_nice_fractions", False)

        request.session["nice_fractions"] = use_nice  # 🔁 use consistent key

        parsed_ingredients = request.session.get("parsed_ingredients", [])
        recipe_data = request.session.get("recipe_data", {})
        original_servings = float(recipe_data.get("original_servings", 1))
        desired_servings = float(recipe_data.get("desired_servings", 1))

        # Reverse fractional string to float quantity
        for ing in parsed_ingredients:
            qty = ing.get("quantity", "")
            try:
                if isinstance(qty, str):
                    parts = qty.strip().split()
                    if len(parts) == 2:  # e.g. "1 1/2"
                        whole, frac = parts
                        qty = float(whole) + float(Fraction(frac))
                    else:
                        qty = float(Fraction(qty))
                else:
                    qty = float(qty)
            except Exception:
                qty = 0
            ing["quantity"] = qty  # store as float first

        # Reformat float to either fraction or decimal
        for ing in parsed_ingredients:
            if ing["quantity"] != "":
                ing["quantity"] = (
                    format_fraction(ing["quantity"]) if use_nice else round(ing["quantity"], 2)
                )

        request.session["parsed_ingredients"] = parsed_ingredients

        return JsonResponse({"scaled_ingredients": parsed_ingredients})

@login_required
def finalize_recipe_save(request):
    recipe_data = request.session.get('recipe_data')
    parsed_ingredients = request.session.get('parsed_ingredients')

    if not recipe_data or not parsed_ingredients:
        return redirect('input_recipe')  # fallback if session data missing

    # Create and save the recipe
    recipe = Recipe.objects.create(
        user=request.user,
        name=recipe_data['name'],
        original_servings=recipe_data['original_servings'],
        servings=recipe_data['desired_servings']
    )

    # Save each ingredient
    for ing in parsed_ingredients:
        quantity_raw = ing.get('quantity', '')
        quantity_float = parse_fraction_string(quantity_raw)

        Ingredient.objects.create(
            recipe=recipe,
            name=ing.get('name', ''),
            quantity=quantity_raw,
            quantity_float=quantity_float,
            unit=ing.get('unit', '')
        )

    # Clear the session if you want to start fresh
    del request.session['recipe_data']
    del request.session['parsed_ingredients']

    return redirect('my_recipes')
    
    