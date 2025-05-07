from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.courses_list, name='courses_list'),
    path('tally-masterclass/', views.tally_masterclass, name='tally_masterclass'),
    path('tally-intro/', views.tally_intro, name='tally_intro'),
    path('tally-setup/', views.tally_setup, name='tally_setup'),
    path('tally-advance/', views.tally_advance, name='tally_advance'),
    path('aws-masterclass/', views.aws_masterclass, name='aws_masterclass'),
    path('aws-intro/', views.aws_intro, name='aws_intro'),
    path('aws-setup/', views.aws_setup, name='aws_setup'),
    path('aws-s3/', views.aws_s3, name='aws_s3'),
    path('python-masterclass/', views.python_masterclass, name='python_masterclass'),
    path('python-inside/', views.python_inside, name='python_inside'),
    path('python-install-setup/', views.python_install_setup, name='python_install_setup'),
    path('python-basic/', views.python_basic, name='python_basic'),
    path('python-advance/', views.python_advance, name='python_advance'),
    path('<str:course_name>/', views.course_overview, name='course_overview'),
    path('<str:course_name>/<str:level>/', views.course_detail, name='course_detail'),
]
