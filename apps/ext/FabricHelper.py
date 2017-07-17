# /usr/bin/python
# -*- coding:utf-8 -*-

import time
import os
import logging
from datetime import datetime
from fabric.api import *

# 接口为22的服务器列表
hosts_22 = ['192.168.0.55']

logger = logging.getLogger(__name__)

env.key_filename = '/root/.ssh/id_rsa.pub'


def get_port(server_ip):
    """
    获取端口号
    :param server_ip:
    :return:
    """
    if server_ip in hosts_22:
        return 22
    return 20755


def git_to_develop(git_dir, after_commit_id, before_commit_id, develop_server_ip, develop_server_dir, develop_server_account):
    """
    每次提交上传GIT代码到开发环境
    :param git_dir:
    :param after_commit_id:
    :param before_commit_id:
    :param develop_server_ip:
    :param develop_server_dir:
    :param develop_server_account:
    :return:
    """
    curr_time = datetime.now()
    tar_file = curr_time.strftime("%Y_%m_%d_%H_%M_%S_%f") + '.tar.gz'
    local_file = '/tmp/' + tar_file

    logger.debug(local_file)

    with lcd(git_dir):

        # 打包增量文件并且过滤删除的文件列表
        with settings(warn_only=True):
            result = local('git archive -o ' + local_file + ' HEAD $(git diff ' + before_commit_id + ' ' + after_commit_id + ' --name-only --diff-filter=ACM)')

            logger.debug(result)

        if not os.path.exists(local_file):
            return False

        if os.path.getsize(local_file) <= 0:
            return False

    env.user = develop_server_account
    env.host_string = develop_server_ip
    env.port = get_port(develop_server_ip)

    # 先试探，如果失败的话，重启UWSGI
    with settings(warn_only=True):
        try:
            cd(develop_server_dir)
        except:
            os.system('/bin/sh /home/huowu/start.sh')

    with cd(develop_server_dir):

        try:
            result = put(local_file, tar_file)
        except:
            # 报错后执行命令，重启uwsgi
            os.system('/bin/sh /home/huowu/start.sh')
            # 如果失败的话，重试一次
            result = put(local_file, tar_file)

        logger.debug(result)

        with settings(warn_only=True):
            result = run('tar -zxvf ' + tar_file)

            logger.debug(result)

        result = run('rm ' + tar_file)

        logger.debug(result)

    local('rm ' + local_file)

    return True


def backup(server_ip, server_dir, server_account):
    """
    备份
    :param server_ip:
    :param server_dir:
    :param server_account:
    :return:
    """
    env.user = server_account
    env.host_string = server_ip
    env.port = get_port(server_ip)

    curr_time = datetime.now()
    backup_dir = '/data/huowu/backup'
    tar_file = curr_time.strftime("%Y_%m_%d_%H_%M_%S_%f") + '.tar.gz'
    tar_file_full_path = backup_dir + '/' + tar_file

    with settings(warn_only=True):
        run('mkdir ' + backup_dir)

    remote_result = None

    with cd(server_dir):
        list_result = run('ls | wc -l')   # 存在目录或者文件
        stat_count = int(list_result.stdout)
        if not list_result.failed and stat_count <= 0:
            return stat_count, tar_file_full_path

        remote_result = run('tar -zcf ' + tar_file_full_path + ' * ')

    return remote_result, tar_file_full_path


def deploy(from_server_ip, from_server_dir, from_server_account,
           to_server_ip, to_server_dir, to_server_account):
    """
    发布代码
    :param from_server_ip:
    :param from_server_dir:
    :param from_server_account:
    :param to_server_ip:
    :param to_server_dir:
    :param to_server_account:
    :param backup:
    :return:
    """

    curr_time = datetime.now()
    tar_file = curr_time.strftime("%Y_%m_%d_%H_%M_%S_%f") + '.tar.gz'

    env.user = from_server_account
    env.host_string = from_server_ip
    env.port = get_port(from_server_ip)

    with cd(from_server_dir):
        result = run('tar -zcf ' + tar_file + ' * ')

        logger.debug(result)

        result = get(tar_file, tar_file)

        logger.debug(result)

        result = run('rm ' + tar_file)

        logger.debug(result)

    env.user = to_server_account
    env.host_string = to_server_ip
    env.port = get_port(to_server_ip)

    with cd(to_server_dir):
        result = put(tar_file, tar_file)

        logger.debug(result)

        result = run('tar -zxvf ' + tar_file)

        logger.debug(result)

        result = run('rm ' + tar_file)

        logger.debug(result)

    result = local('rm ' + tar_file)

    logger.debug(result)

    return True


def rollback(server_ip, server_dir, server_account, file_path):
    """
    代码回滚
    :param server_ip:
    :param server_dir:
    :param server_account:
    :param file_path:
    :return:
    """
    env.user = server_account
    env.host_string = server_ip
    env.port = get_port(server_ip)

    execute_result = None

    with cd(server_dir):
        execute_result = run('tar -zxvf ' + file_path)

    return execute_result


