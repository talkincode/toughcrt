#!/usr/bin/env python
#coding:utf-8

from toughcrt.handlers.base import BaseHandler,MenuSys
from toughcrt.handlers.base import authenticated
from txweb.permit import permit
from toughcrt import models
import psutil

@permit.route(r"/")
class HomeHandler(BaseHandler):
    @authenticated
    def get(self):
        self.redirect("/admin/dashboard")


@permit.route(r"/admin")
class HomeHandler(BaseHandler):
    @authenticated
    def get(self):
        self.redirect("/admin/dashboard")        

@permit.route(r"/admin/dashboard")
class DashboardHandler(BaseHandler):

    @authenticated
    def get(self):
        cpuuse = psutil.cpu_percent(interval=None, percpu=True)
        memuse = psutil.virtual_memory()
        self.render("index.html",config=self.gdata.config,
            cpuuse=cpuuse,memuse=memuse)


