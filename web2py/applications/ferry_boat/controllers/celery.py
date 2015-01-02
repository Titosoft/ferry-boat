# -*- coding: utf-8 -*-
# try something like

def view_logs():
    return dict()

def log_table():
    import os
    logs=reversed(open(os.path.join('/var/log/ferry-btm/','tasks.log'),'r').readlines())
    return dict(logs=logs)

def clear_logs():
    import os
    fp=open(os.path.join('/var/log/ferry-btm/','tasks.log'),'w')
    fp.close()
