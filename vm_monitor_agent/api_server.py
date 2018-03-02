# -*- coding: utf-8 -*-
import web
import json
import logging
import base64
import agent

import data_collector as dc
import six.moves.urllib.parse as urlparse

from datetime import datetime
from os import path

from report_server_api import reporter
from keystoneclient.v2_0 import client as client_v2
from config import settings
from swift_common import common_error_response, common_success_response, GLOBAL_READ_ACL, \
    CHUNK_SIZE, LIST_CONTENTS_ACL, _metadata_to_header, FOLDER_DELIMITER, wildcard_search, swift_api, Container, \
    get_auth_spec, swift_object_exists, swift_get_objects, _objectify, swift_container_exists
from swift import get_object as swift_download_object
from swiftclient.service import SwiftService, SwiftError, SwiftUploadObject

LOG = logging.getLogger()


# Currently we support three types of API, one is charge system api, another is vm command api and last is object api.
urls = (
    # Charge system API

    # VM command api
    '/api/cmd', 'cmd',
    # '/api/proc/list/(\d)', 'pslist',
    # '/api/proc/watch', 'watch_process',
    # '/api/proc/unwatch', 'unwatch_process',
    # '/api/vm/status', 'vm_status'

    # authenticate api
    '/api/authenticate','Authenticate',
    # object api
    ## Container related api
    '/api/containers', 'Swift_Containers',
    '/api/container_exists', 'Swift_Container_Exists',
    '/api/get_container', 'Swift_Get_Container',
    '/api/create_container', 'Swift_Create_Container',
    '/api/update_container', 'Swift_Update_Container',
    '/api/delete_container', 'Swift_Delete_Container',

    ## Objects related api
    '/api/object_exists', 'Swift_Object_Exists',
    '/api/objects', 'Swift_Get_Objects',
    '/api/filter_objects', 'Swift_Filter_Objects',
    '/api/copy_object', 'Swift_Copy_Object',
    '/api/upload_object', 'Swift_Upload_Object',
    '/api/create_pseudo_folder', 'Swift_Create_Pseudo_Folder',
    '/api/delete_object', 'Swift_Delete_Object',
    '/api/delete_folder', 'Swift_Delete_Folder',
    '/api/get_object', 'Swift_Get_Object',
    '/api/get_capabilities', 'Swift_GET_Capabilities',
)


class Authenticate:
    def POST(self):
        data = web.input().data
        data = json.loads(data)
        user = data['user']
        key = data['key']
        auth_url = data['auth_url']
        tenant_name = data['tenant_name']
        client = client_v2.Client(username=user, password=key, auth_url=auth_url,
                                  tenant_name=tenant_name)
        if client.authenticate():
            token = client.auth_ref['token']['id']
            return common_success_response([{"token": token}], "Authenticate user successfully!")
        else:
            return common_error_response("Authenticate user failed!")



class Swift_Containers:
    """
        {
        u'msg': u'Getcontainerslistsuccessfully',
        u'results': [
        {
            u'count': 58,
            u'bytes': 130015,
            u'name': u'config'
        },
        {
            u'count': 0,
            u'bytes': 0,
            u'name': u'config05aaa497-cc84-4802-aaba-d1ca3ee5a4c5'
        },
        {
            u'count': 0,
            u'bytes': 0,
            u'name': u'config529694eb-f8ae-4480-8364-df8334670986'
        },
        {
            u'count': 0,
            u'bytes': 0,
            u'name': u'config5e4d1580-63c2-4224-a26d-e3e8f2bf46a6'
        },
        {
            u'count': 0,
            u'bytes': 0,
            u'name': u'config73e1c465-2768-4ba1-b7e3-778190ccfcfb'
        },
        {
            u'count': 0,
            u'bytes': 0,
            u'name': u'dongdong'
        },
        {
            u'count': 61,
            u'bytes': 1198912,
            u'name': u'my-container'
        },
        {
            u'count': 0,
            u'bytes': 0,
            u'name': u'my-new-container'
        },
        {
            u'count': 0,
            u'bytes': 0,
            u'name': u'test'
        }
    ],
    u'errcode': 1
    }
    """
    def GET(self):
        data = web.input()
        try:
            auth_spec = get_auth_spec(data)
            headers, containers = swift_api(**auth_spec).get_account()
            containerobjs = filter(lambda x: not x['name'].endswith('_segments'),
                    [Container(container).to_dict() for container in containers])
            msg = "Get containers list successfully"
            return common_success_response(containerobjs, msg)
        except Exception as e:
            raise
            return common_error_response("Get containers list failed, error is %s" %e)

    def POST(self):
        return web.forbidden(" Post Method is not supported ")


