from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import path
from django.conf import settings
import google.generativeai as genai
from .models import Question, Certificate, Category
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class GenerateQuestionsForm(forms.Form):
    num_questions = forms.IntegerField(label="Number of Questions to Generate", min_value=1, max_value=10, initial=1)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'generate_questions_form']

    def generate_questions_form(self, obj):
       # Return a button that links to the generate_ai_question view
       return format_html(
           '<a class="button" href="generate-ai-question/?category_id={}">Generate AI Question</a>',
           obj.pk,
       )

    generate_questions_form.short_description = "Generate Questions"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-ai-question/',
                self.admin_site.admin_view(self.generate_ai_question),
                name='generate_ai_question'
            ),
        ]
        return custom_urls + urls

    def generate_ai_question(self, request):
        if request.method == 'POST':
            form = GenerateQuestionsForm(request.POST)
            category_id = request.POST.get('category_id')
            try:
                category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                messages.error(request, "Invalid category ID.")
                return redirect('admin:certificate_category_changelist')

            if form.is_valid():
                num_questions = form.cleaned_data['num_questions']
                try:
                    # Configure Gemini
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    model = genai.GenerativeModel('gemini-pro')

                    for _ in range(num_questions):
                        # Construct the prompt
                        prompt = f"Generate a multiple-choice question with 4 options about {category.name}. Clearly mark the correct answer with '(Correct)'."
                        print(f"Prompt: {prompt}")  # Good for debugging

                        # Generate the question
                        response = model.generate_content(prompt)
                        generated_text = response.text
                        print(f"Generated Text: {generated_text}") # For debugging

                        # Parse the generated text (same logic as before)
                        lines = [line.strip() for line in generated_text.split("\n") if line.strip()]
                        if len(lines) < 5:
                            raise ValueError("Gemini response is incomplete.")

                        question_text = lines[0]
                        options = lines[1:5]
                        correct_option_index = None

                        for i, line in enumerate(lines[1:5], start=1):
                            if "(Correct)" in line:
                                correct_option_index = i
                                options[i - 1] = line.replace("(Correct)", "").strip()

                        if correct_option_index is None:
                            raise ValueError("No correct answer identified.")

                        # Create the question
                        Question.objects.create(
                            category=category,
                            text=question_text,
                            option1=options[0],
                            option2=options[1],
                            option3=options[2],
                            option4=options[3],
                            correct_option=correct_option_index
                        )

                    messages.success(request, f"{num_questions} Gemini-generated questions added successfully!")

                except Exception as e:
                    messages.error(request, f"Error generating question: {str(e)}")
                return redirect('admin:certificate_category_changelist')
            else:
                messages.error(request, "Invalid number of questions.")
                return redirect('admin:certificate_category_changelist')
        else:
           return redirect('admin:certificate_category_changelist')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'category']
    list_filter = ['category']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'date_issued']
    list_filter = ['category']