#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import string
import uuid
import time
import datetime
from decimal import Decimal
from hashlib import md5 as __md5__


salt = '19797997'

def gen_random_str(clen=32):
    chars = string.ascii_letters+string.digits
    return ''.join([random.choice(chars) for _ in range(clen)])

def gen_random_num(clen=16):
    chars = string.digits
    return ''.join([random.choice(chars) for _ in range(clen)])

def saltmd5(src):
    return __md5__(salt + src).hexdigest()

def md5(src):
    return __md5__(src).hexdigest()

def get_secret_uuid():
    src = uuid.uuid1().hex.upper()
    return saltmd5(src)

def fmtyuan(val):
    if isinstance(val, Decimal):
        return str(val.quantize(Decimal('1.00')))
    return str(Decimal(val).quantize(Decimal('1.00')))

def is_expire(dtstr,secs=0):
    start_time = datetime.datetime.strptime(dtstr, '%Y-%m-%d %H:%M:%S')
    nowdate = datetime.datetime.now()
    dt = nowdate - start_time
    return dt.total_seconds() > secs

def datetime2msec(dtime_str):
    _datetime =  datetime.datetime.strptime(dtime_str,"%Y-%m-%d %H:%M:%S")
    return int(time.mktime(_datetime.timetuple()))

def format_time(times):
    if times <= 60:
        return u"%s秒"%times

    d = times / (3600 * 24)
    h = times % (3600 * 24) / 3600
    m = times % (3600 * 24) % 3600 / 60
    s = times % (3600 * 24) % 3600 % 60

    if int(d) > 0:
        return u"%s天%s小时%s分钟%s秒" % (int(d), int(h), int(m),int(s))
    elif int(d) == 0 and int(h) > 0:
        return u"%s小时%s分钟%s秒" % (int(h), int(m), int(s))
    elif int(d) == 0 and int(h) == 0 and int(m) > 0:
        return u"%s分钟%s秒" % (int(m),int(s))    

if __name__ == '__main__':
    print datetime2msec("2016-05-10 13:46:10")
    print fmtyuan("223.154")
    print fmtyuan(Decimal(22))
    print saltmd5("tss@#$%root")
    print saltmd5("toughdb")



