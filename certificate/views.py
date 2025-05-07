from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question, Certificate, Category, UserProfile
from django.db.models import Count, Q
from django.contrib import messages

from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


from .models import ContactMessage
from django.http import JsonResponse

def send_message(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        return JsonResponse({'success': True})



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

    if user_certificates.exists():
        # Get the most recent certificate
        cert = user_certificates.select_related('category').latest('id')
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

@login_required
def view_python_content(request):
    """
    View Python course content as a comprehensive study guide in HTML format
    """
    try:
        python_category = Category.objects.get(name='Python')
        python_questions = Question.objects.filter(category=python_category)
        
        context = {
            'questions': python_questions,
        }
        
        return render(request, 'python_study_guide.html', context)
        
    except Category.DoesNotExist:
        messages.error(request, "Python course content not available")
        return redirect('quiz_selection')

@login_required
def view_aws_content(request):
    """
    View AWS Cloud Computing content as a comprehensive study guide in HTML format
    """
    try:
        aws_category = Category.objects.get(name='AWS')
        aws_questions = Question.objects.filter(category=aws_category)
        
        context = {
            'questions': aws_questions,
        }
        
        return render(request, 'aws_study_guide.html', context)
        
    except Category.DoesNotExist:
        messages.error(request, "AWS course content not available")
        return redirect('quiz_selection')

@login_required
def download_aws_content(request):
    """
    Download AWS Cloud Computing content as a comprehensive study guide in text format
    """
    try:
        aws_category = Category.objects.get(name='AWS')
        aws_questions = Question.objects.filter(category=aws_category)
        
        # Create a text file with AWS course content
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="AWS_Study_Guide.txt"'
        
        # Title and Introduction
        response.write("===============================================\n")
        response.write("           AWS CLOUD COMPUTING STUDY GUIDE      \n")
        response.write("===============================================\n\n")
        
        response.write("ABOUT THIS GUIDE\n")
        response.write("--------------\n")
        response.write("This comprehensive study guide is designed to help you master AWS Cloud Computing\n")
        response.write("from fundamentals to advanced services. Use this guide alongside your course\n")
        response.write("materials to enhance your learning experience.\n\n")
        
        # Table of Contents
        response.write("TABLE OF CONTENTS\n")
        response.write("-----------------\n")
        response.write("1. Introduction to AWS\n")
        response.write("2. AWS Global Infrastructure\n")
        response.write("3. Core AWS Services\n")
        response.write("4. Compute Services\n")
        response.write("5. Storage Services\n")
        response.write("6. Database Services\n")
        response.write("7. Networking & Content Delivery\n")
        response.write("8. Security, Identity & Compliance\n")
        response.write("9. AWS Management Tools\n")
        response.write("10. Practice Questions\n\n")
        
        # Section 1: Introduction
        response.write("===============================================\n")
        response.write("1. INTRODUCTION TO AWS\n")
        response.write("===============================================\n\n")
        
        response.write("What is AWS?\n")
        response.write("-------------\n")
        response.write("Amazon Web Services (AWS) is a comprehensive cloud computing platform provided by\n")
        response.write("Amazon. It offers a mixture of infrastructure as a service (IaaS), platform as a\n")
        response.write("service (PaaS), and packaged software as a service (SaaS) offerings.\n\n")
        
        response.write("Why Use AWS?\n")
        response.write("--------------\n")
        response.write("• Flexibility - Only use what you need, scale up or down as required\n")
        response.write("• Cost-Effective - Pay only for what you use, no upfront hardware costs\n")
        response.write("• Scalability - Easily scale resources up or down based on demand\n")
        response.write("• Security - Comprehensive security capabilities and features\n")
        response.write("• Global Reach - Deploy applications worldwide in minutes\n\n")
        
        response.write("AWS Account Structure\n")
        response.write("--------------\n")
        response.write("• Root Account - The initial account created when first setting up AWS\n")
        response.write("• IAM Users - Individual users created within the account\n")
        response.write("• Organizations - Manage multiple AWS accounts as a single unit\n")
        response.write("• Consolidated Billing - Single payment method for all accounts\n\n")
        
        # Section 2: AWS Global Infrastructure
        response.write("===============================================\n")
        response.write("2. AWS GLOBAL INFRASTRUCTURE\n")
        response.write("===============================================\n\n")
        
        response.write("Regions\n")
        response.write("--------------\n")
        response.write("• Geographical areas with multiple Availability Zones\n")
        response.write("• Each region is completely independent\n")
        response.write("• Not all services are available in all regions\n")
        response.write("• Data does not automatically replicate across regions\n\n")
        
        response.write("Availability Zones (AZs)\n")
        response.write("--------------\n")
        response.write("• Physically separate data centers within a region\n")
        response.write("• Connected with high-bandwidth, low-latency networking\n")
        response.write("• Designed for fault isolation\n")
        response.write("• Applications should be designed to use multiple AZs for high availability\n\n")
        
        response.write("Edge Locations\n")
        response.write("--------------\n")
        response.write("• Content Delivery Network (CloudFront) endpoints\n")
        response.write("• More numerous than regions or AZs\n")
        response.write("• Used to cache content closer to users\n")
        response.write("• Also used for Route 53 (DNS) and AWS Shield (DDoS protection)\n\n")
        
        # Section 3: Core AWS Services
        response.write("===============================================\n")
        response.write("3. CORE AWS SERVICES\n")
        response.write("===============================================\n\n")
        
        response.write("Identity and Access Management (IAM)\n")
        response.write("--------------\n")
        response.write("• Manage access to AWS services and resources\n")
        response.write("• Create and manage AWS users and groups\n")
        response.write("• Use permissions to allow/deny access to resources\n")
        response.write("• Implement Multi-Factor Authentication (MFA)\n")
        response.write("• Enable temporary security credentials\n\n")
        
        response.write("Virtual Private Cloud (VPC)\n")
        response.write("--------------\n")
        response.write("• Isolated section of the AWS Cloud\n")
        response.write("• Complete control over virtual networking environment\n")
        response.write("• Create subnets, route tables, network gateways\n")
        response.write("• Connect to your data center using VPN or Direct Connect\n")
        response.write("• Implement security groups and network ACLs\n\n")
        
        # Section 4: Compute Services
        response.write("===============================================\n")
        response.write("4. COMPUTE SERVICES\n")
        response.write("===============================================\n\n")
        
        response.write("Elastic Compute Cloud (EC2)\n")
        response.write("--------------\n")
        response.write("• Virtual servers in the cloud\n")
        response.write("• Various instance types optimized for different use cases\n")
        response.write("• Multiple pricing options (On-Demand, Reserved, Spot)\n")
        response.write("• Auto Scaling to adjust capacity as needed\n")
        response.write("• Load Balancing to distribute traffic\n\n")
        
        response.write("Lambda\n")
        response.write("--------------\n")
        response.write("• Serverless compute service\n")
        response.write("• Run code without provisioning servers\n")
        response.write("• Pay only for compute time consumed\n")
        response.write("• Automatically scales applications\n")
        response.write("• Supports multiple programming languages\n\n")
        
        response.write("Elastic Beanstalk\n")
        response.write("--------------\n")
        response.write("• Platform as a Service (PaaS)\n")
        response.write("• Deploy and scale web applications\n")
        response.write("• Automatically handles capacity provisioning, load balancing, and monitoring\n")
        response.write("• Supports various platforms (Java, .NET, PHP, Node.js, etc.)\n\n")
        
        # Section 5: Storage Services
        response.write("===============================================\n")
        response.write("5. STORAGE SERVICES\n")
        response.write("===============================================\n\n")
        
        response.write("Simple Storage Service (S3)\n")
        response.write("--------------\n")
        response.write("• Object storage service\n")
        response.write("• Virtually unlimited storage capacity\n")
        response.write("• Highly durable and available\n")
        response.write("• Different storage classes for different use cases\n")
        response.write("• Versioning, encryption, and access control\n\n")
        
        response.write("Elastic Block Store (EBS)\n")
        response.write("--------------\n")
        response.write("• Persistent block storage for EC2 instances\n")
        response.write("• Independent lifecycle from EC2 instances\n")
        response.write("• Different volume types for different performance needs\n")
        response.write("• Point-in-time snapshots\n\n")
        
        response.write("Glacier\n")
        response.write("--------------\n")
        response.write("• Low-cost storage for data archiving\n")
        response.write("• Designed for infrequently accessed data\n")
        response.write("• Various retrieval options (minutes to hours)\n")
        response.write("• Highly durable storage\n\n")
        
        # Section 10: Practice Questions
        response.write("===============================================\n")
        response.write("10. PRACTICE QUESTIONS\n")
        response.write("===============================================\n\n")
        
        # Add quiz questions from the database
        for i, question in enumerate(aws_questions, 1):
            response.write(f"Question {i}: {question.text}\n")
            response.write(f"A) {question.option1}\n")
            response.write(f"B) {question.option2}\n")
            response.write(f"C) {question.option3}\n")
            response.write(f"D) {question.option4}\n")
            response.write(f"Answer: {'ABCD'[question.correct_option-1]}\n\n")
        
        # Conclusion
        response.write("===============================================\n")
        response.write("CONCLUSION\n")
        response.write("===============================================\n\n")
        
        response.write("Congratulations on completing this AWS Cloud Computing study guide!\n")
        response.write("Continue exploring AWS services and practicing with hands-on labs to\n")
        response.write("enhance your cloud computing skills. AWS offers a vast ecosystem of\n")
        response.write("services that can help you build scalable, reliable, and secure applications.\n\n")
        
        response.write("Happy cloud computing!\n")
        
        return response
        
    except Category.DoesNotExist:
        return HttpResponse("AWS course content not available", content_type="text/plain")

@login_required
def download_python_content(request):
    """
    Download Python course content as a comprehensive study guide in text format
    """
    try:
        python_category = Category.objects.get(name='Python')
        python_questions = Question.objects.filter(category=python_category)
        
        # Create a text file with Python course content
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="Python_Study_Guide.txt"'
        
        # Title and Introduction
        response.write("===============================================\n")
        response.write("           PYTHON PROGRAMMING STUDY GUIDE      \n")
        response.write("===============================================\n\n")
        
        response.write("ABOUT THIS GUIDE\n")
        response.write("--------------\n")
        response.write("This comprehensive study guide is designed to help you master Python programming\n")
        response.write("from fundamentals to advanced concepts. Use this guide alongside your course\n")
        response.write("materials to enhance your learning experience.\n\n")
        
        # Table of Contents
        response.write("TABLE OF CONTENTS\n")
        response.write("-----------------\n")
        response.write("1. Introduction to Python\n")
        response.write("2. Python Fundamentals\n")
        response.write("3. Data Structures\n")
        response.write("4. Control Flow\n")
        response.write("5. Functions and Modules\n")
        response.write("6. Object-Oriented Programming\n")
        response.write("7. File Handling\n")
        response.write("8. Exception Handling\n")
        response.write("9. Working with Libraries\n")
        response.write("10. Practice Questions\n\n")
        
        # Section 1: Introduction
        response.write("===============================================\n")
        response.write("1. INTRODUCTION TO PYTHON\n")
        response.write("===============================================\n\n")
        
        response.write("What is Python?\n")
        response.write("-------------\n")
        response.write("Python is a high-level, interpreted programming language created by Guido van Rossum\n")
        response.write("and first released in 1991. It emphasizes code readability with its notable use of\n")
        response.write("significant whitespace. Python features a dynamic type system and automatic memory\n")
        response.write("management and supports multiple programming paradigms.\n\n")
        
        response.write("Why Learn Python?\n")
        response.write("--------------\n")
        response.write("• Readability and simplicity - Clean syntax that's easy to learn\n")
        response.write("• Versatility - Used in web development, data science, AI, automation, and more\n")
        response.write("• Large standard library - \"Batteries included\" philosophy\n")
        response.write("• Strong community support - Extensive documentation and resources\n")
        response.write("• High demand in job market - One of the most sought-after programming skills\n\n")
        
        response.write("Python Versions\n")
        response.write("--------------\n")
        response.write("• Python 2.x - Legacy version (officially discontinued as of January 2020)\n")
        response.write("• Python 3.x - Current version with ongoing development and improvements\n")
        response.write("• This guide focuses on Python 3.x\n\n")
        
        # Section 2: Python Fundamentals
        response.write("===============================================\n")
        response.write("2. PYTHON FUNDAMENTALS\n")
        response.write("===============================================\n\n")
        
        response.write("Getting Started\n")
        response.write("--------------\n")
        response.write("• Installing Python: Download from python.org or use package managers\n")
        response.write("• Python Interpreter: Interactive mode using 'python' or 'python3' command\n")
        response.write("• IDEs and Code Editors: PyCharm, VS Code, Jupyter Notebooks\n\n")
        
        response.write("Basic Syntax\n")
        response.write("-----------\n")
        response.write("• Indentation: Python uses indentation (typically 4 spaces) to define code blocks\n")
        response.write("• Comments: Use # for single-line comments and triple quotes for multi-line comments\n")
        response.write("• Line Continuation: Use \\ for line continuation or implicit continuation within brackets\n\n")
        
        response.write("Variables and Data Types\n")
        response.write("----------------------\n")
        response.write("• Variables: Names that store values (no explicit declaration needed)\n")
        response.write("• Naming Rules: Start with letter/underscore, case-sensitive, no reserved words\n\n")
        
        response.write("Basic Data Types:\n")
        response.write("• Integers (int): Whole numbers like 5, -3, 0\n")
        response.write("• Floating-point (float): Decimal numbers like 3.14, -0.001\n")
        response.write("• Strings (str): Text enclosed in quotes - 'hello', \"world\"\n")
        response.write("• Booleans (bool): True or False values\n")
        response.write("• None: Represents absence of value\n\n")
        
        response.write("Type Conversion:\n")
        response.write("• int(), float(), str(), bool() - Convert between types\n\n")
        
        response.write("Basic Operations\n")
        response.write("---------------\n")
        response.write("Arithmetic Operators:\n")
        response.write("• Addition (+): 5 + 3 = 8\n")
        response.write("• Subtraction (-): 5 - 3 = 2\n")
        response.write("• Multiplication (*): 5 * 3 = 15\n")
        response.write("• Division (/): 5 / 3 = 1.6666...\n")
        response.write("• Floor Division (//): 5 // 3 = 1\n")
        response.write("• Modulus (%): 5 % 3 = 2\n")
        response.write("• Exponentiation (**): 5 ** 3 = 125\n\n")
        
        response.write("Comparison Operators:\n")
        response.write("• Equal (==), Not Equal (!=)\n")
        response.write("• Greater Than (>), Less Than (<)\n")
        response.write("• Greater Than or Equal (>=), Less Than or Equal (<=)\n\n")
        
        response.write("Logical Operators:\n")
        response.write("• and, or, not\n\n")
        
        response.write("Assignment Operators:\n")
        response.write("• =, +=, -=, *=, /=, %=, //=, **=\n\n")
        
        # Section 3: Data Structures
        response.write("===============================================\n")
        response.write("3. DATA STRUCTURES\n")
        response.write("===============================================\n\n")
        
        response.write("Lists\n")
        response.write("-----\n")
        response.write("• Ordered, mutable collections of items\n")
        response.write("• Created with square brackets: my_list = [1, 2, 3, 'hello']\n")
        response.write("• Indexing starts at 0: my_list[0] returns 1\n")
        response.write("• Negative indexing: my_list[-1] returns 'hello'\n")
        response.write("• Slicing: my_list[1:3] returns [2, 3]\n\n")
        
        response.write("Common List Methods:\n")
        response.write("• append(), extend(), insert()\n")
        response.write("• remove(), pop(), clear()\n")
        response.write("• index(), count(), sort(), reverse()\n\n")
        
        response.write("Tuples\n")
        response.write("------\n")
        response.write("• Ordered, immutable collections of items\n")
        response.write("• Created with parentheses: my_tuple = (1, 2, 3, 'hello')\n")
        response.write("• Similar indexing and slicing as lists\n")
        response.write("• Used for data that shouldn't change\n\n")
        
        response.write("Dictionaries\n")
        response.write("-----------\n")
        response.write("• Unordered collections of key-value pairs\n")
        response.write("• Created with curly braces: my_dict = {'name': 'John', 'age': 30}\n")
        response.write("• Accessing values: my_dict['name'] returns 'John'\n")
        response.write("• Keys must be immutable (strings, numbers, tuples)\n\n")
        
        response.write("Common Dictionary Methods:\n")
        response.write("• get(), keys(), values(), items()\n")
        response.write("• update(), pop(), clear()\n\n")
        
        response.write("Sets\n")
        response.write("----\n")
        response.write("• Unordered collections of unique items\n")
        response.write("• Created with curly braces: my_set = {1, 2, 3}\n")
        response.write("• No duplicates allowed\n")
        response.write("• Useful for membership testing and eliminating duplicates\n\n")
        
        response.write("Common Set Methods:\n")
        response.write("• add(), remove(), discard()\n")
        response.write("• union(), intersection(), difference()\n\n")
        
        # Section 4: Control Flow
        response.write("===============================================\n")
        response.write("4. CONTROL FLOW\n")
        response.write("===============================================\n\n")
        
        response.write("Conditional Statements\n")
        response.write("---------------------\n")
        response.write("if-elif-else Structure:\n")
        response.write("```python\n")
        response.write("if condition1:\n")
        response.write("    # code block executed if condition1 is True\n")
        response.write("elif condition2:\n")
        response.write("    # code block executed if condition1 is False and condition2 is True\n")
        response.write("else:\n")
        response.write("    # code block executed if all conditions are False\n")
        response.write("```\n\n")
        
        response.write("Loops\n")
        response.write("-----\n")
        response.write("For Loops:\n")
        response.write("```python\n")
        response.write("for item in iterable:\n")
        response.write("    # code block executed for each item\n")
        response.write("```\n\n")
        
        response.write("While Loops:\n")
        response.write("```python\n")
        response.write("while condition:\n")
        response.write("    # code block executed while condition is True\n")
        response.write("```\n\n")
        
        response.write("Loop Control:\n")
        response.write("• break - Exit the loop completely\n")
        response.write("• continue - Skip the current iteration and continue with the next\n")
        response.write("• pass - Do nothing (placeholder)\n\n")
        
        response.write("Comprehensions\n")
        response.write("--------------\n")
        response.write("List Comprehensions:\n")
        response.write("```python\n")
        response.write("[expression for item in iterable if condition]\n")
        response.write("```\n\n")
        
        response.write("Dictionary Comprehensions:\n")
        response.write("```python\n")
        response.write("{key_expr: value_expr for item in iterable if condition}\n")
        response.write("```\n\n")
        
        # Section 5: Functions and Modules
        response.write("===============================================\n")
        response.write("5. FUNCTIONS AND MODULES\n")
        response.write("===============================================\n\n")
        
        response.write("Defining Functions\n")
        response.write("-----------------\n")
        response.write("```python\n")
        response.write("def function_name(parameters):\n")
        response.write("    \"\"\"Docstring describing the function\"\"\"\n")
        response.write("    # Function body\n")
        response.write("    return value  # Optional return statement\n")
        response.write("```\n\n")
        
        response.write("Parameters and Arguments\n")
        response.write("----------------------\n")
        response.write("• Positional arguments: Matched by position\n")
        response.write("• Keyword arguments: Matched by parameter name\n")
        response.write("• Default parameters: Specify default values\n")
        response.write("• *args: Variable number of positional arguments (as tuple)\n")
        response.write("• **kwargs: Variable number of keyword arguments (as dictionary)\n\n")
        
        response.write("Lambda Functions\n")
        response.write("---------------\n")
        response.write("• Anonymous functions defined using lambda keyword\n")
        response.write("• Syntax: lambda parameters: expression\n")
        response.write("• Example: square = lambda x: x**2\n\n")
        
        response.write("Modules and Packages\n")
        response.write("-------------------\n")
        response.write("• Module: Python file containing code (functions, classes, variables)\n")
        response.write("• Package: Directory containing multiple modules\n")
        response.write("• Importing: import module_name or from module_name import function_name\n")
        response.write("• Standard Library: Built-in modules like math, random, datetime\n\n")
        
        # Section 6: Object-Oriented Programming
        response.write("===============================================\n")
        response.write("6. OBJECT-ORIENTED PROGRAMMING\n")
        response.write("===============================================\n\n")
        
        response.write("Classes and Objects\n")
        response.write("-----------------\n")
        response.write("• Class: Blueprint for creating objects\n")
        response.write("• Object: Instance of a class\n")
        response.write("• Attributes: Variables that belong to a class/object\n")
        response.write("• Methods: Functions that belong to a class/object\n\n")
        
        response.write("Class Definition:\n")
        response.write("```python\n")
        response.write("class ClassName:\n")
        response.write("    # Class attribute\n")
        response.write("    class_attribute = value\n")
        response.write("    \n")
        response.write("    # Constructor method\n")
        response.write("    def __init__(self, parameters):\n")
        response.write("        # Instance attributes\n")
        response.write("        self.attribute = value\n")
        response.write("    \n")
        response.write("    # Instance method\n")
        response.write("    def method_name(self, parameters):\n")
        response.write("        # Method body\n")
        response.write("        return value\n")
        response.write("```\n\n")
        
        response.write("Inheritance\n")
        response.write("-----------\n")
        response.write("• Mechanism for creating a new class that is a modified version of an existing class\n")
        response.write("• Syntax: class ChildClass(ParentClass):\n")
        response.write("• super() function: Access parent class methods\n\n")
        
        response.write("Polymorphism\n")
        response.write("-----------\n")
        response.write("• Same interface for different underlying forms (data types/classes)\n")
        response.write("• Method overriding: Redefining methods in child classes\n\n")
        
        response.write("Encapsulation\n")
        response.write("------------\n")
        response.write("• Restricting access to methods and variables\n")
        response.write("• Name mangling: __attribute (double underscore) for private attributes\n")
        response.write("• Properties: @property decorator for getter/setter methods\n\n")
        
        # Section 10: Practice Questions
        response.write("===============================================\n")
        response.write("10. PRACTICE QUESTIONS\n")
        response.write("===============================================\n\n")
        
        # Add quiz questions from the database
        for i, question in enumerate(python_questions, 1):
            response.write(f"Question {i}: {question.text}\n")
            response.write(f"A) {question.option1}\n")
            response.write(f"B) {question.option2}\n")
            response.write(f"C) {question.option3}\n")
            response.write(f"D) {question.option4}\n")
            response.write(f"Answer: {'ABCD'[question.correct_option-1]}\n\n")
        
        # Conclusion
        response.write("===============================================\n")
        response.write("CONCLUSION\n")
        response.write("===============================================\n\n")
        
        response.write("Congratulations on completing this Python study guide! Remember that\n")
        response.write("programming is a skill that improves with practice. Continue building\n")
        response.write("projects, solving problems, and exploring new concepts to enhance your\n")
        response.write("Python programming abilities.\n\n")
        
        response.write("Happy coding!\n")
        
        return response
        
    except Category.DoesNotExist:
        return HttpResponse("Python course content not available", content_type="text/plain")

# Dashboard View
@login_required
def dashboard(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    certificates = Certificate.objects.filter(user=user).select_related('category')
    categories = Category.objects.all()
    
    return render(request, 'dashboard.html', {
        'certificates': certificates,
        'user': user,
        'profile': profile,
        'categories': categories
    })

# Profile View
@login_required
def profile(request):
    user = request.user
    # Get or create the user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    certificates = Certificate.objects.filter(user=user).select_related('category')
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Check if it's a profile update
        if 'email' in request.POST:
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            
            # Update bio
            profile.bio = request.POST.get('bio', '')
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            
            # Save both user and profile
            user.save()
            profile.save()
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
        'profile': profile,
        'categories': categories
    })


# UserProfile is now imported at the top of the file

