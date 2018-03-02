# -*- coding: utf-8 -*-

import datetime
import json
from os import path

from swift_common import get_auth_spec, swift_api, Container, common_success_response, common_error_response, GLOBAL_READ_ACL, \
    swift_container_exists, _metadata_to_header, swift_get_objects, FOLDER_DELIMITER, _objectify, wildcard_search, \
    swift_object_exists, CHUNK_SIZE
from swiftclient.service import SwiftService, SwiftError, SwiftUploadObject



def get_user_all_containers(request, data):
    """
    Get user's account. A account contains one or many containers according to the user.
    :param request: 
    :param data: 
    
        data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name"
        }
    :return: 
    
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
    try:
        auth_spec = get_auth_spec(data)
        headers, containers = swift_api(**auth_spec).get_account()
        containerobjs = [Container(container).to_dict() for container in containers]
        msg = "Get containers list successfully"
        return common_success_response(containerobjs, msg)
    except Exception as e:
        return common_error_response("Get containers list failed, error is %s" %e)



def container_existed(request, data):
    """
    Detect a container is existed or not.
    :param request: 
    :param data:
     
        data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name",
            "container_name: "container_name"
        }
     
    :return: 
        {
            u'msg': u'containerisexisted',
            u'results': [],
            u'errcode': 1
        }
    """
    container_name = data.get('container_name')
    if not container_name:
        return common_error_response("Container name is required")

    try:
        auth_spec = get_auth_spec(data)
        swift_api(**auth_spec).head_container(container_name)
        return common_success_response([], "container is existed")
    except Exception as e:
        return common_error_response("container is not existed")


def object_existed(request, data):
    """
    Detect a object is existed or not.
    :param request: 
    :param data: 
    
        data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name",
            "container_name": "container_name",
            "object_name": "object_name"
        }
    
    
    :return: 
    
            {
                u'msg': u'objectisnotexisted',
                u'results': [],
                u'errcode': 0
            }
    """
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


def get_container(request, data):
    """
    Get a container content. This will return the list of objects in the container.
    If set with_data to 1, it will fetch the data of the container.That is the object list. 
    :param request: 
    :param data: 
        
        data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name",
            "container_name": "container_name",
            "with_data": "0" or "1"
        }
        
        without data:
        {
                u'msg': u'Get container detail done', 
                u'results':
                    [{
                        u'container_object_count': u'3', 
                        u'name': u'dongdong', 
                        u'timestamp': u'2017-10-28T23:06:31.115380', 
                        u'container_bytes_used': u'725173', 
                        u'is_public': False, 
                        u'data': None
                    }]
                u'errcode': 1
        }

        with data:
    
            {
                u'msg': u'Get container detail done', 
                u'results': [{
                        u'container_object_count': u'3', 
                        u'name': u'dongdong', 
                        u'timestamp': u'2017-10-28T23:06:31.115380', 
                        u'container_bytes_used': u'725173', 
                        u'is_public': False, 
                        u'data': u'dir/\nfolder0de8cdfc-3e4a-4a23-ba82-d182eafda654/folderb43fbb9c-7726-4a0c-823d-f16755b710c1/\nsetuptools-36.6.0.zip'}], 
                u'errcode': 1
            }

    
    
    :return: objects list
    """
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


def create_container(request, data):
    """
    Create a container with public or private.
    :param request: 
    :param data: 
    
    
        data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name",
            "container_name": "container_name",
            "metadata": {"is_public": False} # default to False
        }
    
    :return: 
    
        {
            u'msg': u'Createacontainersuccessfully',
            u'results': [
                {
                    u'name': u'config96b81929-aa78-472e-a61e-b9cb7bb50f81'
                }
            ],
            u'errcode': 1
        }
    """
    auth_spec = get_auth_spec(data)
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


def update_container(request, data):
    """
    Update container between public and private.
    :param request: 
    :param data:
     
         
        data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name",
            "container_name": "container_name",
            "metadata": {"is_public": False}
        }
    
    :return: 
    
    
            {
                u'msg': u'updateacontainersuccessfully!',
                u'results': [
                    {
                        u'name': u'config96b81929-aa78-472e-a61e-b9cb7bb50f81'
                    }
                    ],
                u'errcode': 1
            }
    
    
    """

    auth_spec = get_auth_spec(data)
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



def delete_container(request, data):
    """
    Delete a container.It cannot be deleted if it's not empty. The batch remove of objects be done in swiftclient
    :param request: 
    :param data: 
    
        data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name",
            "container_name": "container_name",
        }
    
    
    :return: 
    
        {
            u'msg': u'deleteacontainersuccessfully',
            u'results': [],
            u'errcode': 1
        }
    
    """

    auth_spec = get_auth_spec(data)
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


def get_objects(request, data):
    """
    
    Get the detailas of objects in a container.
    :param request: 
    :param data: 
    
            data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name",
            "container_name": "container_name",
            }
    
    :return: 
    
        {
            u'msg': u'Get container objects successfully!', 
            u'results': 
                [
                    {u'subdir': u'dir/'}, 
                    {u'subdir': u'folder0de8cdfc-3e4a-4a23-ba82-d182eafda654/'}, 
                    {u'hash': u'74663b15117d9a2cc5295d76011e6fd1', u'last_modified': u'2017-10-28T23:11:25.072Z', u'bytes': 725173, u'name': u'setuptools-36.6.0.zip'}
                ], 
            u'errcode': 1
        }
    
    """
    limit = None
    prefix = None
    marker = None
    auth_spec = get_auth_spec(data)
    container_name = data.get('container_name')
    if not container_name:
        return common_error_response("Container name is required")
    limit = limit or 1000
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



def filter_objects(request, data):
    """
    Filter objects by str.    
    # FIXME(kewu): Swift currently has no real filtering API, thus the marker
    # parameter here won't actually help the pagination. For now I am just
    # getting the largest number of objects from a container and filtering
    # based on those objects.
    :param request: 
    :param data: 
    :return: 
    """

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



def copy_object(request, data):
    """
    Copy object from one object to grand new object.
    :param request: 
    :param data: 
        data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "new_container_name": new_created_container,
        "new_object_name": new_created_object,
        "orig_container_name": CONTAINER_NAME,
        "orig_object_name": OBJECT_NAME
    }
    :return: 
    
    """
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

MAX_FILE_SIZE = 5 * 1024 ** 3 # 5GB
SEGMENT_SIZE = MAX_FILE_SIZE - int(round(0.1 * 1024 ** 3)) # 4.9GB

def upload_object(data):
    """
    Upload object is uploading file to an existed object or create a new one.
    # :param request:
    :param data: 
    
            data = {
                "user": USER,
                "key": KEY,
                "auth_url": AUTH_URL,
                "tenant_name": TENANT_NAME,
                "container_name": CONTAINER_NAME,
                "object_name": new_created_object,
                "orig_file_name":  f.name, #filename,
                "upload_file": FILE_PATH,
                "file_size": BYTES_OF_THIS_FILE
            }
    # :param files:
        # files = {'upload_file': ('test.txt',open("/tmp/test.txt", 'rb'))}
    :return: 
    
    
        {
            u'msg': u'Uploadobjectissuccessfully!',
            u'results': [
                {
                    u'etag': u'cde100e18faa796115785428dec30f7b',
                    u'bytes': 0,
                    u'name': u'object6a003e93-581c-4512-b79b-124c3da2c901'
                }
            ],
            u'errcode': 1
        }
    
    
    """
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
                        return common_error_response("Upload object is failed, error is %s" % error)
        except Exception as e:
            return common_error_response("Upload object is failed, error is %s" % e.value)
    # headers = {}
    # size = 0
    # auth_spec = get_auth_spec(data)
    # container_name = data['container_name']
    # object_name = data['object_name']
    # object_file = files['upload_file']
    # if not container_name:
        # return common_error_response("Container name is required")
    # if object_file:
        # headers['X-Object-Meta-Orig-Filename'] = data['orig_file_name']
        # # headers['content-type'] = data['content_type']
        # #size = object_file.size
    # try:
        # etag = swift_api(**auth_spec).put_object(container_name,
                                             # object_name,
                                             # object_file,
                                             # #content_length=size,
                                             # headers=headers)

        # obj_info = {'name': object_name, 'bytes': size, 'etag': etag}
        # return common_success_response([obj_info], "Upload object is successfully!")
    # except Exception as e:
        # return common_error_response("Upload object is failed, error is %s" %e)


def create_pseduo_folder(request, data):
    """
    Create a pseudo folder.
    :param request: 
    :param data: 
        
        data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": CONTAINER_NAME,
        "pseudo_folder_name": pseudo_folder_name,
        #"path":""
        "path":"folder0de8cdfc-3e4a-4a23-ba82-d182eafda654/"
    }
    :return: 
    
    """
    # Make sure the folder name doesn't already exist.
    auth_spec = get_auth_spec(data)
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


def delete_object(request, data):
    """
    Delete object
    :param request: 
    :param data:
     
         data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": new_created_container,
        "object_name": new_created_object,
    }
     
     
    :return: 
        {
            u'msg': u'Deleteaswiftobjectisfailed,
            errorisObjectDELETEfailed: http: //192.168.1.7: 7480/swift/v1/config/object6a003e93-581c-4512-b79b-124c3da2c901404NotFoundNoSuchKey',
            u'results': [
        
            ],
            u'errcode': 0
        }
    """
    auth_spec = get_auth_spec(data)
    container_name = data['container_name']
    object_name = data.get('object_name')
    if not container_name:
        return common_error_response("Container name is required")
    try:
        swift_api(**auth_spec).delete_object(container_name, object_name)
        return common_success_response([], "Swift object delete is done")
    except Exception as e:
        return common_error_response("Delete a swift object is failed, error is %s" %e)


def detele_folder(request, data):
    auth_spec = get_auth_spec(data)
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



#Please refer to /usr/lib/python2.7/site-packages/swiftclient/client.py# class _RetryBody for more download details
def get_object(request, data):
    """
    Download a file from object.
    :param request: 
    :param data: 
    
    
            data = {
            "user": "username",
            "key": "password",
            "auth_url": "keystone_auth_url",
            "tenant_name": "tenant_name",
            "container_name": "container_name",
            "object_name": "object_name",
            "orig_name": "orig_name",
            "content_type": "content_type",
            "with_data": "1"
        }
    
    :return: 
    
    
        [
            {
                "name": "setuptools-36.6.0.zip",
                "timestamp": null,
                "bytes": "725173",
                "orig_name": "setuptools-36.6.0.zip",
                "etag": "74663b15117d9a2cc5295d76011e6fd1",
                "content_type": "binary/octet-stream",
                "data": null
            }
            ],
            "errcode": 1
        }

    """
    with_data = data.get('with_data')
    resp_chunk_size = CHUNK_SIZE
    container = data.get('container_name')
    objects = [data.get('object_name')]
    try:
        options = {
            'os_auth_url': data.get('auth_url'),
            'os_username': data.get('user'),
            'os_password': data.get('key'),
	        'os_tenant_name': data.get('tenant_name'),
			'out_file': path.join(request, data.get('orig_name'))
        }

        with SwiftService(options=options) as swift:
            try:
                down_iter = swift.download(container=container, objects=objects)
                return common_success_response([down for down in down_iter], "get object successfully!")
            except SwiftError as e:
                return common_error_response(" Get object failed, error is %s" %e)

    except Exception as e:
        return common_error_response(" Get object failed, error is %s" %e)


def get_capabilities(request, data):
    """
    This function is not supported by ceph.
    :param request: 
    :param data: 
    :return: 
    """
    auth_spec = get_auth_spec(data)
    try:
        # TODO: format cs
        cs = swift_api(**auth_spec).get_capabilities()
        return common_success_response([cs.to_dict()], "get capabilities done")
    # NOTE(tsufiev): Ceph backend currently does not support '/info', even
    # some Swift installations do not support it (see `expose_info` docs).
    except Exception as e:
        return common_error_response("get Capabilities failed error is %s" % e)
	
if __name__ == "__main__":
    data = {
        "user": "yes",
        "key": "123",
        "auth_url": "http://192.168.1.89:5000/v2.0",
        "tenant_name": "yes",
        "container_name": "test_swift",
        "object_name": "nidaye.xls",
        "with_data": "1"
    }

    # Example:
    request = "C:/clouddoc"
    return_json = get_object(request, data)
    print return_json

