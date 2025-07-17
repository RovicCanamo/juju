import re
from fractions import Fraction

def parse_ingredient_line(line):
    pattern = r'^(\d+\s\d+/\d+|\d+/\d+|\d+)?\s*([a-zA-Z.]+)?\s*(.*)$'
    match = re.match(pattern, line.strip())
    if not match:
        return {"quantity": "", "unit": "", "name": line.strip()}

    quantity_raw, unit, name = match.groups()
    try:
        if quantity_raw:
            if ' ' in quantity_raw:
                whole, frac = quantity_raw.split()
                quantity = float(whole) + float(Fraction(frac))
            else:
                quantity = float(Fraction(quantity_raw))
        else:
            quantity = ""
    except:
        quantity = ""

    return {
        "quantity": quantity,
        "unit": unit or "",
        "name": name.strip()
    }

def parse_ingredients(text):
    lines = text.strip().split('\n')
    return [parse_ingredient_line(line) for line in lines if line.strip()]

def parse_fraction_string(s):
    try:
        if ' ' in s:
            whole, frac = s.split()
            return float(whole) + float(Fraction(frac))
        return float(Fraction(s))
    except:
        return None

def parse_ingredients_text(text):  # <- for compatibility with old import
    return parse_ingredients(text)