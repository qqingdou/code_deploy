# /usr/bin/python
# -*- coding:utf-8 -*-


"""
用户授权类
"""
class UserAuth(object):
    def __init__(self, request):
        self.django_request = request
        self.session_key = 'login_auth'  # request.session.session_key
        self.auth_key = '8734718fef6e7fb91fdbdc4d14f04c69'

    def set(self, data):
        self.django_request.session[self.session_key] = data

    def check(self):
        login_data = self.get()
        return not login_data

    def get(self):
        return self.django_request.session.get(self.session_key) or ''
