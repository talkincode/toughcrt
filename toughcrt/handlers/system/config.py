#!/usr/bin/env python
# coding:utf-8
import os
import cyclone.web
from txweb import utils, logger, dispatch
from toughcrt.handlers.system import config_forms
from toughcrt.handlers.base import BaseHandler,MenuSys
from toughcrt.handlers.base import authenticated
from toughcrt import models
from txweb.permit import permit

@permit.route(r"/admin/config", u"系统配置管理", MenuSys, order=2.0000, is_menu=True)
class ConfigHandler(BaseHandler):
    @authenticated
    def get(self):
        active = self.get_argument("active", "system")
        system_form = config_forms.system_form()
        system_form.fill(self.gdata.config.system)
        database_form = config_forms.database_form()
        radius_form = config_forms.radius_form()
        radius_form.fill(self.gdata.config.radius)        
        if 'DB_TYPE' in os.environ and 'DB_URL' in os.environ:
            self.gdata.config['database']['dbtype'] = os.environ.get('DB_TYPE')
            self.gdata.config['database']['dburl'] = os.environ.get('DB_URL')

        database_form.fill(self.gdata.config.database)        
        syslog_form = config_forms.syslog_form()
        syslog_form.fill(self.gdata.config.syslog)
        self.render("config.html",
            active=active,
            system_form=system_form,
            database_form=database_form,
            radius_form=radius_form,
            syslog_form=syslog_form)


@permit.route(r"/admin/config/system/update", u"系统配置", u"系统管理", order=2.0001, is_menu=False)
class DefaultHandler(BaseHandler):
    @authenticated
    def post(self):
        config = self.gdata.config
        config['system']['debug'] = int(self.get_argument("debug"))
        config['system']['tz'] = self.get_argument("tz")
        config['system']['secret'] = self.get_argument("secret")
        config.save()
        self.redirect("/admin/config?active=system")

@permit.route(r"/admin/config/database/update", u"数据库配置", u"系统管理", order=2.0002, is_menu=False)
class DatabaseHandler(BaseHandler):
    @authenticated
    def post(self):
        config = self.gdata.config
        config['database']['echo'] = int(self.get_argument("echo"))
        config['database']['dbtype'] = self.get_argument("dbtype")
        config['database']['dburl'] = self.get_argument("dburl")
        config['database']['pool_size'] = int(self.get_argument("pool_size"))
        config['database']['pool_recycle'] = int(self.get_argument("pool_recycle"))
        # config['database']['backup_path'] = self.get_argument("backup_path")
        config.save()
        self.redirect("/admin/config?active=database")

@permit.route(r"/admin/config/radius/update", u"Radius 配置", u"系统管理", order=2.0003, is_menu=False)
class RadiusHandler(BaseHandler):
    @authenticated
    def post(self):
        config = self.gdata.config
        config['radius']['nasid'] = self.get_argument("nasid")
        config['radius']['nasaddr'] = self.get_argument("nasaddr")
        config['radius']['authorize_port'] = int(self.get_argument("authorize_port"))
        config['radius']['interim_update'] = int(self.get_argument("interim_update"))
        config.save()
        self.redirect("/admin/config?active=radius")        


@permit.route(r"/admin/config/syslog/update", u"syslog 配置", u"系统管理", order=2.0003, is_menu=False)
class SyslogHandler(BaseHandler):
    @authenticated
    def post(self):
        self.gdata.config['syslog']['enable'] = int(self.get_argument("enable"))
        self.gdata.config['syslog']['server'] = self.get_argument("server")
        self.gdata.config['syslog']['port'] = int(self.get_argument("port",514))
        self.gdata.config['syslog']['level'] = self.get_argument("level")
        self.gdata.config.save()
        dispatch.pub(logger.EVENT_SETUP,self.gdata.config)
        self.redirect("/admin/config?active=syslog")









