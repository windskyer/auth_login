from config import  Config
CONF = Config()
print CONF.CONF.get_all_options()
print CONF.get_wsgi_args()


#from Crypto.Util.randpool import RandomPool as _RandomPool
