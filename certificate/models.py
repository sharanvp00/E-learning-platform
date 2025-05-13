from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver








# User Profile model to extend the built-in User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# Automatically create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# Model to store messages from a contact form
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

# Quiz category model
class Category(models.Model):
    CATEGORY_CHOICES = (
        ('Python', 'Python'),
        ('AWS', 'AWS'),
        ('Tally', 'Tally'),
        
    )
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True, default='Python')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# Quiz question model
class Question(models.Model):
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

# Certificate model linked to User and Category
class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_issued = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.user.username} in {self.category.name}"
