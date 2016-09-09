#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import datetime
from txweb import utils
from toughcrt.common import tools
from toughcrt import models
from txweb.dbutils import get_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from hashlib import md5


def init_db(db):

    params = [
        ('system_name', u'管理系统名称', u'ToughCRT 管理控制台'),
        ('is_debug', u'DEBUG模式', u'0'),
    ]

    for p in params:
        param = models.SysParam()
        param.param_name = p[0]
        param.param_desc = p[1]
        param.param_value = p[2]
        db.add(param)

    opr = models.SysOperator()
    opr.id = 1
    opr.operator_name = u'admin'
    opr.operator_type = 0
    opr.operator_pass = tools.saltmd5('root')
    opr.operator_desc = 'admin'
    opr.operator_status = 0
    db.add(opr)

    db.commit()
    db.close()


def update(config,force=False):
    try:
        db_engine = get_engine(config)
        if int(os.environ.get("DB_INIT", 1)) == 1 or force:
            print 'starting update database...'
            metadata = models.get_metadata(db_engine)
            metadata.drop_all(db_engine)
            metadata.create_all(db_engine)
            print 'update database done'
            db = scoped_session(sessionmaker(bind=db_engine, autocommit=False, autoflush=True))()
            init_db(db)
    except:
        import traceback
        traceback.print_exc()

def drop_table(config,table_name):
    try:
        print 'starting drop table %s' % table_name
        db_engine = get_engine(config)
        metadata = models.get_metadata(db_engine)
        for tname,table in metadata.tables.items():
            if tname == table_name:
                table.drop(db_engine)
                print 'drop table %s done' % table_name
                break
    except Exception, e:
        import traceback
        traceback.print_exc()

def create_table(config,table_name):
    try:
        print 'starting create table %s' % table_name
        db_engine = get_engine(config)
        metadata = models.get_metadata(db_engine)
        for tname,table in metadata.tables.items():
            if tname == table_name:
                table.create(db_engine)
                print 'create table %s done' % table_name
                break
    except Exception, e:
        import traceback
        traceback.print_exc()







