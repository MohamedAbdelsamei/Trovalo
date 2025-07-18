from django.http import HttpResponseForbidden
import face_recognition, tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import MissingPersonReport, ModerationLog, ReportMessage
from .forms import RegisterForm, LoginForm, ReportForm , ReportSearchForm,ReportMessageForm
from django.utils import timezone
from django.contrib import messages
from PIL import Image
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.db.models import Count, Q


@staff_member_required
def moderation_queue(request):
    reports = MissingPersonReport.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'core/moderation_queue.html', {'reports': reports})


def home_view(request):
    return render(request, 'core/home.html')

def register_view(request):

    if request.user.is_authenticated:
        messages.info(request, "You're already logged in!")
        return redirect('report_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()  # Initialize the form for GET request
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('home')
            
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def report_create(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user

            image_file = request.FILES.get('image')
            if image_file:
                try:
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
                        pil_img = Image.open(image_file).convert("RGB")
                        pil_img.save(temp_img.name)
                        image = face_recognition.load_image_file(temp_img.name)
                        face_locations = face_recognition.face_locations(image)

                        if face_locations:
                            encodings = face_recognition.face_encodings(image, face_locations)
                            if encodings:
                                report.set_face_encoding(encodings[0].tolist())  # ✅ Convert ndarray → list
                            else:
                                messages.warning(request, "⚠ Face found but encoding failed.")
                        else:
                            messages.warning(request, "⚠ No face detected in the uploaded image.")

                except Exception as e:
                    messages.warning(request, f"❌ Face encoding failed: {e}")
                    print("ERROR:", e)

            report.save()
            return redirect('report_list')
    else:
        form = ReportForm()
    return render(request, 'core/report_form.html', {'form': form})

@login_required
def report_list(request):
    if request.user.is_admin:
        reports = MissingPersonReport.objects.all().order_by('-created_at')
    else:
        reports = MissingPersonReport.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'core/report_list.html', {'reports': reports})


@login_required
def report_search(request):
    
    result = None
    match_score = None
    form = ReportSearchForm(request.POST or None, request.FILES or None)
    search_attempted = False

    if request.method == 'POST' and form.is_valid():
        search_attempted = True
        national_id = form.cleaned_data['national_id']
        image = form.cleaned_data['image']
        age = form.cleaned_data['age']
        location = form.cleaned_data['last_seen_location']
        name = form.cleaned_data['name']

        # 1: National ID Match
        if national_id:
            try:
                result = MissingPersonReport.objects.get(national_id=national_id)
                match_score = 100.0
                return render(request, 'core/search.html', {'form': form, 'result': result, 'match_score': match_score})
            except MissingPersonReport.DoesNotExist:
                pass  # Proceed to next

        # 2: Combined Face + Name + Age + Location
        best_report = None
        best_score = 0

        candidates = MissingPersonReport.objects.all()

        if image:
            try:
                uploaded_image = face_recognition.load_image_file(image)
                encodings = face_recognition.face_encodings(uploaded_image)
                if not encodings:
                    messages.warning(request, "No face found in the uploaded image.")
                    return render(request, 'core/search.html', {'form': form})
                uploaded_encoding = encodings[0]


                for report in candidates.exclude(face_encoding__isnull=True):
                    score = 0

                    # Face score (50%)
                    encoding = report.get_face_encoding()
                    distance = face_recognition.face_distance([encoding], uploaded_encoding)[0]
                    face_score = (1 - distance)
                    score += face_score * 0.5

                    # Location match (20%)
                    if location and location.lower() in report.last_seen_location.lower():
                        score += 0.2

                    # Age match (15%)
                    if age:
                        age_diff = abs(report.age - age)
                        age_score = max(0, (10 - age_diff) / 10)
                        score += age_score * 0.15

                    # Name match (15%)
                    if name and name.lower() in report.name.lower():
                        score += 0.15

                    if score > best_score:
                        best_score = score
                        best_report = report

            except Exception as e:
                messages.warning(request, f"Face recognition failed: {str(e)}")
        
        if best_report and best_score >= 0.3:  # Threshold for a match
            result = best_report
            match_score = round(best_score * 100, 2)        

    return render(request, 'core/search.html', {
        'form': form,
        'result': result,
        'match_score': match_score,
        'search_attempted': search_attempted
    })


@staff_member_required
def moderation_queue(request):
    reports = MissingPersonReport.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'core/moderation_queue.html', {'reports': reports})

@staff_member_required
def moderate_report(request, report_id):
    report = get_object_or_404(MissingPersonReport, id=report_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approve', 'delete']:
            report.status = 'Active' if action == 'approve' else 'Deleted'
            report.save()

             
            ModerationLog.objects.create(
                report=report,
                action=action,
                moderated_by=request.user,
                timestamp=timezone.now(),
                comments=request.POST.get('comment')
            )

            # ✅ Notify user (log to console or send email)
            print(f"🔔 User {report.user.username} notified: report {report.name} was {action}d.")

    return redirect('moderation_queue')


@login_required
def message_threads(request):
    # 1. Reports where current user is the owner and has messages
    owned_reports = MissingPersonReport.objects.filter(user=request.user, messages__isnull=False)
    # 2. Reports where user sent a message
    messaged_reports = MissingPersonReport.objects.filter(messages__sender=request.user)
    # Combine both and remove duplicates
    reports = (owned_reports | messaged_reports).distinct().annotate(
    unread_count=Count('messages', filter=Q(messages__recipient=request.user, messages__is_read=False))
    )
    return render(request, 'core/message_threads.html', {'reports': reports})

@login_required
def message_thread(request, report_id):
    report = get_object_or_404(MissingPersonReport, id=report_id)
    messages_thread = ReportMessage.objects.filter(report=report).order_by('sent_at')
    
    ReportMessage.objects.filter(
    report=report,
    recipient=request.user,
    is_read=False
    ).update(is_read=True)

    if request.method == 'POST':
        form = ReportMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.report = report
            msg.sender = request.user
            if request.user == report.user:
                # This is a reply — get the original sender
                last_msg = messages_thread.last()
                msg.recipient = last_msg.sender if last_msg else None  # fallback if thread is broken
            else:
                # This is the first contact
                msg.recipient = report.user 
            msg.save()

            send_mail(
                f"📨 Reply regarding report {report.name}",
                f"{request.user.username} replied: {msg.content}",
                "noreply@trovalo.local",
                [msg.recipient.email],
                fail_silently=True
            )

            return redirect('message_thread', report_id=report.id)
    else:
        form = ReportMessageForm()

    return render(request, 'core/message_thread.html', {
        'report': report,
        'messages': messages_thread,
        'form': form,
    })
