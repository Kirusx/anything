# -*- coding:utf-8 -*-
from builtins import classmethod

from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from stronghold.decorators import public
from any.models import ProjectLog, ProjectGroup
from django.contrib.auth.models import User
from django.template import RequestContext, loader
# Create your views here.
import json
import yaml
import os.path
from kubernetes import client
from kubernetes.client.rest import ApiException

beta_api = client.AppsV1beta1Api()
v1api_ins = client.CoreV1Api()
extensions_v1beta1 = client.ExtensionsV1beta1Api()


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


def nodeinfo():
    node_info = v1api_ins.list_node().items
    node_info_dict = {}
    for item in node_info:
        node_info_dict[item.metadata.name] = {}
        node_info_dict[item.metadata.name]['status'] = item.status.conditions[3].type
        node_info_dict[item.metadata.name]['message'] = item.status.conditions[3].message
        node_info_dict[item.metadata.name]['create_timestamp'] = item.metadata.creation_timestamp
        node_info_dict[item.metadata.name]['node_ip'] = item.status.addresses[0].address
    return node_info_dict


def podinfo(namespace):
    pods_info = v1api_ins.list_namespaced_pod(namespace).items
    pods_info_dict = {}
    for item in pods_info:
        pods_info_dict[item.metadata.name] = {}
        pods_info_dict[item.metadata.name]['pod_ip'] = item.status.pod_ip
        pods_info_dict[item.metadata.name]['node_name'] = item.spec.node_name
        pods_info_dict[item.metadata.name]['status'] = item.status.phase
        pods_info_dict[item.metadata.name]['image'] = item.spec.containers[0].image
    return pods_info_dict


def namespaceinfo():
    namespace_info = v1api_ins.list_namespace().items
    namespace_info_list = []
    for item in namespace_info:
        namespace_info_list.append(item.metadata.name)
    return namespace_info_list


def indexinfo(namespace):
    deployment = beta_api.list_namespaced_deployment(namespace)

    node_info = v1api_ins.list_node()
    pods_info = v1api_ins.list_namespaced_pod(namespace)
    configmap = v1api_ins.list_namespaced_config_map(namespace)
    namespace_info = v1api_ins.list_namespace()

    request_dict = {
        'node_counts': len(node_info.items),
        'deployment_counts': len(deployment.items),
        'pod_counts': len(pods_info.items),
        'configmap_counts': len(configmap.items),
        'node_info': node_info.items,
        'namespace_info': namespace_info.items,
        'pods_info': pods_info.items
    }
    return request_dict


def index(request):
    if request.method == "POST":
        namespace = request.POST.get('namespace', default='default')
        ret_dict = indexinfo(namespace)
        return HttpResponse(ret_dict)
    else:
        ret_dict = indexinfo('default')
    return render(request, 'index.html', {'request_dict': ret_dict})


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


def user_info(request):
    response_res = {'result': None}
    if request.method == 'POST':
        uid = request.POST.get('uid')
        role = request.POST.get('role')
        stat = request.POST.get('stat')
        user_obj = User.objects.filter(id=uid).first()
        if uid and user_obj:
            User.objects.filter(id=uid).update(is_superuser=role)
            User.objects.filter(id=uid).update(is_active=stat)
        return HttpResponse(json.dumps(response_res))


def node_info(request):
    node_name = request.POST.get('node_name')
    node_status = v1api_ins.read_node_status(node_name)
    status_dict = {
        'name': node_status.metadata.name,
        'uid': node_status.metadata.uid,
        'cpu': node_status.status.capacity['cpu'],
        'memory': node_status.status.capacity['memory'],
        'pods': node_status.status.capacity['pods'],
        'ip': node_status.status.addresses[0].address,
        'kernel_version': node_status.status.node_info.kernel_version,
        'kube_proxy_version': node_status.status.node_info.kube_proxy_version,
        'kubelet_version': node_status.status.node_info.kubelet_version,
        'os': node_status.status.node_info.os_image,
    }
    return HttpResponse(json.dumps(status_dict))


def deployment(request):
    if request.method == 'POST':
        namespace = request.POST.get('namespace')
        deployment = beta_api.list_namespaced_deployment(namespace)
        if len(deployment.items) == 0:
            ret_data = None
        else:
            ret_data = {}
            for index, item in enumerate(deployment.items):
                ret_data[item.metadata.name] = {}
                ret_data[item.metadata.name]['id'] = index
                ret_data[item.metadata.name]['namespace'] = item.metadata.namespace
                ret_data[item.metadata.name]['ready_replicas'] = item.status.ready_replicas
                ret_data[item.metadata.name]['replicas'] = item.status.replicas
                ret_data[item.metadata.name]['updated_replicas'] = item.status.updated_replicas
                ret_data[item.metadata.name]['available_replicas'] = item.status.available_replicas
                ret_data[item.metadata.name]['image'] = item.spec.template.spec.containers[0].image
        return HttpResponse(json.dumps(ret_data))
    else:
        deployment = beta_api.list_namespaced_deployment('default')
        namespace = v1api_ins.list_namespace()
        return render(request, 'deployment.html', {'deployment': deployment.items, 'namespace': namespace.items})


