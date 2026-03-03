from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Project
from .forms import ProjectForm

# Create your views here.
def projects(request):
    projects = Project.objects.all()
    context = {'projects':projects}
    return render(request, 'projects/projects.html', context)


def project(request, pk):
    project = Project.objects.get(id=pk)
    context = {'project':project}
    return render(request, 'projects/project.html', context)


@login_required(login_url='login')
def create_project(request):
    form = ProjectForm()

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid:
            project = form.save(commit=False)
            project.owner = request.user
            form.save()
            return redirect('/')

    context = {'form':form}
    return render(request, 'projects/create-project.html', context)


@login_required(login_url='login')
def update_project(request, pk):
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)

    if request.user.profile != project.owner:
        return render(request, 'unauthorized.html')

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid:
            form.save()
            return redirect('project', project.id)

    context = {'form':form}
    return render(request, 'projects/create-project.html', context)


@login_required(login_url='login')
def delete_project(request, pk):
    project = Project.objects.get(id=pk)

    if request.user.profile != project.owner:
        return render(request, 'unauthorized.html')

    if request.method == "POST":
        project.delete()
        return redirect('/')
    context = {'object':project}
    return render(request, 'delete.html', context)