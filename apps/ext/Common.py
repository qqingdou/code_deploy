# /usr/bin/python
# -*- coding:utf-8 -*-

import json
from UserAuth import UserAuth
from django.http import HttpResponse,HttpResponseRedirect

class Common:

    def __init__(self):
        pass

    @staticmethod
    def output_json(code=0, message='操作成功'):
        result = json.dumps({"code": code, "msg": message})
        return HttpResponse(result)

