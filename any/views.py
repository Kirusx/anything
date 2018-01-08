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
    project_list = ProjectLog.objects.all()
    user_list = User.objects.all()
    return render(request, 'group.html', {'group_list': group_list, 'project_list': project_list, 'user_list': user_list})


def group_add(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        project_name = request.POST.getlist('project_name')
        project_user = request.POST.getlist('project_user')
        group_obj = ProjectGroup.objects.filter(group_name=group_name)
        if not group_obj:
            group_obj = ProjectGroup.objects.create(group_name=group_name)
            for name in project_name:
                group_obj.log.add(ProjectLog.objects.filter(project_name=name).first().project_id)
            for user in project_user:
                group_obj.user.add(User.objects.filter(username=user).first().id)
        else:
            for group in group_obj:
                for name in project_name:
                    group.log.add(ProjectLog.objects.filter(project_name=name).first().project_id)
                for user in project_user:
                    group.user.add(User.objects.filter(username=user).first().id)
        return HttpResponse(json.dumps('GET'))
    else:
        project_list = ProjectLog.objects.all()
        user_list = User.objects.all()
        return render(request, 'group_add.html', {'project_list': project_list, 'user_list': user_list})

