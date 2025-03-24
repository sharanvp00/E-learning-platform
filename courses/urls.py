from django.urls import path
from .views import course_overview, course_detail, courses_list

app_name = 'courses'  # Add this line

urlpatterns = [
    
    path('', courses_list, name='courses_list'),
    path('<str:course_name>/', course_overview, name='course_overview'),
    path('<str:course_name>/<str:level>/', course_detail, name='course_detail'),
]
