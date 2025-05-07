from django.contrib import admin, messages
from django.utils.html import format_html
from django.template.response import TemplateResponse
from .models import Question, Certificate, Category, UserProfile, ContactMessage

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'category', 'option_preview']
    list_filter = ['category']
    search_fields = ['text', 'category__name']
    fieldsets = (
        ('Question Information', {'fields': ('category', 'text')}),
        ('Options', {'fields': ('option1', 'option2', 'option3', 'option4', 'correct_option'), 'classes': ('wide',)}),
    )

    def option_preview(self, obj):
        correct_option = getattr(obj, f'option{obj.correct_option}')
        return format_html('<span style="color: green; font-weight: bold;">\u2713</span> {}', correct_option)
    option_preview.short_description = 'Correct Answer'

    actions = ['duplicate_questions']

    def duplicate_questions(self, request, queryset):
        count = 0
        for question in queryset:
            question.pk = None
            question.text += " (Copy)"
            question.save()
            count += 1
        self.message_user(request, f"{count} question(s) duplicated successfully.", messages.SUCCESS)
    duplicate_questions.short_description = "Duplicate selected questions"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_email', 'get_full_name', 'profile_picture_preview']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    list_filter = ['user__is_active', 'user__date_joined']

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or "N/A"
    get_full_name.short_description = 'Full Name'

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_preview.short_description = 'Profile Picture'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'message_preview']
    search_fields = ['name', 'email', 'subject', 'message']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'

# Unregister Category and Certificate from admin panel if they were registered
try:
    admin.site.unregister(Category)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Certificate)
except admin.sites.NotRegistered:
    pass
