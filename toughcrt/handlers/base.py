#!/usr/bin/env python
#coding:utf-8
import json
import re
import os
import urlparse
import urllib
import traceback
import cyclone.auth
import cyclone.escape
import cyclone.web
import tempfile
import traceback
import functools
from urllib import urlencode
from cyclone.util import ObjectDict
from txweb import utils, apiutils
from txweb.web import BaseHandler as BasicHandler
from txweb.apiutils import apistatus
from txweb.permit import permit
from txweb import dispatch,logger
from txweb import redis_session
from toughcrt import __version__
from toughcrt import models
from toughcrt.common import tools
from twisted.internet import defer
from txweb.paginator import Paginator



ADMIN_MENUS = (MenuSys, MenuRes, MenuOpt, MenuStat) = (
    u"系统管理", u"资源管理", u"测试管理", u"统计分析")

MENU_ICONS = {
    u"系统管理": "fa fa-cog",
    u"服务管理": "fa fa-desktop",
    u"测试管理": "fa fa-wrench",
    u"统计分析": "fa fa-bar-chart"
}

def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                self.set_header('Content-Type', 'application/json; charset=UTF-8')
                self.write(json.dumps({'code': 1, 'msg': 'session expire'}))
                return
            if self.request.method in ("GET", "POST", "HEAD"):
                return self.redirect("/admin/login")
            return self.render_error(msg=u"Unauthorized access")
        else:
            if not self.current_user.permit.match(self.current_user.username,self.request.path):
                return self.render_error(msg="Unauthorized access")
            return method(self, *args, **kwargs)
    return wrapper


class BaseHandler(BasicHandler):

    
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.cache = self.gdata.cache
        self.aes = self.gdata.aes
        self.tp_lookup = self.gdata.tp_lookup
        self.db_backup = self.gdata.db_backup
        self.session = redis_session.Session(self.gdata.session_manager, self)

    def initialize(self):
        self.db = self.application.gdata.db()

    def on_finish(self):
        self.db.close()
        
    def get_error_html(self, status_code=500, **kwargs):
        if 'exception' in kwargs:
            failure = kwargs.get("exception")
            logger.exception(failure,trace="admin")
            if os.environ.get("XDEBUG"):
                from mako import exceptions
                return  exceptions.html_error_template().render(traceback=failure.getTracebackObject())
        # print repr(exception.getTraceback())
        try:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return self.render_json(code=1, msg=u"%s:服务器处理失败，请联系管理员" % status_code)

            if status_code == 404:
                return self.render_string("error.html", msg=u"404:页面不存在")
            elif status_code == 403:
                return self.render_string("error.html", msg=u"403:非法的请求")
            elif status_code == 500:
                return self.render_string("error.html", msg=u"500:服务器处理失败，请联系管理员")
            else:
                return self.render_string("error.html", msg=u"%s:服务器处理失败，请联系管理员" % status_code)
        except:
            import traceback
            traceback.print_exc()
            return self.render_string("error.html", msg=u"%s:服务器处理失败，请联系管理员" % status_code)

    def render(self, template_name, **template_vars):
        html = self.render_string(template_name, **template_vars)
        self.write(html)

    def render_error(self, **template_vars):
        tpl = "error.html"
        html = self.render_string(tpl, **template_vars)
        self.write(html)

    def render_json(self, **template_vars):
        if not template_vars.has_key("code"):
            template_vars["code"] = 0
        resp = json.dumps(template_vars, ensure_ascii=False)
        self.write(resp)


    def render_string(self, template_name, **template_vars):
        template_vars["xsrf_form_html"] = self.xsrf_form_html
        template_vars["current_user"] = self.current_user
        template_vars["static_url"] = self.gdata.config.web.static_url
        template_vars["login_time"] = self.get_secure_cookie("tr_login_time")
        template_vars["request"] = self.request
        template_vars["requri"] = "{0}://{1}".format(self.request.protocol, self.request.host)
        template_vars["handler"] = self
        template_vars["utils"] = utils
        template_vars["tools"] = tools
        template_vars["gdata"] = self.gdata
        template_vars['sys_version'] = __version__
        if self.current_user:
            template_vars["permit"] = self.current_user.permit
            template_vars["menu_icons"] = MENU_ICONS
            template_vars["all_menus"] = self.current_user.permit.build_menus(
                order_cats=ADMIN_MENUS
            )
        mytemplate = self.tp_lookup.get_template("admin/{0}".format(template_name))
        return mytemplate.render(**template_vars)

    def render_from_string(self, template_string, **template_vars):
        from mako.template import Template
        template = Template(template_string)
        return template.render(**template_vars)

    def set_session_user(self, username, ipaddr, opr_type, login_time):
        session_opr = ObjectDict()
        session_opr.username = username
        session_opr.ipaddr = ipaddr
        session_opr.opr_type = opr_type
        session_opr.login_time = login_time
        session_opr.resources = [r.rule_path for r in self.db.query(models.SysOperatorRule).filter_by(operator_name=username)]
        self.session['session_opr'] = session_opr
        self.session.save()

    def clear_session(self):
        self.session.clear()
        self.clear_all_cookies()  
        
    def get_current_user(self):
        opr = self.session.get("session_opr")
        if opr:
            opr.permit = permit.fork(opr.username,opr.opr_type,opr.resources)
        return opr

    def get_param_value(self, name, defval=None):
        val = self.db.query(models.SysParam.param_value).filter_by(param_name = name).scalar()
        return val or defval

    def add_oplog(self,message):
        msg = u"operate_log: %s %s %s %s" % (
            self.current_user.username,self.current_user.ipaddr,utils.get_currtime(),utils.safeunicode(message))
        logger.info(msg, trace="oplog")

    def status_desc(self,status):
        if status in (0,'0'):
            return u"正常"
        else:
            return u"停用"


