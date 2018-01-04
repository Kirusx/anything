# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.contrib import auth
from stronghold.decorators import public
from any.models import ProjectLog, ProjectGroup
from django.contrib.auth.models import User
# Create your views here.
import json

@public
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            return redirect('/home')
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def user_logout(request):
    auth.logout(request)
    return redirect('/login')


def index(request):
    return render(request, 'index.html', {'user': request.user})


def home(request):
    project_list = ProjectLog.objects.all()
    return render(request, 'home.html', {'project_list': project_list})


def groups(request):
    group_list = ProjectGroup.objects.all()
    return render(request, 'group.html', {'group_list': group_list})


def group_add(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        project_name = request.POST.get('project_name')
        project_user = request.POST.get('project_user')
        print(group_name, project_name, project_user)
        return redirect('/group_add')
    else:
        project_list = ProjectLog.objects.all()
        user_list = User.objects.all()
        return render(request, 'group_add.html', {'project_list': project_list, 'user_list': user_list})