def services(request):
    if request.method == 'POST':
        return HttpResponse('get')
    else:
        namespace = v1api_ins.list_namespace()
        service = v1api_ins.list_namespaced_service('default')
        return render(request, 'services.html', {'services': service.items, 'namespace': namespace.items})


def datatable(request):
    if request.method == 'POST':
        namespace = request.POST.get('namespace')
        deployment = beta_api.list_namespaced_deployment(namespace)
        if len(deployment.items) == 0:
            ret_data = None
        else:
            ret_data = {}
            for index, item in enumerate(deployment.items):
                ret_data[item.metadata.name] = {}
                ret_data[item.metadata.name]['id'] = index
                ret_data[item.metadata.name]['namespace'] = item.metadata.namespace
                ret_data[item.metadata.name]['ready_replicas'] = item.status.ready_replicas
                ret_data[item.metadata.name]['replicas'] = item.status.replicas
                ret_data[item.metadata.name]['updated_replicas'] = item.status.updated_replicas
                ret_data[item.metadata.name]['available_replicas'] = item.status.available_replicas
                ret_data[item.metadata.name]['image'] = item.spec.template.spec.containers[0].image
        return HttpResponse(json.dumps(ret_data))
    else:
        return HttpResponse(None)


def deployment_opt(request, action_name):
    action_dict = {
        'update': extensions_v1beta1.patch_namespaced_deployment,
        'scaleup': extensions_v1beta1.patch_namespaced_deployment_scale,
        'scaledown': extensions_v1beta1.patch_namespaced_deployment_scale,
        'delete': extensions_v1beta1.delete_namespaced_deployment
    }
    if request.method == 'POST':
        action = request.POST.get('action').lower()
        name = request.POST.get('deploymentname')
        namespace = request.POST.get('deploymentnamespace')
        image = request.POST.get('deploymentimage')
        if action in action_dict:
            deployment_ins = extensions_v1beta1.read_namespaced_deployment(name, namespace)
            if action == 'update':
                deployment_ins.spec.template.spec.containers[0].image = image
                action_dict[action](name=name, namespace=namespace, body=deployment_ins)
            elif action == 'delete':
                delete_opt = client.V1DeleteOptions(propagation_policy='Foreground', grace_period_seconds=3)
                extensions_v1beta1.delete_namespaced_deployment(name, namespace, body=delete_opt)
            elif action == 'scaleup':
                deployment_ins.spec.replicas += 1
                extensions_v1beta1.patch_namespaced_deployment_scale(name, namespace, body=deployment_ins)
            elif action == 'scaledown':
                deployment_ins.spec.replicas -= 1
                extensions_v1beta1.patch_namespaced_deployment_scale(name, namespace, body=deployment_ins)
            return HttpResponse(json.dumps({'success': action + ' ' + name + ' success'}))
        else:
            return HttpResponse(json.dumps({'error': action + ' does not support'}))
    else:
        return HttpResponse(status=404)


def create_deployment(request):
    resouce_dict = {
        'Deployment': extensions_v1beta1.create_namespaced_deployment,
        'Service': v1api_ins.create_namespaced_service
    }
    if request.method == 'POST':
        file = request.FILES.get('deployment-file')
        from anything.settings import UPLOAD_DIR
        save_file = os.path.join(UPLOAD_DIR, file.name)
        with open(save_file, 'wb+') as dest_file:
            for chunk in file.chunks():
                dest_file.write(chunk)
        with open(save_file) as deployment_file:
            dep = yaml.load(deployment_file)
        if dep['kind'] in resouce_dict:
            if 'namespace' in dep['metadata'].keys():
                namespace = dep['metadata']['namespace']
            else:
                namespace = 'default'
            try:
                resouce_dict[dep['kind']](body=dep, namespace=namespace)
                return redirect('/create/deployment')
            except ApiException as e:
                reason = json.loads(e.body)
                return render(request, 'upload.html', {'msg': reason['message']})
        else:
            return render(request, 'upload.html', {'msg': "%s does not support." % dep['kind']})
    else:
        return render(request, 'upload.html')
