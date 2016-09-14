#!/usr/bin/env python
# coding:utf-8

import cyclone.web
from txweb import utils
from toughcrt.handlers.base import BaseHandler, MenuOpt
from toughcrt.handlers.base import authenticated
from txweb.permit import permit
from toughcrt.handlers.opt import account_form
from toughcrt import models

@permit.route(r"/admin/account", u"测试账号管理", MenuOpt, order=2.0000, is_menu=True)
class AccountListHandler(BaseHandler):
    @authenticated
    def get(self):
        userlist = self.db.query(models.TTAccount)
        self.render("account_list.html",userlist=userlist)

@permit.route(r"/admin/account/add", u"测试账号新增", MenuOpt, order=2.0001)
class AccountAddHandler(BaseHandler):
    @authenticated
    def get(self):
        form = account_form.account_add_form()
        self.render("base_form.html",form=form)

    def post(self):
        form = account_form.account_add_form()
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)

        if self.db.query(models.TTAccount).filter_by(username=form.d.username).count() > 0:
            return self.render("base_form.html", form=form, msg=u"账号已经存在")

        account = models.TTAccount()
        account.username = form.d.username
        account.password = form.d.password
        self.db.add(account)
        self.db.commit()
        self.redirect("/admin/account", permanent=False)

@permit.route(r"/admin/account/delete", u"测试账号删除", MenuOpt, order=2.0002)
class AccountDeleteHandler(BaseHandler):
    @authenticated
    def get(self):
        username = self.get_argument("username")
        self.db.query(models.TTAccount).filter_by(username=username).delete()
        self.db.commit()
        self.redirect("/account",permanent=False)






