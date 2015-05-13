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

##
import argparse
from argparse import Namespace


## Function 
def _fixpath(p):
    """Apply tilde expansion and absolutization to a path."""
    return os.path.abspath(os.path.expanduser(p))

def _get_config_dirs(project=None):
    """Return a list of directors where config files may be located.

    :param project: an optional project name

    If a project is specified, following directories are returned::

      ~/.${project}/
      ~/
      /etc/${project}/
      /etc/

    Otherwise, these directories::

      ~/
      /etc/
    """
    cfg_dirs = [
        _fixpath(os.path.join('~', '.' + project)) if project else None,
        _fixpath('~'),
        os.path.join('/etc', project) if project else None,
        '/etc'
    ]

    return filter(bool, cfg_dirs)

def _search_dirs(dirs, basename, extension=""):
    """Search a list of directories for a given filename.

    Iterator over the supplied directories, returning the first file
    found with the supplied name and extension.

    :param dirs: a list of directories
    :param basename: the filename, e.g. 'glance-api'
    :param extension: the file extension, e.g. '.conf'
    :returns: the path to a matching file, or None
    """
    for d in dirs:
        path = os.path.join(d, '%s%s' % (basename, extension))
        if os.path.exists(path):
            return path

def find_config_files(project=None, prog=None, extension='.conf'):
    """Return a list of default configuration files.

    :param project: an optional project name
    :param prog: the program name, defaulting to the basename of sys.argv[0]
    :param extension: the type of the config file

    We default to two config files: [${project}.conf, ${prog}.conf]

    And we look for those config files in the following directories::

      ~/.${project}/
      ~/
      /etc/${project}/
      /etc/

    We return an absolute path for (at most) one of each the default config
    files, for the topmost directory it exists in.

    For example, if project=foo, prog=bar and /etc/foo/foo.conf, /etc/bar.conf
    and ~/.foo/bar.conf all exist, then we return ['/etc/foo/foo.conf',
    '~/.foo/bar.conf']

    If no project name is supplied, we only look for ${prog.conf}.
    """
    if prog is None:
        prog = os.path.basename(sys.argv[0])

    cfg_dirs = _get_config_dirs(project)

    config_files = [] 
    if project:
        config_files.append(_search_dirs(cfg_dirs, project, extension))

    config_files.append(_search_dirs(cfg_dirs, prog, extension))

    return filter(bool, config_files)


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

class _Namespace(Namespace):
    def __init__(self):
        pass
    def __call__(self, confs):
        if not isinstance(dict, confs):
           pass 