class Swift_Container_Exists:
    def GET(self):
        data = web.input()
        container_name = data.get('container_name')
        if not container_name:
            return common_error_response("Container name is required")

        try:
            auth_spec = get_auth_spec(data)
            swift_api(**auth_spec).head_container(container_name)
            return common_success_response([], "container is existed")
        except Exception as e:
            return common_error_response("container is not existed")

    def POST(self):
        return web.forbidden(" Post Method is not supported ")


class Swift_Object_Exists:
    def GET(self):
        data = web.input()
        container_name = data.get('container_name')
        object_name = data.get('object_name')
        if not container_name and not object_name:
            return common_error_response("Container name and object name are required")

        try:
            auth_spec = get_auth_spec(data)
            swift_api(**auth_spec).head_object(container_name, object_name)
            return common_success_response([], "object is existed")
        except Exception as e:
            return common_error_response("object is not existed")

    def POST(self):
        return web.forbidden(" Post Method is not supported ")


class Swift_Get_Container:
    def GET(self):
        """
        container name:
        with_data: 
        :return: 
        
            without data:
                
                {
                u'msg': u'Getcontainerdetaildone',
                u'results': [
                    {
                    u'container_object_count': u'0',
                    u'name': u'dongdong',
                    u'timestamp': u'2017-10-28T23: 06: 31.115380',
                    u'container_bytes_used': u'0',
                    u'is_public': False,
                    u'data': None
                    }
                    ],
                u'errcode': 1
                }
        
        
        """
        data = web.input()
        container_name = data.get('container_name')
        with_data = data.get('with_data', 0)
        if not container_name:
            return common_error_response("Container name is required")
        auth_spec = get_auth_spec(data)

        if int(with_data) == 1:
            headers, data = swift_api(**auth_spec).get_object(container_name, "")
        else:
            data = None
            headers = swift_api(**auth_spec).head_container(container_name)
        timestamp = None
        is_public = False
        public_url = None
        try:
            is_public = GLOBAL_READ_ACL in headers.get('x-container-read', '')
            """
            if is_public:
                swift_endpoint = base.url_for(request,
                                              'object-store',
                                              endpoint_type='publicURL')
                parameters = urlparse.quote(container_name.encode('utf8'))
                public_url = swift_endpoint + '/' + parameters
            """
            ts_float = float(headers.get('x-timestamp'))
            timestamp = datetime.utcfromtimestamp(ts_float).isoformat()
        except Exception:
            raise
        container_info = {
            'name': container_name,
            'container_object_count': headers.get('x-container-object-count'),
            'container_bytes_used': headers.get('x-container-bytes-used'),
            'timestamp': timestamp,
            'data': data,
            'is_public': is_public,
            #'public_url': public_url,
        }
        return common_success_response([container_info], "Get container detail done")

    def POST(self):
        return web.forbidden(" Post Method is not supported ")


