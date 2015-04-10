#!/usr/bin/env python 
#coding: utf-8

#author leidong
#date 20150331

import os, sys
import subprocess

## configure
from ConfigParser import ConfigParser
from ConfigParser import re

## ssh 
import paramiko
from paramiko import PasswordRequiredException
from paramiko.dsskey import DSSKey
from paramiko.rsakey import RSAKey
from paramiko.ssh_exception import SSHException


SERVERS = {"vm200":["172.24.23.200",],"vm222":["172.24.23.222",],"aix20":["172.24.23.20"],"aix212":["172.24.23.212",], "aix140":["172.24.23.140",]}


FILE_DIR = os.getcwd()
FILE_DIR = os.path.dirname(sys.argv[:1][0])
FILE_NAME = "loginfile.sh "
FILE = os.path.join(FILE_DIR , FILE_NAME)
CONF_FILE = "%s/.ssh/author_login" % os.environ.get('HOME')

if os.path.isfile(FILE):
    print FILE


## return dict type
## read ssh config file
def read_conf(conf=None,name=None):
    returndict = {}
    servernamelist = []
    cf = ConfigParser()
    if conf is None:
        print "Not Found ~/.ssh/author_login file"
        sys.exit(2)

    cf.read(conf)

    if cf.has_section('server'):
        if cf.has_option('server','ssh_server_alias'):
            servernames = cf.get('server', 'ssh_server_alias')
        else:
            print "Not Found ~/.ssh/author_login in ssh_server_alias option  file"
            sys.exit(2)
    else:
        print "Not Found ~/.ssh/author_login in server section file"
        sys.exit(2)

    servernamelist = re.split("\,|\#|\?|\|", servernames)

    if name is not None:
        if name in servernamelist:
            if cf.has_section(name):
                vmlist = cf.items(name)
                vmdict = {}
                for vm in vmlist:
                    vmdict[vm[0]] = vm[1]

                returndict[name] = vmdict 
            else:
                print "Not Found ~/.ssh/author_login in %s section  file" % name
                sys.exit(3)
        else:
            for k in servernamelist:
                print "\tplease input\t'%s'" % k
            print "Not Found ~/.ssh/author_login in %s section  file" % name
            sys.exit(3)
    else:
        print "please input ssh server name eg:"
        for k in servernamelist:
            print "\tplease input\t'%s'" % k
        sys.exit(3)
    
    return returndict
                

def login_server(servername,loginfile):

    if os.path.isfile(loginfile) == "False":
        print "this is %s is Not Found !" % loginfile
        return 0
    if servername is None:
        print "this is %s is None !" % servername 
        return 0

    #获取ip 通过 server name
    vips = SERVERS.get(servername)
    for vip in vips:
        try:
            print "login server %s  host ip %s" % (servername,vip)
            ret = subprocess.call("expect " + FILE + " " + vip , shell=True) 
        except subprocess.CalledProcessError.message as e:
            print "Execution failed:", e
        if ret == 0:
            subprocess.call("clear " , shell=True) 
            print "logout server %s  host" % vip
            print "您已经退出服务器 %s " % servername
            break
        else :
            print "%s ip is not useage" % vip


## check vmname host
def check_vmnames(vmname=None):
    if vmname not in SERVERS.keys() or vmname is None:
        for vmname , values in SERVERS.items():
            print "please input\t%s\t------->\tlogin info\t%s " % (vmname,values)
        sys.exit(1)

    return True 

## get vmname host
def get_vmnames(vmnames="all"):
    if vmnames == "all":
        vmnames = SERVERS.keys()

    for vmname in vmnames:
        if check_vmnames(vmname):
            login_server(vmname, FILE)

## main function 
if __name__ == "__main__":
    vmnames = sys.argv[1:]
    #get_vmnames(vmnames)
    print read_conf(CONF_FILE, vmnames[0])

