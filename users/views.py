from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Profile, Skill
from .forms import CustomUserCreationForm, ProfileForm
from .utils import search_profiles


# Create your views here.
def home(request):
    profiles = Profile.objects.all()

    #The search developers function
    profiles, search_query = search_profiles(request)

    context = {'profiles':profiles, 'search_query':search_query}
    return render(request, 'users/home.html', context)



def profile(request, pk):
    profile = Profile.objects.get(id=pk)

    top_skills = profile.skill_set.exclude(description__exact="")
    other_skills = profile.skill_set.filter(description="")
    projects = profile.project_set.all()
    context = {'profile':profile, 'top_skills':top_skills, 'other_skills':other_skills,
               'projects':projects}
    return render(request, 'users/profile.html', context)



@login_required(login_url='login')
def user_account(request):
    profile = request.user.profile

    top_skills = profile.skill_set.exclude(description__exact="")
    other_skills = profile.skill_set.filter(description="")
    projects = profile.project_set.all()
    context = {'profile':profile, 'top_skills':top_skills, 'other_skills':other_skills,
               'projects':projects}
    return render(request, 'users/account.html', context)



@login_required(login_url='login')
def edit_profile(request):
    user = request.user
    profile = user.profile
    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context = {'form':form}
    return render(request, 'users/edit-profile.html', context)




def login_user(request):
    page = 'login'

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return redirect('home')
    context = {'page':page}
    return render(request, 'users/login.html', context)



def logout_user(request):
    logout(request)
    return redirect('login')



def create_user(request):
    page = 'sign-up'
    form = CustomUserCreationForm()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.first_name = user.first_name.title()
            user.save()

            login(request, user)
            return redirect('home')
    context = {'page':page, 'form':form}
    return render(request, 'users/login.html', context)