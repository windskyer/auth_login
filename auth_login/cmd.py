## Author leidong

if __name__ == "__main__":
    from  common.config import ConfigException
    from  common.config import Config
    cf = Config()
    print cf.get_vmname_values("vm24")
    print cf.get_one_section('subnets','net')
    print cf.get_one_section('passwords','user_passwd')
    print cf.get_one_section('usernames','user_name')
