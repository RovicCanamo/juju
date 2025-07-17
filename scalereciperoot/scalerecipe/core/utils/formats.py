from fractions import Fraction

def format_fraction(value):
    frac = Fraction(value).limit_denominator(10)
    if frac.denominator == 1:
        return f"{frac.numerator}"
    elif frac.numerator > frac.denominator:
        whole = frac.numerator // frac.denominator
        remainder = frac.numerator % frac.denominator
        return f"{whole} {remainder}/{frac.denominator}"
    else:
        return f"{frac.numerator}/{frac.denominator}"

def format_quantity(value):
    try:
        if isinstance(value, float):
            return str(Fraction(value).limit_denominator())
        elif isinstance(value, str):
            # Skip formatting if it's already a mixed string like "1 4/7"
            return value
    except:
        return ''
