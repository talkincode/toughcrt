#!/usr/bin/env python
#coding:utf-8
import warnings
import sqlalchemy
warnings.simplefilter('ignore', sqlalchemy.exc.SAWarning)
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


def get_metadata(db_engine):
    global DeclarativeBase
    metadata = DeclarativeBase.metadata
    metadata.bind = db_engine
    return metadata


class SysOperator(DeclarativeBase):
    """
    操作员表 

    操作员类型 0 系统管理员 1 普通操作员
    """

    __tablename__ = 'sys_operator'

    __table_args__ = {}

    id = Column(u'id', INTEGER(), primary_key=True, nullable=False,doc=u"(主键)操作员id")
    operator_type = Column('operator_type', INTEGER(), nullable=False,doc=u"操作员类型")
    operator_name = Column(u'operator_name', Unicode(32), nullable=False,doc=u"操作员名称")
    operator_pass = Column(u'operator_pass', Unicode(length=128), nullable=False,doc=u"操作员密码")
    operator_status = Column(u'operator_status', INTEGER(), nullable=False,doc=u"操作员状态,0/1")
    operator_desc = Column(u'operator_desc', Unicode(255), nullable=False,doc=u"操作员描述")
    
class SysOperatorRule(DeclarativeBase):
    """
    操作员权限表
    """

    __tablename__ = 'sys_operator_rule'

    __table_args__ = {}
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False,doc=u"(主键)权限id")
    operator_name = Column(u'operator_name', Unicode(32), nullable=False,doc=u"操作员名称")
    rule_path = Column(u'rule_path', Unicode(128), nullable=False,doc=u"权限URL")
    rule_name = Column(u'rule_name', Unicode(128), nullable=False,doc=u"权限名称")
    rule_category = Column(u'rule_category', Unicode(128), nullable=False,doc=u"权限分类")


class SysParam(DeclarativeBase):
    """
    系统参数表 
    """

    __tablename__ = 'sys_param'

    __table_args__ = {}

    param_name = Column(u'param_name', Unicode(length=64), primary_key=True, nullable=False,doc=u"(主键)参数名")
    param_value = Column(u'param_value', Unicode(length=1024), nullable=False,doc=u"参数值")
    param_desc = Column(u'param_desc', Unicode(length=255),doc=u"参数描述")


class SysRadius(DeclarativeBase):
    """radius节点表 """
    __tablename__ = 'tt_radius'

    __table_args__ = {}

    # column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False, doc=u"id")
    ip_addr = Column(u'ip_addr', Unicode(length=15), nullable=False, doc=u"IP地址")
    name = Column(u'name', Unicode(length=64), nullable=False, doc=u"radius名称")
    secret = Column(u'secret', Unicode(length=64), nullable=False, doc=u"共享密钥")
    auth_port = Column(u'auth_port', INTEGER(), nullable=False, doc=u"认证端口")
    acct_port = Column(u'acct_port', INTEGER(), nullable=False, doc=u"记账端口")


class TTAccount(DeclarativeBase):
    """
    上网账号表
    """

    __tablename__ = 'tt_account'

    __table_args__ = {}

    username = Column('username', Unicode(length=32),primary_key=True,nullable=False,doc=u"上网账号")
    password = Column('password', Unicode(length=128), nullable=False,doc=u"上网密码")

class TTAccountAttr(DeclarativeBase):
    """Vendor属性 """
    __tablename__ = 'tt_account_attr'

    __table_args__ = {}

    # column definitions
    username = Column('username', Unicode(length=32),primary_key=True,doc=u"上网账号")
    attr_name = Column(u'attr_name', Unicode(length=128), primary_key=True, doc=u"属性名")
    attr_value = Column(u'attr_value', Unicode(length=255), nullable=False, doc=u"属性值")
    attr_desc = Column(u'attr_desc', Unicode(length=255), doc=u"属性描述")
    UniqueConstraint('username',"attr_name", name='unique_account_attr')


class TTSession(DeclarativeBase):
    """用户在线信息表"""
    __tablename__ = 'tt_session'

    __table_args__ = {
        'mysql_engine' : 'MEMORY'
    }

    acct_session_id = Column(u'acct_session_id', Unicode(length=64), primary_key=True,doc=u"会话id")
    nas_id = Column(u'nas_id', Unicode(length=32), nullable=False, doc=u"nas id")
    username = Column(u'username', Unicode(length=32), nullable=False, index=True, doc=u"上网账号")
    mac_addr = Column(u'mac_addr', Unicode(length=32), nullable=False,doc=u"mac地址")
    nas_addr = Column(u'nas_addr', Unicode(length=32), nullable=False,index=True, doc=u"bas地址")
    nas_port = Column(u'nas_port', INTEGER(), nullable=False, default=0, doc=u"接入端口")
    nas_port_id = Column(u'nas_port_id', Unicode(length=255), nullable=False,doc=u"接入端口物理信息")
    framed_ipaddr = Column(u'framed_ipaddr', Unicode(length=32), nullable=False,doc=u"IP地址")
    session_timeout = Column(u'session_timeout', INTEGER(), nullable=False,doc=u"会话时间")
    acct_input_total = Column(u'acct_input_total', INTEGER(),doc=u"上行流量（kb）")
    acct_output_total = Column(u'acct_output_total', INTEGER(),doc=u"下行流量（kb）")
    acct_start_time = Column(u'acct_start_time', Unicode(length=19), nullable=False,doc=u"会话开始时间")
    acct_session_time = Column(u'acct_session_time', INTEGER(), nullable=False,doc=u"已记账时间")
    acct_input_packets = Column(u'acct_input_packets', INTEGER(),doc=u"上行消息数")
    acct_output_packets = Column(u'acct_output_packets', INTEGER(),doc=u"下行消息数")    
