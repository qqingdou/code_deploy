# /usr/bin/python
# -*- coding:utf-8 -*-

import time
from ext.FabricHelper import *
from ext.Common import Common
from ext.UserAuth import UserAuth
from models.ProjectsModel import ProjectsModel
from models.BackupsModel import BackupsModel
from django.shortcuts import render
from django.http import HttpResponseRedirect

login_data = None


def check_login(request):
    """
    验证登录
    :param request:
    :return:
    """
    global login_data
    my_user_auth = UserAuth(request)
    login_data = my_user_auth.get()
    return login_data


def index(request):
    """
    后台首页
    :param request:
    :return:
    """
    if not check_login(request):
        return HttpResponseRedirect('/web_hook/login')

    return render(request, 'index.html')


def welcome(request):
    """
    欢迎页面
    :param request:
    :return:
    """
    if not check_login(request):
        return HttpResponseRedirect('/web_hook/login')

    return render(request, 'welcome.html')


def projects_list(request):
    """
    项目列表
    :param request:
    :return:
    """
    if not check_login(request):
        return HttpResponseRedirect('/web_hook/login')

    page = int(request.GET.get('page', '1'))
    page_size = int(request.GET.get('page_size', '10'))
    my_projects_mod = ProjectsModel()
    lists = my_projects_mod.fetch_all(fields='*',
                                      order='id DESC',
                                      limit=''.join((str((page - 1) * page_size), ',', str(page_size))))
    record_count = 0
    page_count_sql = my_projects_mod.fetch_one(fields='COUNT(1) AS my_count')
    if page_count_sql:
        record_count = int(page_count_sql['my_count'])

    return render(request, 'projects.html', {'lists': lists, 'record_count': record_count})


def project_action(request):
    """
    项目操作
    :param request:
    :return:
    """
    if request.method == 'POST':
        params = request.POST.dict()
        id_param = request.POST.get('id', '')
        my_projects_mod = ProjectsModel()
        del params['id']
        if not id_param:
            params['inserttime'] = time.time()
            result = my_projects_mod.add(params)
        else:
            params['updatetime'] = time.time()
            result = my_projects_mod.save({'id': id_param}, params)
        if not result:
            return Common.output_json(1, '系统错误')
        else:
            return Common.output_json(0, '操作成功')

    else:
        id_param = request.GET.get('id', '')
        if not id_param:
            return render(request, 'project_action.html')
        else:
            my_projects_mod = ProjectsModel()
            project_info = my_projects_mod.fetch_one('*', {'id': id_param})
            return render(request, 'project_action.html', {'project': project_info})


def to_test_env(request):
    """
    迁移到测试环境
    :param request:
    :return:
    """
    return render(request, 'to_test_env.html', {'id': request.GET.get('id', 0)})


def to_test_env_action(request):
    """
    迁移到测试环境操作
    :param request:
    :return:
    """
    if request.method == 'POST':
        id_param = int(request.POST.get('id', 0))
        if id_param <= 0:
            return Common.output_json(1, '参数错误')
        my_project_mod = ProjectsModel()
        project_info = my_project_mod.fetch_one(fields='*', condition={'id': id_param})
        if not project_info or project_info is None:
            return Common.output_json(1, '该项目不存在')

        deploy_result = deploy(project_info['develop_server_ip'], project_info['develop_server_dir'], project_info['develop_server_account'], project_info['test_server_ip'], project_info['test_server_dir'], project_info['test_server_account'])

        if not deploy_result:
            return Common.output_json(1, '发布失败')

        return Common.output_json(0, '操作成功')


def to_produce_env(request):
    """
    迁移到生产环境
    :param request:
    :return:
    """
    project_id = request.GET.get('id', 0)

    my_backup_mod = BackupsModel()
    lists = my_backup_mod.fetch_all('*', condition={'project_id': project_id}, order='id DESC')

    for item in lists:
        temp_time = time.localtime(int(item['inserttime']))
        item['inserttime'] = time.strftime("%Y-%m-%d %H:%M:%S", temp_time)

    return render(request, 'to_produce_env.html', {'id': project_id, 'lists': lists, 'record_count': len(lists)})


def to_produce_env_action(request):
    """
    迁移到生产环境操作
    :param request:
    :return:
    """
    if request.method == 'POST':
        id_param = int(request.POST.get('id', 0))
        if id_param <= 0:
            return Common.output_json(1, '参数错误')
        my_project_mod = ProjectsModel()
        project_info = my_project_mod.fetch_one(fields='*', condition={'id': id_param})
        if not project_info or project_info is None:
            return Common.output_json(1, '该项目不存在')

        # 先备份，再发布代码
        backup_result, backup_path = backup(
            project_info['produce_server_ip'],
            project_info['produce_server_dir'],
            project_info['produce_server_account'])

        if not isinstance(backup_result, int) and backup_result.failed:
            return Common.output_json(1, '备份失败，请解决备份问题在发布.')

        # 备份成功后，做日志记录
        if not isinstance(backup_result, int):

            my_backup_mod = BackupsModel()
            backup_data = {
                'project_id': id_param,
                'backup_file_path': backup_path,
                'inserttime': int(time.time()),
            }
            record_result = my_backup_mod.add(backup_data)

            if not record_result or record_result is None:
                return Common.output_json(1, '备份后记录日志失败，请检查.')

        deploy_result = deploy(project_info['test_server_ip'],
                               project_info['test_server_dir'],
                               project_info['test_server_account'],
                               project_info['produce_server_ip'],
                               project_info['produce_server_dir'],
                               project_info['produce_server_account'])

        if not deploy_result:
            return Common.output_json(1, '发布失败')

        return Common.output_json(0, '发布成功')


def project_rollback(request):
    """
    项目回滚
    :param request:
    :return:
    """
    if request.method == 'POST':

        backup_id = request.POST.get('id', 0)

        backup_mod = BackupsModel()

        backup_info = backup_mod.fetch_one(fields='*', condition={'id': backup_id})

        if backup_info is None:
            return Common.output_json(1, '该备份已经删除。')

        project_mod = ProjectsModel()

        project_info = project_mod.fetch_one(fields='*', condition={'id': backup_info['project_id']})

        if project_info is None:
            return Common.output_json(1, '该项目已经下架。')

        exec_result = rollback(project_info['produce_server_ip'],
                               project_info['produce_server_dir'],
                               project_info['produce_server_account'],
                               backup_info['backup_file_path'])

        if exec_result is None or exec_result.failed:
            return Common.output_json(1, '回滚失败。')

        return Common.output_json(0, '回滚成功。')

