from django.contrib import admin
from .models import Question, Attempt

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'category', 'answer')
    search_fields = ('question_text', 'category')

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'selected', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('user__username', 'question__question_text')

from .models import QuizResult

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'correct', 'total', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
