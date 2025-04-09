from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question, Certificate, Category, Profile
from .forms import ProfileUpdateForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

# Logout View
def user_logout(request):
    logout(request)
    return redirect('index')

# Homepage View
def index(request):
    categories = Category.objects.all()
    return render(request, 'index.html', {'categories': categories})

# Register View
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "register.html")

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("login")

    return render(request, "login.html")

# Quiz Selection View
@login_required
def quiz_selection(request):
    categories = Category.objects.all()
    return render(request, "quiz_selection.html", {"categories": categories})

# Quiz View
@login_required
def quiz(request, category_name):
    category = Category.objects.get(name=category_name)
    questions = Question.objects.filter(category=category)

    if request.method == 'POST':
        score = 0
        for q in questions:
            user_answer = request.POST.get(f'question_{q.id}')
            correct_answer = str(q.correct_option)
            if user_answer == correct_answer:
                score += 1

        total = questions.count()
        percentage = (score / total) * 100 if total > 0 else 0
        passed = "True" if percentage >= 50 else "False"

        if percentage >= 50:
            Certificate.objects.get_or_create(user=request.user, category=category)

        return redirect(reverse('result', args=[score, total, passed, category_name]))

    return render(request, 'quiz.html', {'questions': questions, 'category': category})

# Result View
@login_required
def result(request, score, total, passed, category_name):
    return render(request, 'result.html', {'score': score, 'total': total, 'passed': passed, 'category_name': category_name})

# Certificate View
@login_required
def certificate(request):
    user_certificates = Certificate.objects.filter(user=request.user)

    if user_certificates.exists():
        cert = user_certificates.latest('id')
    else:
        cert = None

    return render(request, 'certificate.html', {'cert': cert})

# Generate Certificate PDF
@login_required
def generate_certificate_pdf(request):
    user = request.user
    cert = Certificate.objects.filter(user=user).select_related('category').last()

    if not cert:
        return HttpResponse("No certificate available", content_type="text/plain")

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="Certificate_{user.username}.pdf"'

    p = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)

    p.setFont("Helvetica-Bold", 40)
    p.drawCentredString(width / 2, height - 100, "CERTIFICATE OF COMPLETION")

    p.setFont("Helvetica", 20)
    p.drawCentredString(width / 2, height - 160, "This is proudly presented to")

    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(width / 2, height - 220, user.username)

    p.setFont("Helvetica", 18)
    p.drawCentredString(width / 2, height - 270, f"For successfully completing the course: {cert.category.name}")

    p.setFont("Helvetica", 16)
    p.drawCentredString(width / 2, height - 320, f"Date Issued: {cert.date_issued}")

    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 4, height - 400, "")
    p.drawCentredString(3 * width / 4, height - 400, "Augustin")

    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 4, height - 420, "")
    p.drawCentredString(3 * width / 4, height - 420, "Director")

    p.showPage()
    p.save()

    return response

# Profile View
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to refresh the profile page after update
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile.html', {'form': form, 'profile': profile})

# Profile Update View
@login_required
def profile_update(request):
    try:
        # Get the user's profile
        profile = request.user.profile
    except Profile.DoesNotExist:
        # If no profile exists, create one (optional)
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated profile (bio and profile_picture)
            return redirect('profile')  # Redirect to the profile view page after update
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile_update.html', {'form': form})
