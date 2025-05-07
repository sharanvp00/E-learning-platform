import os
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Course, CourseContent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root

def get_course_content(course_name, level):
    file_path = os.path.join(BASE_DIR, "courses", "content", f"{course_name}_{level}.txt")  
    print("🔍 Checking file path:", file_path)  # Debugging

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            print("✅ File found. Content:\n", content)  # Debugging
            return content
    else:
        print("❌ File not found!")
        return "Content not found for this course and level."

def course_overview(request, course_name):
    levels = ['beginner', 'intermediate', 'advanced']
    
    context = {
        'course_name': course_name.capitalize(),
        'levels': levels,  # Pass lowercase levels (capitalize in the template)
    }
    return render(request, 'courses/course_overview.html', context)

def course_detail(request, course_name, level):
    content = get_course_content(course_name, level)
    
    context = {
        'course_name': course_name.capitalize(),
        'level': level.capitalize(),
        'content': content,
    }
    return render(request, 'courses/course_detail.html', context)

def courses_list(request):
    courses = ['python', 'tally', 'aws', 'power_bi']
    context = {'courses': courses}
    return render(request, 'courses/courses_list.html', context)

def python_content(request):
    return render(request, 'courses/pythoncontent.html')
    


def python_masterclass(request):
    return render(request, 'courses/python_masterclass.html')

def python_inside(request):
    return render(request, 'courses/Python_inside.html')

def python_install_setup(request):
    return render(request, 'courses/Python_install_setup.html')

def python_basic(request):
    return render(request, 'courses/Python_basic.html')

def python_advance(request):
    return render(request, 'courses/Python_Advance.html')


def aws_masterclass(request):
    return render(request, 'courses/aws_masterclass.html')

def aws_intro(request):
    return render(request, 'courses/aws_intro.html')

def aws_s3(request):
    return render(request, 'courses/aws_s3.html')

def aws_setup(request):
    return render(request, 'courses/aws_setup.html')


def tally_masterclass(request):
    return render(request, 'courses/tally_masterclass.html')


def tally_intro(request):
    return render(request, 'courses/tally_intro.html')

def tally_setup(request):
    return render(request, 'courses/tally_setup.html')

def tally_advance(request):
    return render(request, 'courses/tally_advanced.html')
