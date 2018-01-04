# -*- coding:utf-8 -*-
import os
import configparser
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def getconfig():
    config_dict = {}
    config = configparser.ConfigParser()
    config.read(os.path.join(BASE_DIR, 'setting.conf'))
    config_dict['database_name'] = config.get('mysql', 'DATABASE_NAME')
    config_dict['database_user'] = config.get('mysql', 'DATABASE_USER')
    config_dict['database_password'] = config.get('mysql', 'DATABASE_PASSWORD')
    config_dict['database_host'] = config.get('mysql', 'DATABASE_HOST')
    config_dict['database_port'] = config.get('mysql', 'DATABASE_PORT')
    config_dict['ldap_server_url'] = config.get('ldap', 'AUTH_LDAP_SERVER_URI')
    config_dict['ldap_bind_dn'] = config.get('ldap', 'AUTH_LDAP_BIND_DN')
    config_dict['ldap_bind_password'] = config.get('ldap', 'AUTH_LDAP_BIND_PASSWORD')
    return config_dict

