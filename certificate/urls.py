from django.urls import path
from . import views

urlpatterns = [
    path('send-message/', views.send_message, name='send_message'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('certificate/', views.certificate, name='certificate'),
    path('logout/', views.user_logout, name='logout'),
    path('quiz_selection/', views.quiz_selection, name='quiz_selection'),
    path('quiz/<str:category_name>z/', views.quiz, name='quiz'),
    path('result/<int:score>/<int:total>/<str:passed>/<str:category_name>/', views.result, name='result'),
    path('download_certificate/', views.generate_certificate_pdf, name='download_certificate'),
    path('python-content/', views.python_content, name='python_content'),
    path('download-python-content/', views.download_python_content, name='download_python_content'),
    path('view-python-content/', views.view_python_content, name='view_python_content'),
    path('download-aws-content/', views.download_aws_content, name='download_aws_content'),
    path('view-aws-content/', views.view_aws_content, name='view_aws_content'),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('coursepage/', views.course_page, name='coursepage'),
    path('forgot-password/', views.forgot_password, name='forgot_password')
    
]
