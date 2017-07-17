# /usr/bin/python
# -*- coding:utf-8 -*-
from apps.ext.MySQL import MySQL


class BackupsModel(MySQL):
    table = 'rc_backups'

    def __init__(self):
        MySQL.__init__(self)

