import os
from django.shortcuts import render

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
