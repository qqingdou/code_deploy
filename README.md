# code_deploy
代码自动部署

步骤一

启动该项目，可以直接runserver 或者 uwsgi

步骤二

在gitlab的项目里面找到CI，然后在地址里面输入你部署的项目地址：

如：http://192.168.0.54:8080/web_hook/push

备注：可根据实际修改。

勾选 push

步骤三

访问项目，然后添加对应的项目信息。

如：http://192.168.0.54:8080/web_hook/login
