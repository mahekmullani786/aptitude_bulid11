from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Question, Attempt
from django.db.models import Count


def home(request):
    # show categories and user progress
    categories = Question.objects.values('category').annotate(count=Count('id'))
    user_score = None
    chart_data = None
    streak_days = None
    if request.user.is_authenticated:
        total = Attempt.objects.filter(user=request.user).count()
        correct = Attempt.objects.filter(user=request.user, is_correct=True).count()
        user_score = {'total': total, 'correct': correct}

        # prepare chart data from QuizResult
        from .models import QuizResult
        results = QuizResult.objects.filter(user=request.user).order_by('created_at')
        labels = [r.created_at.strftime('%Y-%m-%d') for r in results]
        scores = [r.correct for r in results]
        chart_data = {'labels': labels, 'scores': scores}

        # prepare streak data for last 30 days
        from datetime import date, timedelta
        solved_dates = set(r.created_at.date() for r in results)
        today = date.today()
        days = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            days.append({'date': d.isoformat(), 'label': d.strftime('%b %d'), 'solved': d in solved_dates})
        streak_days = days

    return render(request, 'home.html', {'categories': categories, 'user_score': user_score, 'chart_data': chart_data, 'streak_days': streak_days})


from django.core import signing
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .forms import CustomUserCreationForm


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # create inactive user until email verified
            user.is_active = False
            user.save()

            # generate token
            token = signing.dumps({'user_id': user.id}, salt='email-verify')
            verify_url = f"{request.scheme}://{request.get_host()}{reverse('quiz:verify_email', args=[token])}"

            # send verification email
            subject = 'Verify your Aptitude Build account'
            message = render_to_string('registration/verification_email.html', {'user': user, 'verify_url': verify_url})
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

            return render(request, 'registration/verification_sent.html', {'email': user.email})
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def verify_email(request, token):
    try:
        data = signing.loads(token, salt='email-verify', max_age=60 * 60 * 24)
        user_id = data.get('user_id')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        return render(request, 'registration/verification_complete.html')
    except signing.SignatureExpired:
        return render(request, 'registration/verification_invalid.html', {'reason': 'expired'})
    except Exception:
        return render(request, 'registration/verification_invalid.html', {'reason': 'invalid'})


@login_required
def start_quiz(request):
    """Initialize a session-scoped quiz with up to 10 random questions."""
    qids = list(Question.objects.order_by('?').values_list('id', flat=True)[:10])
    request.session['quiz_qids'] = qids
    request.session['quiz_pos'] = 0
    request.session['quiz_total'] = len(qids)
    request.session['quiz_attempt_ids'] = []
    request.session.modified = True
    return redirect('quiz:quiz_question')


@login_required
def quiz_question(request):
    # Use session-stored question list for a fixed-length quiz
    qids = request.session.get('quiz_qids')
    if not qids:
        return redirect('quiz:start')

    pos = int(request.session.get('quiz_pos', 0))
    total = int(request.session.get('quiz_total', len(qids)))

    if pos >= total:
        return redirect('quiz:result')

    qid = qids[pos]
    next_q = get_object_or_404(Question, id=qid)

    feedback = None
    if request.method == 'POST':
        selected = request.POST.get('option')
        is_correct = (selected == next_q.answer)
        attempt = Attempt.objects.create(user=request.user, question=next_q, selected=selected, is_correct=is_correct)
        # store attempt id in session for result review
        ids = request.session.get('quiz_attempt_ids', [])
        ids.append(attempt.id)
        request.session['quiz_attempt_ids'] = ids

        pos += 1
        request.session['quiz_pos'] = pos
        request.session.modified = True

        if pos >= total:
            return redirect('quiz:result')
        return redirect('quiz:quiz_question')

    return render(request, 'quiz_question.html', {'question': next_q, 'position': pos + 1, 'total': total, 'feedback': feedback})


@login_required
def result_view(request):
    attempt_ids = request.session.get('quiz_attempt_ids', [])
    attempts = Attempt.objects.filter(id__in=attempt_ids).select_related('question')
    total = attempts.count()
    correct = attempts.filter(is_correct=True).count()

    # Save summary result
    from .models import QuizResult
    if total > 0:
        QuizResult.objects.create(user=request.user, total=total, correct=correct)

    # cleanup session keys for completed quiz
    request.session.pop('quiz_qids', None)
    request.session.pop('quiz_pos', None)
    request.session.pop('quiz_total', None)
    request.session.pop('quiz_attempt_ids', None)
    request.session.modified = True

    return render(request, 'result.html', {'total': total, 'correct': correct, 'attempts': attempts})
