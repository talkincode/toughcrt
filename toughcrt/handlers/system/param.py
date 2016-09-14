#!/usr/bin/env python
# coding=utf-8

from toughcrt.handlers.base import BaseHandler,MenuSys
from txweb.permit import permit
from toughcrt import models
from toughcrt.handlers.base import authenticated
from toughcrt.handlers.system import param_forms
from txweb import dispatch,redis_cache,logger

@permit.route("/admin/param", u"系统参数管理", MenuSys, is_menu=True, order=2.0005)
class ParamHandler(BaseHandler):

    @authenticated
    def get(self):
        active = self.get_argument("active","syscfg")
        sys_form = param_forms.sys_form()
        fparam = {}
        for p in self.db.query(models.SysParam):
            fparam[p.param_name] = p.param_value

        for form in (sys_form,):
            form.fill(fparam)

        return self.render("param.html",
                      active=active,
                      sys_form=sys_form)


@permit.route("/admin/param/update", u"系统参数更新", MenuSys, order=2.0006)
class ParamUpdateHandler(BaseHandler):

    @authenticated
    def post(self):
        active = self.get_argument("active", "syscfg")
        for param_name in self.get_params():
            if param_name in ("active", "submit"):
                continue

            param = self.db.query(models.SysParam).filter_by(param_name=param_name).first()
            if not param:
                param = models.SysParam()
                param.param_name = param_name
                param.param_value = self.get_argument(param_name)
                self.db.add(param)
            else:
                param.param_value = self.get_argument(param_name)

            dispatch.pub(redis_cache.CACHE_SET_EVENT,param.param_name,param.param_value,600)

        logger.info(u'操作员(%s)修改参数' % (self.current_user.username))
        self.db.commit()
        self.redirect("/admin/param?active=%s" % active)
