#!/usr/bin/env python
#coding:utf-8
import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),os.path.pardir))
from txweb.dbutils import get_engine
from mako.lookup import TemplateLookup
from txweb.dbutils import DBBackup
from txweb.redis_cache import CacheManager
from txweb import redis_session as session
from txweb import logger,dispatch,utils
from txweb.permit import permit, load_handlers, load_events
from txweb.redis_conf import redis_conf
from txweb import utils
from sqlalchemy.orm import scoped_session, sessionmaker
from twisted.python import log
from collections import deque
from toughcrt import models
import msgpack
from twisted.internet import reactor, defer
from txzmq import ZmqEndpoint, ZmqFactory, ZmqPushConnection, ZmqPullConnection, ZmqPubConnection
from toughcrt.radius.stat_counter import StatCounter

def init(gdata): 
    appname = os.path.basename(gdata.app_dir)
    utils.update_tz(gdata.config.system.tz)
    syslog = logger.Logger(gdata.config,appname)
    dispatch.register(syslog)
    log.startLoggingWithObserver(syslog.emit, setStdout=0)

    gdata.db_engine = get_engine(gdata.config)
    gdata.db = scoped_session(sessionmaker(bind=gdata.db_engine, autocommit=False, autoflush=False))
    # web 应用初始化
    gdata.settings = dict(
        cookie_secret="12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        login_url="/admin/login",
        template_path=os.path.join(os.path.dirname(__file__), "views"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        xheaders=True,
        conf=gdata.config
    )

    # 模板初始化
    gdata.tp_lookup = TemplateLookup(
        directories=[gdata.settings['template_path']],
        default_filters=['decode.utf8'],
        input_encoding='utf-8',
        output_encoding='utf-8',
        encoding_errors='ignore',
        module_directory="/tmp/toughcloud"
    )       

    gdata.redisconf = redis_conf(gdata.config)
    gdata.session_manager = session.SessionManager(gdata.redisconf,gdata.settings["cookie_secret"], 7200)
    gdata.cache = CacheManager(gdata.redisconf,cache_name='Cache-%s'%os.getpid())
    gdata.aes = utils.AESCipher(key=gdata.config.system.secret)

    # 数据库备份器初始化
    gdata.db_backup = DBBackup(models.get_metadata(gdata.db_engine), excludes=[])

    #cache event init
    dispatch.register(gdata.cache)  

    # app handles init 
    handler_dir = os.path.join(gdata.app_dir,'handlers')
    load_handlers(handler_path=handler_dir,pkg_prefix="%s.handlers"%appname, excludes=[])
    gdata.all_handlers = permit.all_handlers

    # app event init
    event_dir = os.path.abspath(os.path.join(gdata.app_dir,'events'))
    load_events(event_dir,"%s.events"%appname)

    # init zmq
    gdata.radque = deque([],8192) 
    gdata.radstart = ZmqPushConnection(ZmqFactory(), ZmqEndpoint('bind', gdata.config.mqproxy.radstart_bind))
    gdata.radstop = ZmqPubConnection(ZmqFactory(), ZmqEndpoint('bind',gdata.config.mqproxy.radstop_bind))
    gdata.radresp = ZmqPullConnection(ZmqFactory(), ZmqEndpoint('bind', gdata.config.mqproxy.radresp_bind))
    gdata.radresp.onPull = lambda m: gdata.radque.appendleft(msgpack.unpackb(m[0]))
    gdata.statcache = StatCounter(gdata)
    gdata.statcache.init()
    gdata.statcache.poll_calc()
    
    logger.info(gdata.radstart)
    logger.info(gdata.radstop)
    logger.info(gdata.radresp)




