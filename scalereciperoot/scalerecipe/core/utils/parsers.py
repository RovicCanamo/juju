import re
from fractions import Fraction


def parse_ingredient_line(line):
    quantity, unit, name, note = "", "", "", ""

    # Pattern: optional qty, optional unit (with parentheses), rest of line
    match = re.match(r'^([\d\/\.]+)?\s*(\([^\)]+\)\s*\w+|\w+)?\s+(.*)$', line.strip())
    if match:
        quantity, unit, rest = match.groups()

        # First, check if there's a comma for notes
        if ',' in rest:
            name, note = map(str.strip, rest.split(',', 1))
        else:
            # Try to split note if it's one word at the end
            note_keywords = ['sliced', 'chopped', 'cut', 'cubed', 'diced', 'minced', 'peeled', 'crushed', 'grated', 'quartered']
            parts = rest.strip().split()
            if parts and parts[-1].lower() in note_keywords:
                note = parts[-1]
                name = ' '.join(parts[:-1])
            else:
                name = rest.strip()

    return {
        "quantity": quantity or "",
        "unit": unit or "",
        "name": name or "",
        "note": note or "",
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