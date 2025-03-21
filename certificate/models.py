from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """Model to store predefined quiz categories"""
    CATEGORY_CHOICES = (
        ('Python', 'Python'),
        ('AWS', 'AWS'),
        ('Tally', 'Tally'),
        ('PowerBi','PowerBi')
    )
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True, default='Python')

    def __str__(self):
        return self.name

class Question(models.Model):
    """Model to store quiz questions"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)

    CORRECT_OPTION_CHOICES = (
        (1, 'Option 1'),
        (2, 'Option 2'),
        (3, 'Option 3'),
        (4, 'Option 4'),
    )
    correct_option = models.PositiveSmallIntegerField(choices=CORRECT_OPTION_CHOICES)

    def __str__(self):
        return f"{self.category.name} - {self.text}"

class Certificate(models.Model):
    """Model to store certificates for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Certificate for specific category
    date_issued = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.user.username} in {self.category.name}"