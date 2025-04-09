from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.index, name='index'),
    path('quiz/selection/', views.quiz_selection, name='quiz_selection'),
    path('quiz/<str:category_name>/', views.quiz, name='quiz'),
    path('result/<int:score>/<int:total>/<str:passed>/<str:category_name>/', views.result, name='result'),
    path('certificate/', views.certificate, name='certificate'),
    path('certificate/generate/', views.generate_certificate_pdf, name='generate_certificate_pdf'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
]
