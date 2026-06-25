from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Profile, Skill, Message
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .utils import search_profiles, paginateProfiles


# Create your views here.
def home(request):
    profiles = Profile.objects.all()

    #The search developers function
    profiles, search_query = search_profiles(request)

    #The paginator goes here
    profiles, paginator = paginateProfiles(request, profiles, 3)

    context = {'profiles':profiles, 'search_query':search_query, 'paginator':paginator}
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

    skills = profile.skill_set.all()
    projects = profile.project_set.all()
    context = {'profile':profile, 'skills':skills, 'projects':projects}
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



def login_user(request):
    page = 'login'

    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return redirect(request.GET['next'] if 'next' in request.GET else 'account')
    context = {'page':page}
    return render(request, 'users/login.html', context)



def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def create_skill(request):
    profile = request.user.profile
    form = SkillForm()
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            form.save()
            return redirect('account')
    context = {'form':form}
    return render(request, 'users/skill-form.html', context)


@login_required(login_url='login')
def update_skill(request, pk):
    page = 'update-skill'
    skill = Skill.objects.get(id=pk)
    form = SkillForm(instance=skill)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            return redirect('account')
    context = {'form':form, 'page':page}
    return render(request, 'users/skill-form.html', context)


@login_required(login_url='login')
def delete_skill(request, pk):
    skill = Skill.objects.get(id=pk)
    if request.method == "POST":
        skill.delete()
        return redirect('account')
    context = {'object':skill}
    return render(request, 'delete.html', context)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    message_requests = profile.messages.all() #not using messages because of flash message
    unreadCount = message_requests.filter(is_read=False).count()
    context = {'message_requests':message_requests, 'unreadCount':unreadCount}
    return render(request, "users/inbox.html", context)


@login_required(login_url='login')
def view_message(request, pk):
    message = Message.objects.get(id=pk)
    message.is_read = True
    message.save()
    context = {'message':message}
    return render(request, "users/message.html", context)


def create_message(request, pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    try:
        sender = request.user.profile

    except:
        sender = None

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.email = sender.email
                message.name = sender.name
            message.save()

            messages.success(request, 'Your message was successfully sent!')
            return redirect('profile', pk=recipient.id)
    context = {'form':form, 'recipient':recipient}
    return render(request, "users/message-form.html", context)