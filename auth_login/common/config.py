# author leidong

""" Command-line flag library.

Emulates gflags by wrapping cfg.ConfigOpts.

"""

import os, sys

## gettext
from gettextutils import _

## configure
from ConfigParser import ConfigParser
from ConfigParser import re


class Autho_LoginException(Exception):
    '''youself Autho_Login  Exception class'''

    message = _("An unknown exception occurred.")

    def __init__(self, message=None, **kwargs):
        Exception.__init__(self)
        self.kwargs = kwargs
        if not message:
            try:
                message = self.message % kwargs
            except Exception:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]
                message = self.message

        self.msg = message
        super(Autho_LoginException, self).__init__(message)

    def __str__(self):
        return _(self.msg)

    def __unicode__(self):
        return unicode(self.msg)

class ConfigException(Autho_LoginException):
    """ Config file not found """
    message = _("Config file not found")


class Config():
    """ Config from ~/.ssh/auth_login file """
    
    def __init__(self,file=None):
        if file is None:
            file = "%s/.ssh/auth_login" % os.environ.get('HOME')
            if os.path.isfile(file):
                self._file = file
            else:
                raise Autho_LoginException("Not Found ~/.ssh/auth_login file")
        else:
            self._file = file

        self.__sections = []
        self.__options = {}
        self.__servers = []

        self._cf = ConfigParser()
        ## read ~/.ssh/auth_login configure file 
        self._cf.read(self._file)
    
    ## Get all ssh server name return list
    def get_all_vmnames(self):
        if self._cf.has_section('server'):
            if self._cf.has_option('server','ssh_server_alias'):
                servernames = self._cf.get('server', 'ssh_server_alias')
            else:
                raise Autho_LoginException("Not Found ~/.ssh/auth_login in ssh_server_alias option file")
        else:
            raise Autho_LoginException("Not Found ~/.ssh/auth_login in server section file")

        servernamelist = re.split("\,|\#|\?|\|", servernames)

        self.__servers = servernamelist
        
        return self.__servers

    ## Get all sections return list
    def get_sections(self):
        self.__sections = self._cf.sections()
        return self.__sections

    ## Get all options return dict
    def get_options(self):
        for sec in self._cf.sections():
            self.__options[sec] = self._cf.options(sec)
        return self.__options

    ## Get spec vmanme values return dict
    def get_vmname_values(self,vmname=None):
        vmdict = {}
        vmtemp = "" 
        if vmname is None:
            raise Autho_LoginException("You must speci vmname value (vmname is not None)")
        
        if vmname not in self._cf.sections():
            #raise Autho_LoginException("Not Found %s sections ~/.ssh/auth_login file " % vmname)
            print "Waring Not Found %s sections ~/.ssh/auth_login file " % vmname 
            vmtemp = "DEFAULT"
        else:
            vmtemp = vmname

        vmtmpdict = {}
        for vs in self._cf.items(vmtemp):
            vmtmpdict[vs[0]] = vs[1]
        vmdict[vmname] = vmtmpdict
        return vmdict

    ## Get all vmanme values return dict
    def get_all_vmname_values(self):
        self.__servers = self.get_all_vmnames()
        vmsdict = {}
        for server in self.__servers:
            vmsdict[server] = self.get_vmname_values(server)
        return vmsdict
    
    ## Get configure default section return dict
    def get_default_items(self):
        self_defaults = self._cf.defaults() 
        return self_defaults

    ## Get ssh server section and option
    def get_one_section(self, section=None, option=None):
        print self._cf.has_section(section)
        if not self._cf.has_section(section) or section is None:
            raise Autho_LoginException("Not Found ~/.ssh/auth_login in %s section file" % section)
        elif option is None or not self._cf.has_option(section,option): 
            raise Autho_LoginException("Not Found ~/.ssh/auth_login  %s option in %s section" % (option, section))
        sectiondict = {}
        optiondict = {}
        value = self._cf.get(section,option)
        value = re.split("\,|\#|\?|\|", value)
        optiondict[option] = value
        sectiondict[section] = optiondict[option]

        return sectiondict[section]
                        
    ## Set ~/.ssh/auth_login  configure file 
    def get_config(self,conf=None,vmname=None):
        print 

