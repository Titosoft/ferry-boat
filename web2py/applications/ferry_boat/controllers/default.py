# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    import platform, psutil
    host=dict(machine=platform.machine(),version=platform.version(),platform=platform.platform(),uname=platform.uname(),system=platform.system(),cpu_count=psutil.cpu_count())
    host_usage=dict(cpu=psutil.cpu_times_percent(),memory=psutil.virtual_memory(),swap=psutil.swap_memory(),root_fs=psutil.disk_usage('/'))
    containers=c.containers(all=True)
    docker_info=c.info()
    return dict(containers=containers,host=host,host_usage=host_usage,docker_info=docker_info)

def inspect():
    c_id=request.args(0)
    details=c.inspect_container(c_id)
    logs=c.logs(c_id,timestamps=True)
    if details['State']['Running']:
        processes=c.top(c_id)
    else:
        processes={}
    domains=None
    envs=[]
    l=[i.split('=') for i in details['Config']['Env']]
    for k,v in l:
        envs.append({k:v})
    for i in envs:
        if i.get('VIRTUAL_HOST'):
            domains=i.get('VIRTUAL_HOST')
    return dict(details=details,domains=domains,logs=logs,processes=processes)

def start():
    c_id=request.args(0)
    start=c.start(c_id)
    session.flash='app started'
    redirect(URL('index'))

def stop():
    c_id=request.args(0)
    stop=c.stop(c_id)
    session.flash='app stopped'
    redirect(URL('index'))

def restart():
    c_id=request.args(0)
    restart=c.restart(c_id)
    session.flash='app restarted'
    redirect(URL('index'))

def kill():
    c_id=request.args(0)
    kill=c.restart(c_id)
    redirect(URL('index'))

def remove():
    c_id=request.args(0)
    try:
        start=c.remove_container(c_id)
        session.flash='app removed'
    except:
        session.flash='Stop the container first'
    redirect(URL('index'))

def my_images():
    images=db(db.my_image.id>0).select()
    return dict(images=images)

def new_image():
    form=SQLFORM(db.my_image,submit_button='Next')
    if form.process().accepted:
        redirect(URL('config_image', args=form.vars.id))
    elif form.errors:
        response.flash = 'form has errors'

    return dict(form=form)

def add_volume():
    image_id=request.args(0)
    form=SQLFORM(db.volumes,formname="add_volumes",fields=['host_path','container_path','rw'],submit_button='Add')
    if request.args(1) == 'session':
        volumes=session.volumes
        if form.validate():
            session.volumes.append({'id':len(session.volumes),'host_path':form.vars.host_path,'container_path':form.vars.container_path,'rw':form.vars.rw})
        elif form.errors:
            response.flash = 'form has errors'
    else:
        form.vars.image=image_id
        volumes=db(db.volumes.image==image_id).select()
        if form.process().accepted:
            response.js =  "jQuery('#%s').get(0).reload()" % 'volumes'
        elif form.errors:
            response.flash = 'form has errors'
    return dict(form=form,volumes=volumes)

def delete_volume():
    v_id=request.args(0)
    if request.args(1) == 'session':
        session.volumes.pop(int(v_id))
        for c,i in enumerate(session.volumes):
            i['id']=c
        response.js =  "jQuery('#%s').get(0).reload()" % 'volumes'
    else:
        image=db.volumes(v_id).image
        db(db.volumes.id==v_id).delete()
        response.js =  "jQuery('#%s').get(0).reload()" % 'volumes'

def add_port():
    image_id=request.args(0)
    form=SQLFORM(db.ports,formname="add_ports",fields=['host_port','container_port',],submit_button='Add')
    if request.args(1) == 'session':
        ports=session.ports
        if form.validate():
            session.ports.append({'id':len(session.ports),'host_port':form.vars.host_port,'container_port':form.vars.container_port})
        elif form.errors:
            response.flash = 'form has errors'
    else:
        form.vars.image=image_id
        ports=db(db.ports.image==image_id).select()
        if form.process().accepted:
            response.js =  "jQuery('#%s').get(0).reload()" % 'ports'
        elif form.errors:
            response.flash = 'form has errors'
    return dict(form=form,ports=ports)

