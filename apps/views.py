# /usr/bin/python
# -*- coding:utf-8 -*-

import json
import logging
import hashlib
import ext.Config as Config
from ext.Common import Common
from ext.Captcha import Captcha
from models.UsersModel import UsersModel
from ext.UserAuth import UserAuth
from django.http import HttpResponse
from django.shortcuts import render
from ext.FabricHelper import git_to_develop
from models.ProjectsModel import ProjectsModel

# Create your views here.

# 日志组件
logger = logging.getLogger(__name__)


def login(request):
    """
    登录UI和登录操作
    :param request:
    :return:
    """
    my_captcha = Captcha(request)

    if request.method == 'POST':

        account = str(request.POST.get('account'))
        pwd = str(request.POST.get('password'))
        check_code_p = str(request.POST.get('check_code'))

        if not my_captcha.validate(check_code_p):
            return Common.output_json(1, '验证码输入错误')
        else:
            temp_my_sql = UsersModel()
            user = temp_my_sql.fetch_one('*', {'email': account})
            if user is None:
                return Common.output_json(1, '该帐号不存在')
            if hashlib.md5(''.join((pwd, Config.SQL_PWD_KEY))).hexdigest() != user['password']:
                return Common.output_json(1, '密码错误')
            my_user_auth = UserAuth(request)
            my_user_auth.set(user)
            return Common.output_json(0, 'success')

    else:
        my_captcha = Captcha(request)
        my_captcha.type = 'number'
        check_display = my_captcha.display()
        check_display = ''.join(('data:image/gif;base64,', check_display))
        return render(request, 'login.html', {'code': check_display})


def check_code(request):
    """
    生成验证码
    :param request:
    :return:
    """
    my_captcha = Captcha(request)
    my_captcha.type = 'number'
    check_display = my_captcha.display()
    return HttpResponse(123)


def push(request):
    """
    GIT WEB钩子触发事件
    :param request:
    :return:
    """
    if request.method == 'POST':

        '''记录POST日志'''
        logger.debug(request.body)

        body_unicode = request.body.decode('utf-8')
        post_content = json.loads(body_unicode)

        if post_content is None:
            return HttpResponse('没有捕获到POST数据.')

        if post_content['ref'] != 'refs/heads/master':
            return HttpResponse('只有master分支才触发推送操作.')

        git_ssh_url = post_content['project']['git_ssh_url']

        projects_mod = ProjectsModel()
        project_info = projects_mod.fetch_one(fields='*', condition={'git_http_url': git_ssh_url})

        if project_info is None:
            return HttpResponse('该GIT没有配置信息.')

        git_info = git_ssh_url.split(':')

        base_git_data_dir = '/var/opt/gitlab/git-data/repositories/'

        code_dir = base_git_data_dir + git_info[1]

        logger.debug(code_dir)

        commit_result = git_to_develop(code_dir,
                                       post_content['after'],
                                       post_content['before'],
                                       project_info['develop_server_ip'],
                                       project_info['develop_server_dir'],
                                       project_info['develop_server_account'])

        logger.debug(commit_result)

        if not commit_result:
            return HttpResponse('提交到开发环境失败.')

        return HttpResponse('提交成功.')

    else:
        return HttpResponse('非法请求方式.')