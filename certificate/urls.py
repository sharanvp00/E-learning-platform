from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('certificate/', views.certificate, name='certificate'),
    path('logout/', views.user_logout, name='logout'),
    path('quiz_selection/', views.quiz_selection, name='quiz_selection'),
    path('quiz/<str:category_name>/', views.quiz, name='quiz'),
    path('result/<int:score>/<int:total>/<str:passed>/<str:category_name>/', views.result, name='result'),
    path('download_certificate/', views.generate_certificate_pdf, name='download_certificate'),
     path('python-content/',views.python_content, name='python_content'),
]
