# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.contrib import auth, sessions
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
            return redirect('/')
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def user_logout(request):
    auth.logout(request)
    return redirect('/login')


def index(request):
    return render(request, 'index.html', {'user': request.user})


def users_list(request):
    user_list = User.objects.all()
    return render(request, 'user_list.html', {'user_list': user_list})


def project_list(request):
    project_list = ProjectLog.objects.all()
    return render(request, 'project_list.html', {'project_list': project_list})


def groups_list(request):
    group_list = ProjectGroup.objects.all()
    project_list = ProjectLog.objects.all()
    user_list = User.objects.all()
    return render(request, 'group_list.html', {'group_list': group_list, 'project_list': project_list, 'user_list': user_list})


def group_add(request):
    response_res = {'result': None}
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
            response_res['result'] = 'success'
            response_res['data'] = 'create ' + group_obj.group_name
        else:
            for group in group_obj:
                for name in project_name:
                    group.log.add(ProjectLog.objects.filter(project_name=name).first().project_id)
                for user in project_user:
                    group.user.add(User.objects.filter(username=user).first().id)
            response_res['result'] = 'success'
        return HttpResponse(json.dumps(response_res))
    else:
        project_list = ProjectLog.objects.all()
        user_list = User.objects.all()
        return render(request, 'group_add.html', {'project_list': project_list, 'user_list': user_list})


def group_query(request):
    project_list = []
    user_list = []
    data_dict = {}
    if request.method == 'POST':
        dept_name = request.POST.get('dept_name')
        dept_group_id = ProjectGroup.objects.filter(group_name=dept_name).first().group_id
        project_obj = ProjectLog.objects.filter(projectgroup__group_id__exact=dept_group_id).values('project_name')
        for project in project_obj:
            project_list.append(project['project_name'])
        user_obj = User.objects.filter(projectgroup__group_id__exact=dept_group_id).values('username')
        for user in user_obj:
            user_list.append(user['username'])
        data_dict['dept_id'] = str(dept_group_id)
        data_dict['project_list'] = project_list
        data_dict['user_list'] = user_list
        return HttpResponse(json.dumps(data_dict))
    else:
        return HttpResponse(status=403)


def group_modify(request):
    response_res = {'result': None}
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group_name = request.POST.get('new_group_name')
        project_name = request.POST.getlist('new_project_name')
        project_user = request.POST.getlist('new_project_user')
        group_obj = ProjectGroup.objects.filter(group_id=group_id).first()
        if group_id and group_obj:
            ProjectGroup.objects.filter(group_id=group_id).update(group_name=group_name)
            group_obj.log.clear()
            group_obj.user.clear()
            for name in project_name:
                group_obj.log.add(ProjectLog.objects.filter(project_name=name).first().project_id)
            for user in project_user:
                group_obj.user.add(User.objects.filter(username=user).first().id)
            response_res['result'] = 'success'
        return HttpResponse(json.dumps(response_res))
    else:
        return HttpResponse(status=403)


def group_del(request):
    response_res = {'result': None}
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group_obj = ProjectGroup.objects.filter(group_id=group_id).first()
        if group_id and group_obj:
            group_obj.log.clear()
            group_obj.user.clear()
            ProjectGroup.objects.filter(group_id=group_id).delete()
            response_res['result'] = 'success'
        return HttpResponse(json.dumps(response_res))