class Swift_Create_Container:
    def POST(self):
        data = web.input().data
        auth_spec = get_auth_spec(data)
        data = json.loads(data)
        container_name = data['container_name']
        metadata = data.get('metadata', {})
        try:
            if not container_name:
                return common_error_response("Container name is required")
            if swift_container_exists(container_name, auth_spec):
                return common_error_response("Container with name %s is already existed" % container_name)
            headers = _metadata_to_header(metadata)
            created_container = swift_api(**auth_spec).put_container(container_name, headers=headers)
            print "created container is " + str(created_container)
            return common_success_response([{"name": container_name}], "Create a container successfully")
        except Exception as e:
            return common_error_response("Create container failed, error is %s" % e)

    def GET(self):
        return web.forbidden(" GET Method is not supported ")


class Swift_Update_Container:

    def POST(self):
        data = web.input().data
        auth_spec = get_auth_spec(data)
        data = json.loads(data)
        container_name = data['container_name']
        metadata = data['metadata']
        headers = _metadata_to_header(metadata)
        if not container_name:
            return common_error_response("Container name is required")
        try:
            swift_api(**auth_spec).post_container(container_name, headers=headers)
            return common_success_response([{'name': container_name}], "update a container successfully!")
        except Exception as e:
            return common_error_response("Update a container is failed, error is %s"%e)

    def GET(self):
        return web.forbidden(" Post Method is not supported ")


class Swift_Delete_Container:
    def POST(self):
        # It cannot be deleted if it's not empty. The batch remove of objects
        # be done in swiftclient instead of Horizon.
        data = web.input().data
        auth_spec = get_auth_spec(data)
        data = json.loads(data)
        container_name = data['container_name']
        if not container_name:
            return common_error_response("Container name is required")
        objects, more = swift_get_objects(container_name, auth_spec)
        if objects:
            error_msg = "The container cannot be deleted since it is not empty."
            return common_error_response(error_msg)
        try:
            swift_api(**auth_spec).delete_container(container_name)
            return common_success_response([], "delete a container successfully")
        except Exception as e:
            return common_error_response("delete a container is failed, error is %s" % e)

    def GET(self):
        return web.forbidden(" GET Method is not supported ")

class Swift_Get_Objects:
    def GET(self):
        data = web.input()
        limit = None
        prefix = None
        marker = None
        auth_spec = get_auth_spec(data)
        LOG.debug("container name: %s" % data.get('container_name').replace(' ', '+'))
        container_name = unicode(base64.b64decode(data.get('container_name').replace(' ', '+')), "utf8", errors="ignore")
        if not container_name:
            return common_error_response("Container name is required")
        limit = limit or getattr(settings, 'API_RESULT_LIMIT', 1000)
        kwargs = dict(prefix=prefix,
                      marker=marker,
                      limit=limit + 1,
                      delimiter=FOLDER_DELIMITER,
                      full_listing=True)
        try:
            headers, objects = swift_api(**auth_spec).get_container(container_name,
                                                                    **kwargs)
            object_objs = _objectify(objects, container_name)
            return common_success_response(object_objs, "Get container objects successfully!")
        except Exception as e:
            return common_error_response("Get container objects failed! error is %s" %e)

    def POST(self):
        return web.forbidden(" POST Method is not supported ")


class Swift_Filter_Objects:

    def Get(self):
        # FIXME(kewu): Swift currently has no real filtering API, thus the marker
        # parameter here won't actually help the pagination. For now I am just
        # getting the largest number of objects from a container and filtering
        # based on those objects.
        data = web.input().data
        container_name = data.get('container_name')
        object_name = data.get('object_name')
        with_data = data.get('with_data', None)
        filter_string = data.get('filter_string', '')
        if not container_name:
            return common_error_response("Container name is required")
        auth_spec = get_auth_spec(data)
        limit = 9999
        prefix = None
        marker = None
        objects = swift_get_objects(container_name,
                                    auth_spec,
                                    prefix=prefix,
                                    marker=marker,
                                    limit=limit)
        filter_string_list = filter_string.lower().strip().split(' ')

        def matches_filter(obj):
            for q in filter_string_list:
                return wildcard_search(obj.name.lower(), q)

        return common_success_response([filter(matches_filter, objects[0])], "filter successfully!")

    def GET(self):
        return web.forbidden(" GET Method is not supported ")



