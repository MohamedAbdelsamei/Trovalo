from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout,get_user_model
from django.contrib.auth.decorators import login_required
from .models import MissingPersonReport
from .forms import RegisterForm, LoginForm, ReportForm
from django.contrib import messages

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

    User = get_user_model()
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = User.objects.get(pk=request.user.pk)
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