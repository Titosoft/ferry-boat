# -*- coding: utf-8 -*-
# try something like

@auth.requires_login()
def view_logs():
    return dict()

@auth.requires_login()
def log_table():
    import os
    logs=reversed(open(os.path.join('/var/log/ferry-btm/','tasks.log'),'r').readlines())
    return dict(logs=logs)

@auth.requires_login()
def clear_logs():
    import os
    fp=open(os.path.join('/var/log/ferry-btm/','tasks.log'),'w')
    fp.close()