class Swift_Copy_Object:
    def POST(self):
        data = json.loads(web.input().data)
        auth_spec = get_auth_spec(data)
        new_container_name = data.get('new_container_name')
        new_object_name = data.get('new_object_name')
        orig_container_name = data.get('orig_container_name')
        orig_object_name = data.get('orig_object_name')
        if not new_container_name:
            return common_error_response("Container name is required")
        if swift_object_exists(new_container_name, auth_spec, object_name=new_object_name):
            return common_error_response("new container name with %s is already existed, please use another name" % new_container_name)

        headers = {"X-Copy-From": FOLDER_DELIMITER.join([orig_container_name,
                                                         orig_object_name])}
        try:
            # TODO: What exactly the return is.
            updated_object = swift_api(**auth_spec).put_object(new_container_name,
                                              new_object_name,
                                              None,
                                              headers=headers)
            return common_success_response([], "copy object successfully!")
        except Exception as e:
            return common_error_response("Copy object failed, error is %s!" %e)

    def GET(self):
        return web.forbidden(" GET Method is not supported ")

MAX_FILE_SIZE = 5 * 1024 ** 3 # 5GB
SEGMENT_SIZE = MAX_FILE_SIZE - int(round(0.1 * 1024 ** 3)) # 4.9GB

class Swift_Upload_Object:
    def POST(self):
        headers = {}
        size = 0
        data = json.loads(web.input().data)
        print data
        container_name = data['container_name']
        object_name = data['object_name']
        object_file = data['upload_file']
        file_size = data['file_size']
        if not container_name:
            return common_error_response("Container name is required")
        
        opts = {
            'os_auth_url': data['auth_url'],
            'os_username': data['user'],
            'os_password': data['key'],
            'os_tenant_name': data['tenant_name']
        }
        if file_size >= MAX_FILE_SIZE:
            opts['segment_size'] = SEGMENT_SIZE
        with SwiftService(options=opts) as swift:
            try:
                obj = SwiftUploadObject(object_file, object_name=object_name)
                for r in swift.upload(container_name, [obj]):
                    if 'action' in r and r['action'] == 'upload_object':
                        if r['success']:
                            return common_success_response([r], "Upload object successfully!")
                        else:
                            error = r['error']
                            return common_error_response("Upload object is failed, error is %s" % error.value)
            except Exception as e:
                return common_error_response("Upload object is failed, error is %s" % e.value)
        
    def GET(self):
        return web.forbidden(" GET Method is not supported ")


class Swift_Create_Pseudo_Folder:
    def POST(self):
        # Make sure the folder name doesn't already exist.
        data = web.input().data
        auth_spec = get_auth_spec(data)
        data = json.loads(data)
        container_name = data['container_name']
        pseudo_folder_name = data['pseudo_folder_name'] + "/"
        path = data['path']
        print "path is " + path
        if path:
            pseudo_folder_name = "/".join([data['path'].rstrip("/"),
                                           data['pseudo_folder_name']]) + "/"
        print pseudo_folder_name
        if not container_name:
            return common_error_response("Container name is required")

        if swift_object_exists(container_name, auth_spec, object_name=pseudo_folder_name):
            name = pseudo_folder_name.strip('/')
            return common_error_response("pseudo_folder_name with name %s is already existed!"%pseudo_folder_name)
        headers = {}
        try:
            etag = swift_api(**auth_spec).put_object(container_name,
                                                 obj=pseudo_folder_name,
                                                 contents=None,
                                                 headers=headers)
            obj_info = {
                'name': pseudo_folder_name,
                'etag': etag
            }

            return common_success_response([obj_info], "create pseudo folder done")
        except Exception as e:
            return common_error_response("create pseudo folder failed, error is %s" %e)


    def GET(self):
        return web.forbidden(" GET Method is not supported ")


