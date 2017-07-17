# /usr/bin/python
# -*- coding:utf-8 -*-

from apps.ext.MySQL import MySQL


class UsersModel(MySQL):
    table = 'rc_users'

    def __init__(self):
        MySQL.__init__(self)

