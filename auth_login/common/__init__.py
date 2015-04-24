# author leidong

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0


from  .config import ConfigException
from  .config import Config
CONF = Config()


# --- function -----#
get_subnet = CONF.get_one_section('ssh_subnets','net')
get_passwd = CONF.get_one_section('ssh_passwords','user_passwd')
get_username = CONF.get_one_section('ssh_usernames','user_name')
get_wsgi_args = CONF.get_wsgi_args()



__all__ = ['get_subnet', 'get_passwd', 'get_username', 'CONF']
__version__ = '2015.4.16'

