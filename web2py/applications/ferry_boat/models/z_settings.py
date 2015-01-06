# -*- coding: utf-8 -*-
import os
import ConfigParser
set_f=os.path.join(request.env.web2py_path,'applications','ferry_boat','private','settings.ini')
Config = ConfigParser.ConfigParser()
Config.read(set_f)

try:
    if Config.getboolean('General','AllowRegister'):
        if 'register' in auth.settings.actions_disabled:
            auth.settings.actions_disabled.remove('register')
    else:
        if 'register' not in auth.settings.actions_disabled:
            auth.settings.actions_disabled.append('register')
except:
    response.flash=XML('Invalid configuration detected: <a href="%s">Fix</a>' %URL('default', 'settings'))