class Swift_Delete_Object:
    def POST(self):
        data = web.input().data
        auth_spec = get_auth_spec(data)
        data = json.loads(data)
        container_name = data['container_name']
        object_name = data.get('object_name')
        if not container_name:
            return common_error_response("Container name is required")
        try:
            swift_api(**auth_spec).delete_object(container_name, object_name)
            return common_success_response([], "Swift object delete is done")
        except Exception as e:
            return common_error_response("Delete a swift object is failed, error is %s" %e)

    def GET(self):
        return web.forbidden(" GET Method is not supported ")

class Swift_Delete_Folder:
    def POST(self):
        data = web.input().data
        auth_spec = get_auth_spec(data)
        data = json.loads(data)
        container_name = data['container_name']
        object_name = data.get('object_name')
        if not container_name:
            return common_error_response("Container name is required")
        objects, more = swift_get_objects(container_name, auth_spec,
                                          prefix=object_name)
        # In case the given object is pseudo folder,
        # it can be deleted only if it is empty.
        # swift_get_objects will return at least
        # one object (i.e container_name) even if the
        # given pseudo folder is empty. So if swift_get_objects
        # returns more than one object then only it will be
        # considered as non empty folder.
        if len(objects) > 1:
            return common_error_response("The pseudo folder cannot be deleted since it is not empty.")
        try:
            swift_api(**auth_spec).delete_object(container_name, object_name)
            return common_success_response([], "The pseudo folder is deleted")
        except Exception as e:
            return common_error_response("The pseudo folder cannot be deleted since it is %s" %e)

    def GET(self):
        return web.forbidden(" GET Method is not supported ")

#Please refer to /usr/lib/python2.7/site-packages/swiftclient/client.py# class _RetryBody for more download details
class Swift_Get_Object:
    def GET(self):
        data = web.input()
        with_data = data.get('with_data')
        resp_chunk_size = CHUNK_SIZE
        LOG.debug("container name: %s" % data.get('container_name').replace(' ', '+'))
        container_name = unicode(base64.b64decode(data.get('container_name').replace(' ', '+')), "utf8", errors="ignore")
        LOG.debug("object name: %s" % data.get('object_name').replace(' ', '+'))
        object_name = unicode(base64.b64decode(data.get('object_name').replace(' ', '+')), "utf8", errors="ignore")
        LOG.debug("download to: %s" % data.get('download_to').replace(' ', '+'))
        download_to = unicode(base64.b64decode(data.get('download_to').replace(' ', '+')), "utf8", errors="ignore")
        LOG.debug("%s, %s" % (object_name, download_to))
        try:
            if not container_name:
                return common_error_response("Container name is required")
            if not download_to:
                return common_error_response("Path to save download file is required")
            return swift_download_object(path.dirname(download_to), {\
                'user': data.get('user'),\
                'key': data.get('key'),\
                'auth_url': data.get('auth_url'),\
                'tenant_name': data.get('tenant_name'),\
                'container_name': container_name,\
                'object_name': object_name,\
                'orig_name': path.basename(download_to),\
                'with_data': 1\
            })
            # auth_spec = get_auth_spec(data)
            # if with_data:
                # headers, data = swift_api(**auth_spec).get_object(
                    # container_name, object_name, resp_chunk_size=resp_chunk_size)
            # else:
                # data = None
                # headers = swift_api(**auth_spec).head_object(container_name,
                                                         # object_name)
            # orig_name = headers.get("x-object-meta-orig-filename")
            # timestamp = None
            # try:
                # ts_float = float(headers.get('x-timestamp'))
                # timestamp = datetime.utcfromtimestamp(ts_float).isoformat()
            # except Exception:
                # pass
            # obj_info = {
                # 'name': object_name,
                # # FIXME :This should a httpresponse
                # 'data': data,
                # 'orig_name': orig_name,
                # 'bytes': headers.get('content-length'),
                # 'content_type': headers.get('content-type'),
                # 'etag': headers.get('etag'),
                # 'timestamp': timestamp,
            # }
            # return common_success_response([obj_info], "get object successfully!")
        except Exception as e:
            return common_error_response(" Get object failed, error is %s" %e)


    def POST(self):
        return web.forbidden(" POST Method is not supported ")


