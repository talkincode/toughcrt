#!/usr/bin/env python
# coding=utf-8

import time
from twisted.internet import defer, reactor
from decimal import Decimal as D

auth_request_cache_key = 'toughcrt.cache.auth.request'
auth_accept_cache_key = 'toughcrt.cache.auth.accept'
auth_reject_cache_key = 'toughcrt.cache.auth.reject'
acct_start_cache_key = 'toughcrt.cache.acct.start'
acct_update_cache_key = 'toughcrt.cache.acct.update'
acct_stop_cache_key = 'toughcrt.cache.acct.stop'
acct_resp_cache_key = 'toughcrt.cache.acct.resp'
dm_request_cache_key = 'toughcrt.cache.dm.request'
dm_ack_cache_key = 'toughcrt.cache.dm.ack'
dm_nak_cache_key = 'toughcrt.cache.dm.nak'
starttime_cache_key = 'toughcrt.cache.stat.starttime'
lasttime_cache_key = 'toughcrt.cache.stat.lasttime'
stattime_cache_key = 'toughcrt.cache.stat.stattime'
statnum_cache_key = 'toughcrt.cache.stat.statnum'
maxcnum_cache_key = 'toughcrt.cache.stat.maxcnum'
currcnum_cache_key = 'toughcrt.cache.stat.currcnum'

class StatCounter:

    def __init__(self,gdata):
        self.gdata = gdata

    def init(self):
        self.set(starttime_cache_key, time.time())
        self.set(lasttime_cache_key, time.time())
        self.set(stattime_cache_key, time.time())
        self.set(statnum_cache_key, 0)
        self.set(maxcnum_cache_key, 0)
        self.set(currcnum_cache_key, 0)
        self.set(auth_request_cache_key, 0)
        self.set(auth_accept_cache_key, 0)
        self.set(auth_reject_cache_key, 0)
        self.set(acct_start_cache_key, 0)
        self.set(acct_update_cache_key, 0)
        self.set(acct_stop_cache_key, 0)
        self.set(acct_resp_cache_key, 0)
        self.set(dm_request_cache_key, 0)
        self.set(dm_ack_cache_key, 0)
        self.set(dm_nak_cache_key, 0)

    @property
    def starttime(self):
        return float(self.get(starttime_cache_key))

    @property
    def lasttime(self):
        return float(self.get(lasttime_cache_key))

    @property
    def stattime(self):
        return float(self.get(stattime_cache_key))         

    @property
    def statnum(self):
        return int(D(self.get(statnum_cache_key) or 0))

    @property
    def requests(self):
        authreqs = int(D(self.get(auth_request_cache_key) or 0))
        acctstarts = int(D(self.get(acct_start_cache_key) or 0))
        acctupdates = int(D(self.get(acct_update_cache_key) or 0))
        acctstops = int(D(self.get(acct_stop_cache_key) or 0))
        return  authreqs + acctstarts + acctupdates + acctstops

    @property
    def replys(self):
        accepts = int(D(self.get(auth_request_cache_key) or 0))
        rejects = int(D(self.get(auth_reject_cache_key) or 0))
        acctresps = int(D(self.get(acct_resp_cache_key) or 0))
        return accepts + rejects + acctresps

    @property
    def maxcnum(self):
        return int(D(self.get(maxcnum_cache_key) or 0))

    @property
    def currcnum(self):
        return int(D(self.get(currcnum_cache_key) or 0))

    def incr(self,key):
        self.gdata.cache.incr(key)

    def set(self,key,value):
        self.gdata.cache.set(key,value,expire=31536000,is_pickle=False)

    def get(self,key):
        return self.gdata.cache.get(key,is_pickle=False)

    def poll_calc(self):
        try:
            self.set(lasttime_cache_key, time.time())
            _sectimes = self.lasttime - self.stattime
            if _sectimes > 1:
                _stat_num = self.replys - self.statnum
                _percount = int(_stat_num /(0 if _sectimes < 0 else _sectimes))
                self.set(currcnum_cache_key, _percount)
                if _percount > self.maxcnum:
                    self.set(maxcnum_cache_key, _percount)
                self.set(stattime_cache_key, self.lasttime)
                self.set(statnum_cache_key, self.replys)
        finally:
            reactor.callLater(1.0,self.poll_calc)

            
    def statdata(self):
        return dict(
            requests=self.requests,
            replys=self.replys,
            maxcnum=int(self.maxcnum),
            currcnum=int(self.currcnum),
        )        










