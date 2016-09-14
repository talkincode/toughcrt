#!/usr/bin/env python
# coding=utf-8
import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),os.path.pardir))
import datetime
import six
import msgpack
import toughcrt
import traceback
from txweb.redis_cache import CacheManager
from txweb import redis_session as session
from txzmq import ZmqEndpoint, ZmqFactory, ZmqPushConnection, ZmqPullConnection, ZmqSubConnection
from twisted.python import log
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import defer
from txweb import utils
from txweb.redis_conf import redis_conf
from txweb import logger,dispatch
from txweb.storage import Storage
from txweb.dbutils import get_engine
from txweb.utils import timecast
from toughcrt.radius.session import RadiusSession
from toughcrt.radius.stat_counter import StatCounter
from collections import deque
from sqlalchemy import *
from sqlalchemy.sql import text as _sql
from toughcrt import models

####################################################################################
# sync service
####################################################################################

class RadClientWorker(object):

    def __init__(self, gdata):
        self.gdata = gdata
        self.config = gdata.config
        self.que = deque() 
        self.cache = gdata.cache
        self.db_engine = gdata.db_engine
        self.metadata = models.get_metadata(self.db_engine)
        self.ops = {
            'radstart':self.start_session,
            'radstop':self.stop_session
        }
        self.radstart = ZmqPullConnection(ZmqFactory(), ZmqEndpoint('connect', self.config.mqproxy.radstart_connect))
        self.radstop = ZmqSubConnection(ZmqFactory(), ZmqEndpoint('connect',self.config.mqproxy.radstop_connect))
        self.radresp = ZmqPushConnection(ZmqFactory(), ZmqEndpoint('connect', self.config.mqproxy.radresp_connect))
        self.radstop.subscribe('radstop')
        self.radstop.gotMessage = self.subdataReceived
        self.radstart.onPull = self.dataReceived
        self.process_poll()
        logger.info("Start radstart %s" % self.radstart)
        logger.info("Start radstop %s" % self.radstop)
        logger.info("Start radresp %s" % self.radresp)


    def subdataReceived(self, request,tag):
        try:
            message = msgpack.unpackb(request)
            if self.config.system.debug:
                logger.debug(u"received radius start request:"+utils.safeunicode(message))
            self.que.appendleft(message)
        except:
            traceback.print_exc()

    def dataReceived(self, request):
        try:
            message = msgpack.unpackb(request[0])
            if self.config.system.debug:
                logger.debug(u"received radius start request:"+utils.safeunicode(message))
            self.que.appendleft(message)
        except:
            traceback.print_exc()

    def start_session(self,userdata):
        username = userdata['username']
        password = userdata['password']
        radius_ipaddr = userdata['radius_ipaddr']
        num = userdata.get("num",1)
        isresp = int(userdata.get("isresp",0))
        sendresp = lambda r : self.radresp.push(msgpack.packb(['radstart_resp',r])) if isresp else None
        senderror = lambda e: self.radresp.push(msgpack.packb(['radstart_error',dict(code=1,msg=repr(e))])) if isresp else None 
        for i in range(num):
            rad_session = RadiusSession(self.config,self.db_engine,
                statcache=self.gdata.statcache,radius_ipaddr=radius_ipaddr)
            rad_session.start(username,password).addCallbacks(sendresp,senderror)

    def stop_session(self,userdata):
        ipaddr = userdata.get('ipaddr','')
        session_id = userdata.get('session_id','')
        username = userdata.get('username','')
        RadiusSession.stop_session(ipaddr=ipaddr,session_id=session_id,username=username)
        self.radresp.push(msgpack.packb(['radstop_resp',dict(code=0,msg="session(%s,%s,%s) stop done"%(ipaddr,session_id,username))]))

    def process_poll(self):
        try:
            action, objdata = self.que.pop()
        except Exception as err:
            # logger.exception(err)
            reactor.callLater(1,self.process_poll)
        else:
            try:
                opfunc = self.ops.get(action)
                if opfunc:
                    opfunc(objdata)
                else:
                    logger.error('action %s not support'%action)
            except Exception as err:
                self.radresp.push(msgpack.packb(['%s_error'%action,dict(code=1,msg=repr(err))]))
                logger.exception(err)
            finally:
                reactor.callLater(0.001,self.process_poll)

@defer.inlineCallbacks
def start(gdata):
    yield
    utils.update_tz(gdata.config.system.tz)
    syslog = logger.Logger(gdata.config,"toughcrt")
    dispatch.register(syslog)
    log.startLoggingWithObserver(syslog.emit, setStdout=0)

    gdata.db_engine = get_engine(gdata.config,pool_size=10)
    # gdata.db = scoped_session(sessionmaker(bind=gdata.db_engine, autocommit=False, autoflush=False))

    gdata.redisconf = redis_conf(gdata.config)
    gdata.cache = CacheManager(gdata.redisconf,cache_name='Cache-%s'%os.getpid())
    gdata.statcache = StatCounter(gdata)
    # cache event init
    dispatch.register(gdata.cache)
    dispatch.register(RadClientWorker(gdata))

    



