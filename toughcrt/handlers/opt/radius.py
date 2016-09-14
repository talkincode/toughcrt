#!/usr/bin/env python
# coding:utf-8

#!/usr/bin/env python
# coding:utf-8
import time
import cyclone.sse
import cyclone.web
import msgpack
import itertools
from txweb import utils
from toughcrt.handlers.base import BaseHandler, MenuOpt
from toughcrt.handlers.base import authenticated
from txweb.permit import permit
from toughcrt import models
from toughlib.btforms.rules import is_number
from twisted.internet import defer, reactor
from toughcrt import models
from toughcrt.handlers.opt import radius_form


@permit.route(r"/admin/radius", u"RADIUS 节点管理", MenuOpt, order=1.0000, is_menu=True)
class RadiusHandler(BaseHandler):
    @authenticated
    def get(self):
        radius_list = self.db.query(models.SysRadius)
        self.render("radius.html",radius_list=radius_list)


@permit.route(r"/admin/radius/add", u"RADIUS 节点新增", MenuOpt, order=1.0003)
class AddHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render("base_form.html", form=radius_form.radius_add_form())

    @authenticated
    def post(self):
        form = radius_form.radius_add_form([])
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)

        if self.db.query(models.SysRadius.id).filter_by(ip_addr=form.d.ip_addr).count() > 0:
            return self.render("base_form.html", form=form, msg=u"ip地址已经存在")

        radius = models.SysRadius()
        radius.ip_addr = form.d.ip_addr
        radius.name = form.d.name
        radius.secret = form.d.secret
        radius.acct_port = form.d.acct_port
        radius.auth_port = form.d.auth_port
        self.db.add(radius)
        self.db.commit()
        self.redirect("/admin/radius", permanent=False)


@permit.route(r"/admin/radius/update", u"RADIUS 节点修改", MenuOpt, order=1.0004)
class UpdateHandler(BaseHandler):
    @authenticated
    def get(self):
        radius_id = self.get_argument("radius_id")
        radius = self.db.query(models.SysRadius).get(radius_id)
        form = radius_form.radius_update_form()
        form.fill(radius)
        return self.render("base_form.html", form=form)

    def post(self):
        form = radius_form.radius_update_form([])
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)

        radius = self.db.query(models.SysRadius).get(form.d.id)
        radius.ip_addr = form.d.ip_addr
        radius.name = form.d.name
        radius.secret = form.d.secret
        radius.acct_port = form.d.acct_port
        radius.auth_port = form.d.auth_port
        self.db.commit()
        self.redirect("/admin/radius", permanent=False)


@permit.route(r"/admin/radius/delete", u"Radius节点删除", MenuOpt, order=1.0005)
class RadiusDeleteHandler(BaseHandler):
    @authenticated
    def get(self):
        radius_id = self.get_argument("radius_id")
        ip_addr = self.db.query(models.SysRadius.ip_addr).filter_by(id=radius_id).scalar()
        self.db.query(models.SysRadius).filter_by(id=radius_id).delete()
        self.db.commit()
        self.redirect("/admin/radius",permanent=False)




