from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question, Certificate, Category
from django.db.models import Count, Q

from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas



def course_page(request):
    return render(request, 'coursepage.html')


# Helper functions for home page
def search_courses(keyword, category):
    """
    Search for courses based on keyword and category
    """
    query = Q()
    if keyword:
        query |= Q(name__icontains=keyword)
    
    if category and category != 'Courses':  # 'Courses' is the default value for all courses
        query &= Q(category__name=category)  # Assuming you want to filter by category name
    
    return Category.objects.filter(query)

def get_featured_courses():
    """
    Get featured courses with question count
    """
    categories = Category.objects.annotate(question_count=Count('questions'))
    return categories

def get_course_statistics():
    """
    Get statistics for the courses
    """
    return {
        'subjects': Category.objects.count(),
        'courses': Category.objects.count(),  # Same as subjects for now
        'instructors': 5,  # Placeholder value
        'students': User.objects.count(),
    }

def course(request):
    """
    View for displaying all courses with search functionality
    """
    categories = Category.objects.all()
    search_results = None
    search_keyword = ''
    search_category = 'Courses'  # Default value
    
    if request.method == 'POST':
        search_keyword = request.POST.get('keyword', '')
        search_category = request.POST.get('category', 'Courses')
        search_results = search_courses(search_keyword, search_category)
    
    context = {
        'categories': categories,
        'search_results': search_results,
        'search_keyword': search_keyword,
        'search_category': search_category
    }
    
    return render(request, 'course.html', context)

  

def home(request):
    # Handle search functionality
    if request.method == 'POST':
        keyword = request.POST.get('keyword', '')
        category = request.POST.get('category', 'Courses')
        search_results = search_courses(keyword, category)
        return render(request, 'home.html', {
            'categories': Category.objects.all(),
            'featured_courses': get_featured_courses(),
            'stats': get_course_statistics(),
            'search_results': search_results,
            'search_keyword': keyword,
            'search_category': category
        })
    
    # Regular page load
    return render(request, 'home.html', {
        'categories': Category.objects.all(),
        'featured_courses': get_featured_courses(),
        'stats': get_course_statistics()
    })

# Logout View
def user_logout(request):
    logout(request)
    return redirect('home')

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
            return redirect("home")
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

    # Debugging: check if multiple certificates exist and their category
    for cert in user_certificates:
        print(cert.category.name)  # See all certificates for this user

    if user_certificates.exists():
        cert = user_certificates.latest('id')  # Are you sure this is the right one?
        print(f"Selected certificate: {cert.category.name}")  # Confirm which one is selected
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

def python_content(request):
    return render(request, 'pythoncontent.html')

# Dashboard View
@login_required
def dashboard(request):
    user = request.user
    certificates = Certificate.objects.filter(user=user).select_related('category')
    categories = Category.objects.all()
    
    return render(request, 'dashboard.html', {
        'certificates': certificates,
        'user': user,
        'categories': categories
    })

# Profile View
@login_required
def profile(request):
    user = request.user
    certificates = Certificate.objects.filter(user=user).select_related('category')
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Check if it's a profile update
        if 'email' in request.POST:
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()
            messages.success(request, "Profile updated successfully!")
        
        # Check if it's a password change
        elif 'current_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Verify current password
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect!")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match!")
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully! Please login again.")
                return redirect('login')
    
    return render(request, 'profile.html', {
        'certificates': certificates,
        'user': user,
        'categories': categories
    })
