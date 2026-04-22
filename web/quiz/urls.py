from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('start/', views.start_quiz, name='start'),
    path('quiz/', views.quiz_question, name='quiz_question'),
    path('result/', views.result_view, name='result'),
]
