#!/usr/bin/env python
#coding:utf-8
from toughcrt.handlers.base import BaseHandler
from txweb.permit import permit

@permit.route(r"/admin/logout")
class LogoutHandler(BaseHandler):

    def get(self):
        if not self.current_user:
            self.redirect("/admin/login")
            return
        self.clear_session()
        self.redirect("/admin/login",permanent=False)


