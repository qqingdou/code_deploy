# /usr/bin/python
# -*- coding:utf-8 -*-
from apps.ext.MySQL import MySQL


class ProjectsModel(MySQL):
    table = 'rc_projects'

    def __init__(self):
        MySQL.__init__(self)