def delete_port():
    v_id=request.args(0)
    if request.args(1) == 'session':
        session.ports.pop(int(v_id))
        for c,i in enumerate(session.ports):
            i['id']=c
        response.js =  "jQuery('#%s').get(0).reload()" % 'ports'
    else:
        image=db.ports(v_id).image
        db(db.ports.id==v_id).delete()
        response.js =  "jQuery('#%s').get(0).reload()" % 'ports'

def add_env():
    form = SQLFORM.factory(
        Field('key', requires=IS_NOT_EMPTY()),
        Field('value', requires=IS_NOT_EMPTY())
        ,submit_button='Add',formname="add_envs")
    envs=session.envs
    if form.validate():
        session.envs.append({'id':len(session.envs),'key':form.vars.key,'value':form.vars.value})
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form,envs=envs)

def delete_env():
    v_id=request.args(0)
    session.envs.pop(int(v_id))
    for c,i in enumerate(session.envs):
        i['id']=c
    response.js = "jQuery('#%s').get(0).reload()" % 'envs'

def config_image():
    image_id=request.args(0)
    image=db.my_image(image_id)
    if not image:
        redirect(URL('new_image'))
    form=SQLFORM(db.my_image,image,submit_button='Next')
    if form.process().accepted:
        pass
    elif form.errors:
        response.flash = 'form has errors'

    return dict(form=form,image=image)

def deploy():
    from docker_tasks import create_start
    create=start=''
    volumes=[]
    binds={}
    ports=[]
    port_bindings={}
    environment={}
    form = SQLFORM.factory(
        Field('name', requires=IS_NOT_EMPTY()),
        Field('image', 'reference my_image', requires=IS_IN_DB(db(db.my_image.id>0), 'my_image.id', '%(name)s')),
        Field('tag'),
        Field('command'),
        Field('use_default', 'boolean', default=True),
        Field('random_port', 'boolean'),
        Field('domains'),
        Field('password', 'password'),
    )
    if form.process().accepted:
        name=form.vars.name
        image_id=form.vars.image
        envs=session.envs
        use_default=form.vars.use_default

        if use_default:
            # build based on image data
            image_q=db.my_image(image_id)
            tag=image_q.default_tag
            if tag:
                tag=tag.lower()
            image=image_q.docker_name+':'+tag
            random_port=image_q.random_port
            command=image_q.command
            ports_q=db(db.ports.image==image_id).select()
            volumes_q=db(db.volumes.image==image_id).select()
        else:
            # customized container
            tag=form.vars.tag
            if tag:
                tag=tag.lower()
            image=db.my_image(image_id).docker_name+':'+tag
            random_port=form.vars.random_port
            command=form.vars.command
            ports_q=session.ports
            volumes_q=session.volumes

        for p in ports_q:
            if p['container_port']:
                ports.append(p['container_port'])
            if p['host_port']:
                port_bindings[p['container_port']]=p['host_port']

        for v in volumes_q:
            if v['container_path']:
                volumes.append(v['container_path'])
                if v['host_path']:
                    binds[v['host_path']]={'bind': v['container_path'],'ro': not v['rw']}

        for e in envs:
            if e['key']:
                environment[e['key']]=e['value']

        create_start.delay(name=name,image=image,ports=ports,volumes=volumes,environment=environment,
                               hostname=name,command=command,binds=binds,port_bindings=port_bindings,publish_all_ports=random_port)
        session.flash='Task sent to BTM. Check logs for status'
        redirect(URL('celery','view_logs'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        session.volumes=[]
        session.ports=[]
        session.envs=[]
    return dict(form=form,v=request.vars,volumes=volumes,binds=binds,ports=ports,port_bindings=port_bindings,environment=environment,create=create,start=start)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
