#!/usr/bin/env python
# coding:utf-8
import time
import cyclone.sse
import cyclone.web
import msgpack
import itertools
import json
import pprint
from txweb import utils
from toughcrt.handlers.base import BaseHandler, MenuOpt
from toughcrt.handlers.base import authenticated
from txweb.permit import permit
from toughcrt import models
from toughlib.btforms.rules import is_number
from twisted.internet import defer, reactor
from toughcrt import models

def sleep(secs):
    d = defer.Deferred()
    reactor.callLater(secs, d.callback, None)
    return d

@permit.route(r"/admin/account/tester/stat", u"账号测试统计", MenuOpt, order=4.0001, is_menu=False)
class AccountTesterStatHandler(BaseHandler):

    @authenticated
    def get(self):
        self.render_json(code=0,msg="ok",statdata=self.gdata.statcache.statdata())

@permit.route(r"/admin/account/tester/resp", u"账号测试响应", MenuOpt, order=4.0001, is_menu=False)
class AccountTesterRespHandler(BaseHandler):

    @authenticated
    def get(self):
        msgs = []
        while 1:
            try:
                robj = self.gdata.radque.pop()
                rjson = json.dumps(
                    robj, ensure_ascii=False,
                    sort_keys=True,indent=4, 
                    separators=(',', ': ')
                )
                msgs.append(rjson)
                if len(msgs) == 10:
                    break
            except:
                break
        self.render_json(code=0,msg="ok",len=len(msgs),respdata="<br><br>".join(msgs))

@permit.route(r"/admin/account/tester", u"账号测试", MenuOpt, order=4.0001, is_menu=True)
class AccountTesterHandler(BaseHandler):

    @authenticated
    def get(self):
        radius_list = self.db.query(models.SysRadius)
        user_list = self.db.query(models.TTAccount).limit(20)
        self.render("account_tester.html",
            radius_list=radius_list,
            user_list=user_list,**self.get_params())


@permit.route(r"/admin/account/tester/start", u"上线消息测试", MenuOpt, order=4.0001)
class StartTesterHandler(BaseHandler):

    @authenticated
    def post(self):
        username = self.get_argument("username",None)
        radius_ipaddr = self.get_argument("radius_ipaddr",None)
        if not radius_ipaddr:
            return self.render_json(code=1,msg="radius is not select")
        password = self.db.query(models.TTAccount).get(username).password
        req = dict(
            username=username,
            password=password,
            radius_ipaddr=radius_ipaddr,
            isresp=1,
            num=1
        )
        self.gdata.radstart.push(msgpack.packb(['radstart',req]))
        self.render_json(code=0,msg="start request send to worker")


@permit.route(r"/admin/account/tester/stop", u"下线消息测试", MenuOpt, order=4.0001)
class StopTesterHandler(BaseHandler):

    @authenticated
    def post(self):
        username = self.get_argument("username",None)
        req = dict(username=username)
        self.gdata.radstop.publish(msgpack.packb(['radstop',req]),'radstop')
        self.render_json(code=0,msg="stop request send to worker")


@permit.route(r"/admin/account/tester/press", u"压力测试", MenuOpt, order=4.0001)
class PressTesterHandler(BaseHandler):

    @defer.inlineCallbacks
    @authenticated
    def post(self):
        username = self.get_argument("username",None)
        sequser = int(self.get_argument("sequser","0"))
        radius_ipaddr = self.get_argument("radius_ipaddr",None)
        test_times = self.get_argument("test_times",0)
        if not is_number.valid(test_times):
            test_times = 1

        if not is_number.valid(sequser):
            sequser = 1

        if not radius_ipaddr:
            self.render_json(code=1,msg="radius not select")
            return

        sequser = int(sequser)
        test_total = int(test_times)
        password = self.db.query(models.TTAccount).get(username).password

        _total = 0
        if sequser > 1:
            users = itertools.cycle( "%s%s"%(username,i) for i in range(sequser) )
            while 1:
                if _total == test_total:
                    break
                req = dict(username=next(users),password=password,radius_ipaddr=radius_ipaddr,num=1)
                self.gdata.radstart.push(msgpack.packb(['radstart',req]))
                _total += 1
                yield sleep(0.002)
        else:
            for i in xrange(int(test_times)):
                if _total == test_total:
                    break
                req = dict(username=username,password=password,radius_ipaddr=radius_ipaddr,num=1)
                self.gdata.radstart.push(msgpack.packb(['radstart',req]))                    
                _total += 1
                yield sleep(0.002)

        self.render_json(code=0,msg=u"send request to worker done")
            
