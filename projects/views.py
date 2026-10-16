from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import json

from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from .utils import search_projects, paginateProjects

# Create your views here.
def projects(request):
    projects = Project.objects.all()

    #The search projects function
    projects, search_query = search_projects(request)

    #The paginator function goes here
    projects, paginator = paginateProjects(request, projects, 3)
    
    context = {'projects':projects, 'search_query':search_query, 'paginator':paginator}
    return render(request, 'projects/projects.html', context)


def project(request, pk):
    project = get_object_or_404(Project, id=pk)
    reviews = project.review_set.all()
    
    form = ReviewForm()
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url='login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user.profile
            review.project = project
            review.save()

            project.updateVote()
            return redirect('project', project.id)


    context = {'project':project, 'form':form, 'reviews':reviews,}
    return render(request, 'projects/project.html', context)


@login_required(login_url='login')
def create_project(request):
    form = ProjectForm()

    if request.method == "POST":
        newtags = request.POST['newtags'].replace(',', ' ').split()

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user.profile
            form.save()

            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
                messages.success(request, "Project successfully created!")
            return redirect('account')

    context = {'form':form}
    return render(request, 'projects/create-project.html', context)


@login_required(login_url='login')
def update_project(request, pk):
    project = get_object_or_404(Project, id=pk)
    form = ProjectForm(instance=project)

    if request.user.profile != project.owner:
        return render(request, 'unauthorized.html')

    if request.method == "POST":
        newtags = request.POST['newtags'].replace(',', ' ').split()

        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()

            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)

            messages.success(request, "Project updated!")
            return redirect('project', project.id)

    context = {'form':form, 'project':project}
    return render(request, 'projects/create-project.html', context)


@login_required(login_url='login')
def delete_project(request, pk):
    project = get_object_or_404(Project, id=pk)

    if request.user.profile != project.owner:
        return render(request, 'unauthorized.html')

    if request.method == "POST":
        project.delete()
        messages.info(request, "Project deleted!")
        return redirect('account')
    context = {'object':project}
    return render(request, 'delete.html', context)


@login_required(login_url='login')
@require_POST
def remove_tag(request):
    data = json.loads(request.body)
    project = get_object_or_404(Project, id=data['project'], owner=request.user.profile)
    tag = get_object_or_404(Tag, id=data['tag'])
    project.tags.remove(tag)
    return JsonResponse({'removed': True})