class Config(object):
    """ Config from auth_login.conf file """
    
    ## init function
    def __init__(self, object="auth_login"):

        self.__sections = []
        self.__options = {}
        self.__servers = []

        self._object = object 
        self._get_config()

    ## Set ~/.ssh/auth_login  configure file 
    def _get_config(self):
        self._default_config_files =  find_config_files(self._object) 
        self._args = self._setup_args_ssh(self._object)
        if not self._default_config_files:
            self._default_config_files = self._args.config_file

        if not self._default_config_files:
            raise Autho_LoginException("Not Found configure file" )

        self._file = self._default_config_files
        self._cf = ConfigParser()
        self._cf.read(self._file)
        self._default_config_files = " | ".join(self._file)

    ## _setup ssh conn function
    def _setup_args_ssh(self, project):
        """Initialize a ConfigOpts object for option parsing."""
        prog = usage = project
        version = "verbose"

        self._project = project
        self._prog = prog
        self._version = version
        self._usage = usage

        self._oparser = argparse.ArgumentParser(prog=prog, usage=usage, description='%(prog)s - SSH Server Daemon')

        self._oparser.add_argument('-v', '--version',
                                   action='version',
                                   version=version,
                                   help='Print more verbose output (set logging level to '
                                        'INFO instead of default WARNING level).')

        self._oparser.add_argument('-D', '--debug',
                                   action='store_false',
                                   default=False,
                                   help='Print debugging output (set logging level to '
                                        'DEBUG instead of default WARNING level).'),

        self._oparser.add_argument('--config-file',
                                   nargs='?',
                                   help='Path to a config file to use. Multiple config '
                                        'files can be specified, with values in later '
                                        'files taking precedence. The default files '
                                        ' used are: %s' % (self._default_config_files, ))


        self._setup_args_wsgi()

        self._args = self._oparser.parse_args()

        return self._args

    ## set wsgi server startup info
    def _setup_args_wsgi(self):

        self._oparser.add_argument('--wsgi-port', '-P',
                        type=int,
                        default=5000,
                        help='Wsgi Server Port to bind (default: 5000)')

        self._oparser.add_argument('--wsgi-host', '-H',
                        default='0.0.0.0',
                        help='Wsgi Server Host to listen to (default: 0.0.0.0)')

        self._oparser.add_argument('--allow-agent', '-A',
                        action='store_true',
                        default=False,
                        help='Wsgi Server Configure Allow the use of the local (where wsshd is running) ' \
                        'ssh-agent to authenticate. Dangerous.')

        #self._args = self._oparser.parse_args()

        #return self._args

    ## set wsgi client startup info
    def _setup_args_client(self):
        parser = argparse.ArgumentParser(
            description='Auth_Login - SSH Over WebSockets Client')
        parser.add_argument('--host', '-H',
                                   help='Auth_Login server host (default: 127.0.0.1)',
                                   default='127.0.0.1')

        parser.add_argument('--port', '-P',
                                   help='Auth_Login server port (default: 5000)',
                                   type=int,
                                   default=5000)

        parser.add_argument('--password', '-p',
                                   nargs='?',
                                   const='',
                                   help='Password-based authentication. ' \
                                   'If no password is provided you will be prompted for one')

        parser.add_argument('--key', '-k',
                            nargs='?',
                            const='',
                            help='Private key authentication. ' \
                            'Selects a file from which the private key ' \
                            'for RSA or DSA authentication is read.  ' \
                            'The default is ~/.ssh/id_rsa and ~/.ssh/id_dsa.')

        parser.add_argument('--key-passphrase', '-K',
                            nargs='?',
                            const='',
                            help='Provide a passphrase for encrypted private key files.')

        parser.add_argument('--ssh-port', '-s',
                            type=int,
                            default=22,
                            help='Ssh to server host"s port')

        parser.add_argument('destination',
                            help='[user@]hostname')



    ## call function 
    def __call__(self, 
                 args=None, 
                 project=None, 
                 prog=None, 
                 version=None, 
                 usage=None,  
                 default_config_files=None):

        """ Parse command line arguments and config files. """

        if default_config_files is None:
            default_config_files = find_config_files(project=project, prog=prog, extension='.conf')
            if len(default_config_files):
                raise Autho_LoginException("Not Found %s file" % (self._default_config_files))

        self._file = file
        self._cf = ConfigParser()
        self._cf.read(self._file)
        
    
    ## Get all ssh server name return list
    def get_all_vmnames(self):
        if self._cf.has_section('ssh_server'):
            if self._cf.has_option('ssh_server','ssh_server_alias'):
                servernames = self._cf.get('ssh_server', 'ssh_server_alias')
            else:
                raise Autho_LoginException("Not Found %s in ssh_server_alias option file" % (self._default_config_files))
        else:
            raise Autho_LoginException("Not Found %s in ssh_server section file" % (self._default_config_files))

        servernamelist = re.split("\,|\#|\?|\|", servernames)

        self.__servers = servernamelist
        
        return self.__servers

    ## Get all sections return list
    def get_all_sections(self):
        self.__sections = self._cf.sections()
        return self.__sections

    ## Get all options return dict
    def get_all_options(self):
        for sec in self._cf.sections():
            self.__options[sec] = self._cf.options(sec)
        return self.__options

    ## Get spec one section options return dict
    def get_one_options(self, section=None):
        if section is not None:
            return self._cf.items(section)
        elif section is None or section not in self.get_all_sections():
            raise Autho_LoginException("Not Found %s have %s section" % (self._default_config_files, section))



    ## Get spec vmanme values return dict
    def get_vmname_values(self,vmname=None):
        vmdict = {}
        vmtemp = "" 
        if vmname is None:
            raise Autho_LoginException("You must speci vmname value (vmname is not None)")
        
        if vmname not in self._cf.sections():
            #raise Autho_LoginException("Not Found %s sections ~/.ssh/auth_login file " % vmname)
            print "Waring Not Found %s sections %s file " % (vmname , self._default_config_files )
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
        if not self._cf.has_section(section) or section is None:
            raise Autho_LoginException("Not Found %s  in %s section file" % (self._default_config_files, section))
        elif option is None or not self._cf.has_option(section,option): 
            raise Autho_LoginException("Not Found %s  %s option in %s section" % (self._default_config_files, option, section))
        sectiondict = {}
        optiondict = {}
        value = self._cf.get(section,option)
        value = re.split("\,|\#|\?|\|", value)
        optiondict[option] = value
        sectiondict[section] = optiondict[option]

        return sectiondict[section]
                        

    def get_wsgi_args(self):
        args = {}
        for value in self.get_one_options('wsgi_server'):
            args[value[0]] = value[1]

        if  "--debug" in sys.argv or "-D" in sys.argv :
            args['debug'] = self._args.debug

        if "--allow-agent" in sys.argv or "-A" in sys.argv:
            args['allow_agent'] = self._args.allow_agent

        if "--wsgi-port" in sys.argv or "-P" in sys.argv:
            args['wsgi_port'] = self._args.wsgi_port 

        if "--wsgi-host" in sys.argv or "-H" in sys.argv:
            args['wsgi_host'] = self._args.wsgi_host
        return args

        #return self._setup_args_wsgi()

    def get_client_args(self):
        args = {}

        return args
