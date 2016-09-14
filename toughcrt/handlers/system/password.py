#!/usr/bin/env python
# coding:utf-8

from hashlib import md5
from txweb import utils,logger
from toughcrt.handlers.base import MenuSys
from toughcrt.handlers.base import BaseHandler
from txweb.permit import permit
from toughcrt import models
from toughcrt.common import tools
from toughcrt.handlers.base import authenticated
from toughcrt.handlers.system import password_forms


@permit.route(r"/admin/password", u"密码修改", MenuSys, order=1.0100, is_menu=False)
class PasswordUpdateHandler(BaseHandler):

    @authenticated
    def get(self):
        form = password_forms.password_update_form()
        form.fill(tr_user=self.current_user.username)
        return self.render("base_form.html", form=form)

    @authenticated
    def post(self):
        form = password_forms.password_update_form()
        if not form.validates(source=self.get_params()):
            self.render("base_form.html", form=form)
            return
        if form.d.tr_user_pass != form.d.tr_user_pass_chk:
            self.render("base_form.html", form=form, msg=u'确认密码不一致')
            return
        opr = self.db.query(models.SysOperator).filter_by(operator_name=form.d.tr_user).first()
        opr.operator_pass = tools.saltmd5(form.d.tr_user_pass)

        logger.info(u'修改%s密码 ' % (self.current_user.username))

        self.db.commit()
        self.redirect("/admin")


