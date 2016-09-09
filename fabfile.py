#!/usr/bin/env python
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from fabric.api import *
from toughcrt import __version__
import datetime

# __version__ = 'v0.0.1'
env.user = 'root'
env.hosts = ['121.201.15.99']
currtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def date_ver():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def push():
    while 1:
        message = raw_input(u"input git commit message:")
        if message.strip():
            break

    local("git add .")
    try:
        local("git commit -m \'%s - %s: %s\'"%(__version__,currtime,message))
        local("git push origin develop")
    except:
        print u'no commit'
 
def master():
    message = "sync master"
    try:
        local("git checkout master")
        local("git merge --no-ff develop -m  \'%s - %s: %s\'" % (__version__,currtime,message) )
        local("git push origin master")
        local("git checkout develop")
    except:
        print u'no commit'
 
def release():
    try:
        ver = date_ver()
        local("git checkout master")
        local("git tag -a release-v%s -m 'release version %s'"%(ver,ver))
        local("git push origin release-v%s:release-v%s"%(ver,ver))
        local("git checkout develop")
    except:
        pass

def deploy():
    ver = date_ver()
    message = "deploy version v%s"%ver
    local("echo '' >> install.sh")
    local("git add .")
    try:
        local("git commit -m \'%s - %s: %s\'"%(__version__,currtime,message))
        local("git push origin develop")
    except:
        print u'no commit'


    try:
        local("git checkout master")
        local("git merge --no-ff develop -m  \'%s - %s: %s\'" % (__version__,currtime,message) )
        local("git push origin master")
        local("git tag -a release-v%s -m 'release version %s'"%(ver,ver))
        local("git push origin release-v%s:release-v%s"%(ver,ver))        
        local("git checkout develop")
    except:
        print u'no commit'

