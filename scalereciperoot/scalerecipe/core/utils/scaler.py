from .formats import format_fraction, format_quantity, format_decimal
from .parsers import parse_fraction_string
from fractions import Fraction


CONVERSION_MAP = [
    ('tsp', 'tbsp', 1 / 3),
    ('tbsp', 'cup', 1 / 16),
    ('cup', 'pint', 1 / 2),
    ('pint', 'quart', 1 / 2),
    ('quart', 'gallon', 1 / 4),
    ('g', 'kg', 1 / 1000),
    ('ml', 'l', 1 / 1000),
    ('pcs', 'dozen', 1 / 12),
    ('unit', 'dozen', 1 / 12),
]

UNITS = {u for pair in CONVERSION_MAP for u in pair[:2]}
UNITS_WITH_THRESHOLDS = {src: factor for src, tgt, factor in CONVERSION_MAP}


def scale_ingredients(recipe_or_data, desired_servings, original_servings=None, *, promote_units=False, rounding_enabled=False):
    try:
        desired_servings = float(desired_servings)
        if original_servings is None:
            original_servings = recipe_or_data.servings if hasattr(recipe_or_data, 'servings') else recipe_or_data.get('original_servings', 1)
        original_servings = float(original_servings)
        multiplier = desired_servings / original_servings
    except Exception:
        multiplier = 1

    if hasattr(recipe_or_data, 'ingredients'):
        ingredients = recipe_or_data.ingredients.all()
    elif isinstance(recipe_or_data, dict):
        ingredients = recipe_or_data.get('ingredients', [])
    elif isinstance(recipe_or_data, list):
        ingredients = recipe_or_data  # it's already a list of parsed ingredients
    else:
        ingredients = []

    parsed_ingredients = []
    for ing in ingredients:
        name = ing.name if hasattr(ing, 'name') else ing.get('name', '')
        unit = ing.unit if hasattr(ing, 'unit') else ing.get('unit', '')
        raw_quantity = ing.quantity if hasattr(ing, 'quantity') else ing.get('quantity', 0)

        try:
            # Use Fraction to safely parse both decimal and fractional strings
            quantity = float(Fraction(str(raw_quantity)))
        except (ValueError, ZeroDivisionError):
            quantity = 0  # Fallback if parsing fails

        parsed_ingredients.append({
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "note": ing.note if hasattr(ing, 'note') else ing.get('note', '')
        })

    return scale_parsed_ingredients(
        parsed_ingredients,
        desired_servings,
        original_servings,
        promote_units=promote_units,
        rounding_enabled=rounding_enabled
    )


def scale_parsed_ingredients(ingredients, desired, original, promote_units=False, rounding_enabled=False):
    scaled = []
    try:
        multiplier = float(desired) / float(original)
    except Exception:
        multiplier = 1

    for ing in ingredients:
        try:
            qty = float(Fraction(str(ing.get('quantity') or 0)))
        except Exception:
            qty = 0
        unit = ing.get('unit', '').lower()
        name = ing.get('name', '').strip()

        scaled_qty = qty * multiplier

        orig_amount, orig_unit = convert_units(qty, unit, rounding=rounding_enabled, promote=promote_units)
        scaled_amount, scaled_unit = convert_units(scaled_qty, unit, rounding=rounding_enabled, promote=promote_units)

        scaled.append({
            'name': name,
            'original_quantity': format_fraction(orig_amount) if rounding_enabled else round(orig_amount, 2),
            'original_unit': pluralize_unit(orig_unit, orig_amount),
            'scaled_quantity_fraction': format_fraction(scaled_amount),
            'scaled_quantity_decimal': format_decimal(scaled_amount),
            'scaled_quantity': format_fraction(scaled_amount) if rounding_enabled else round(scaled_amount, 2),
            'scaled_unit': pluralize_unit(scaled_unit, scaled_amount),
            'quantity': scaled_amount,
            'unit': scaled_unit,
            'note': ing.get('note', '')
        })

    return scaled


def convert_units(amount, unit, *, rounding=True, promote=True):
    """
    Promotes or demotes a unit if the amount crosses the conversion threshold.
    """
    if unit not in UNITS:
        return (round(amount, 2) if rounding else amount), unit

    for src, tgt, factor in CONVERSION_MAP:
        if promote:
            if src == unit and amount >= 1 / factor:
                new_amount = amount * factor  # E.g., 3 tbsp → 1.5 cups (1/16)
                return (round(new_amount, 2) if rounding else new_amount), tgt
        else:
            if tgt == unit and amount < 1:
                new_amount = amount / factor
                return (round(new_amount, 2) if rounding else new_amount), src

    return (round(amount, 2) if rounding else amount), unit


def singularize(unit):
    irregulars = {
        "units": "unit",
        "dozens": "dozen",
        "leaves": "leaf",
        "loaves": "loaf",
        "eggs": "egg",
        "tomatoes": "tomato",
        "potatoes": "potato",
    }

    if unit in irregulars:
        return irregulars[unit]

    if unit.endswith("ies"):
        return unit[:-3] + "y"
    elif unit.endswith("es") and unit[-3] in "sxz" or unit.endswith("ches") or unit.endswith("shes"):
        return unit[:-2]
    elif unit.endswith("s"):
        return unit[:-1]

    return unit


def pluralize_unit(unit, amount):
    uncountable_units = [
        "ml", "l", "tbsp", "tsp", "oz", "lb", "cm", "mm", "kg", "g", "mg"
    ]

    singular_unit = singularize(unit)

    if singular_unit in uncountable_units:
        return singular_unit
    if not unit:
        return ""
    if amount == 1:
        return singular_unit

    irregulars = {
        "unit": "units",
        "dozen": "dozens",
        "leaf": "leaves",
        "loaf": "loaves",
        "egg": "eggs",
        "tomato": "tomatoes",
        "potato": "potatoes",
    }

    if singular_unit in irregulars:
        return irregulars[singular_unit]

    if singular_unit.endswith("y") and singular_unit[-2] not in "aeiou":
        return singular_unit[:-1] + "ies"
    elif singular_unit.endswith(("ch", "s", "sh", "x", "z")):
        return singular_unit + "es"
    else:
        return singular_unit + "s"

def scale_ingredients_in_session(request, use_nice_fractions):
    session = request.session

    raw_ingredients = session.get("parsed_ingredients", [])
    original_servings = session.get("original_servings", 1)
    desired_servings = session.get("desired_servings", 1)

    # Convert quantities from strings to floats safely
    parsed_ingredients = []
    for ing in raw_ingredients:
        try:
            quantity = float(Fraction(ing['quantity']))
        except Exception:
            quantity = 0  # fallback if bad data

        parsed_ingredients.append({
            "name": ing.get("name", ""),
            "quantity": quantity,
            "unit": ing.get("unit", "")
        })

    return scale_ingredients(
        {
            "ingredients": parsed_ingredients,
            "original_servings": original_servings
        },
        desired_servings,
        original_servings,
        promote_units=True,
        rounding_enabled=use_nice_fractions
    )