class Swift_GET_Capabilities:
    def GET(self):
        data = web.input()
        auth_spec = get_auth_spec(data)
        try:
            # TODO: format cs
            cs = swift_api(**auth_spec).get_capabilities()
            return common_success_response([cs.to_dict()], "get capabilities done")
        # NOTE(tsufiev): Ceph backend currently does not support '/info', even
        # some Swift installations do not support it (see `expose_info` docs).
        except Exception as e:
            return common_error_response("get Capabilities failed error is %s" % e)


    def POST(self):
        return web.forbidden(" POST Method is not supported ")


def start_monitor():
    agent.watch()
    reporter.watch()

def stop_monitor():
    agent.unwatch()
    reporter.unwatch()

CMD = {
    'start_monitor': start_monitor,
    'stop_monitor': stop_monitor
}

class cmd:
    def POST(self):
        data = json.loads(web.input().data)
        try:
            if str(settings['reserv_id']) == str(data['reserv_id']):
                CMD[data['method']]()
                return web.ok()
            else:
                return web.forbidden("Bad reserv_id")
        except KeyError, e:
            return web.notfound("No such method: %s" % data['method'])

    def GET(self):
        ret = {
            'success': False,
            'title': None,
            'list': None,
            'msg': None
        }
        ret['success'] = True
        ret['title'] = ['%cpu', '%mem', '%diskIO', '%netIO']
        ret['status'] = [0.5, 0.5, 0.5, 0.5]
        return json.dumps(ret)


class pslist:
    def GET(self, mode):
        ret = {
            'success': False,
            'title': None,
            'list': None,
            'msg': None
        }
        if mode == '0':
            ret['success'] = True
            ret['title'] = ['pid', 'name']
            ret['list'] = dc.get_proc_list(0)
            return json.dumps(ret)
        elif mode == '1':
            ret['success'] = True
            ret['title'] = ['pid', 'name', '%cpu', '%mem', 'diskIO Bps', 'netIO Bps']
            ret['list'] = dc.get_proc_list(1)
            return json.dumps(ret)
        else:
            ret['success'] = False
            ret['msg'] = "bad argument [0-1]"
            return json.dumps(ret)

class watch_process:
    def POST(self):
        data = web.input()
        try:
            dc.proc_watch(json.loads(data.procs))
            ret = {
                'success': True,
                'msg': "%s are watched" % data.procs
            }
        except Exception, e:
            ret = {
                'success': False,
                'msg': str(e)
            }
            LOG.debug(repr(e))
            # print repr(e)
        return json.dumps(ret)

class unwatch_process:
    def POST(self):
        data = web.input()
        try:
            dc.proc_unwatch(json.loads(data.procs))
            ret = {
                'success': True,
                'msg': "%s are unwatched" % data.procs
            }
        except Exception, e:
            ret = {
                'success': False,
                'msg': str(e)
            }
            LOG.debug(repr(e))
            # print repr(e)
        return json.dumps(ret)

class vm_status:
    def GET(self):
        ret = {
            'success': False,
            'title': None,
            'list': None,
            'msg': None
        }
        ret['success'] = True
        ret['title'] = ['%cpu', '%mem', '%diskIO', '%netIO']
        ret['status'] = [0.5, 0.5, 0.5, 0.5]
        return json.dumps(ret)

def run(*args, **kwargs):
    app = web.application(urls, globals(), *args, **kwargs)
    app.run()

if __name__ == '__main__':
    run()

