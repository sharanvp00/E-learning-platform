from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.courses_list, name='courses_list'),
    path('python-masterclass/', views.python_masterclass, name='python_masterclass'),
    path('python-inside/', views.python_inside, name='python_inside'),
    path('python-install-setup/', views.python_install_setup, name='python_install_setup'),
    path('python-basic/', views.python_basic, name='python_basic'),
    path('python-advance/', views.python_advance, name='python_advance'),
    path('<str:course_name>/', views.course_overview, name='course_overview'),
    path('<str:course_name>/<str:level>/', views.course_detail, name='course_detail'),
]
