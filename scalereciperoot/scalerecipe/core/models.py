from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    original_servings = models.IntegerField(default=1)
    desired_servings = models.IntegerField(null=True, blank=True)
    servings = models.PositiveIntegerField()
    use_fractions = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.servings} servings)"

class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=20)  # For display (e.g. "1 1/2")
    quantity_float = models.FloatField(null=True, blank=True)  # For math
    unit = models.CharField(max_length=50, blank=True)
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name} {self.note}" if self.note else f"{self.quantity} {self.unit} {self.name}"
