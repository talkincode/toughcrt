#!/usr/bin/env python
#coding:utf-8
from hashlib import md5
from txweb import utils
from toughcrt.handlers.base import BaseHandler
from toughcrt.common import tools
from toughcrt import models
from txweb.permit import permit
from txweb import logger

@permit.route(r"/admin/login")
class LoginHandler(BaseHandler):

    def get(self):
        self.render("login.html",next = self.get_argument("next","/admin/dashboard"))

    def post(self):

        uname = self.get_argument("username")
        upass = self.get_argument("password")
        next_url = self.get_argument("next")
        print next_url

        if not uname:
            return self.render_json(code=1, msg=u"请填写用户名")
        if not upass:
            return self.render_json(code=1, msg=u"请填写密码")

        enpasswd = tools.saltmd5(upass.encode())

        opr = self.db.query(models.SysOperator).filter_by(
            operator_name=uname,
            operator_pass=enpasswd
        ).first()
        
        if not opr:
            return self.render_json(code=1, msg=u"用户名密码不符")

        if opr.operator_status == 1:
            return self.render_json(code=1, msg=u"该操作员账号已被停用")

        self.set_session_user(uname, self.request.remote_ip, opr.operator_type, utils.get_currtime())

        logger.info(u'操作员(%s)登陆' % (uname))
        self.db.commit()
        self.render_json(code=0, msg="ok", next=next_url)

