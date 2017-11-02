# -*- coding: utf-8 -*-

import json
import swiftclient
import logging

from base import APIDictWrapper
from config import settings


LOG = logging.getLogger()

FOLDER_DELIMITER = "/"
CHUNK_SIZE = 512 * 1024
# Swift ACL
GLOBAL_READ_ACL = ".r:*"
LIST_CONTENTS_ACL = ".rlistings"

def common_success_response(data, msg):
    if isinstance(data, list):
        return json.dumps({"results": data, "errcode": 1, "msg": msg})
    else:
        return json.dumps({"results": [data], "errcode": 1, "msg": msg})


def common_error_response(msg):
    return json.dumps({"results": [], "errcode": 0, "msg": msg})

def _metadata_to_header(metadata):
    headers = {}
    public = metadata.get('is_public')

    if public is True:
        public_container_acls = [GLOBAL_READ_ACL, LIST_CONTENTS_ACL]
        headers['x-container-read'] = ",".join(public_container_acls)
    elif public is False:
        headers['x-container-read'] = ""

    return headers



def wildcard_search(string, q):
    q_list = q.split('*')
    if all(map(lambda x: x == '', q_list)):
        return True
    elif q_list[0] not in string:
        return False
    else:
        if q_list[0] == '':
            tail = string
        else:
            head, delimiter, tail = string.partition(q_list[0])
        return wildcard_search(tail, '*'.join(q_list[1:]))


class Container(APIDictWrapper):
    pass


def swift_api(**kwargs):
    """
    Auth version is 2 by default.We support preauthtoken and user/key authentication.
    For keystone v2:
    conn = Connection(
    authurl=_authurl,
    user=_user,
    key=_key,
    tenant_name=_tenant_name,
    auth_version=_auth_version
    )

    For keystone v3:
    _authurl = 'http://127.0.0.1:5000/v3/'
    _auth_version = '3'
    _user = 'tester'
    _key = 'testing'
    _os_options = {
        'user_domain_name': 'Default',
        'project_domain_name': 'Default',
        'project_name': 'Default'
    }
    conn = Connection(
        authurl=_authurl,
        user=_user,
        key=_key,
        os_options=_os_options,
        auth_version=_auth_version
    )

    For keystone session:
    from keystoneauth1 import session
    from keystoneauth1.identity import v3

    # Create a password auth plugin
    auth = v3.Password(auth_url='http://127.0.0.1:5000/v3/',
                       username='tester',
                       password='testing',
                       user_domain_name='Default',
                       project_name='Default',
                       project_domain_name='Default')

    # Create session
    keystone_session = session.Session(auth=auth)

    # Create swiftclient Connection
    swift_conn = Connection(session=keystone_session)
    :return: 
    """
    LOG.info("Try to get connection")
    preauthtoken = kwargs.get('preauthtoken')
    print "preauthtoken is " + str(preauthtoken)
    user = kwargs.get("user")
    auth_version = kwargs.get("auth_version", 2)
    # If go preauthtoken, return swiftclient.client.Connection
    if preauthtoken:
        preauthurl = kwargs.get('auth_url')  # 'http://192.168.1.7:7480/swift/v1'
        print "preauthurl is " + str(preauthurl)
        conn = swiftclient.client.Connection(None, user, None, preauthtoken=preauthtoken,
                                             preauthurl=preauthurl, auth_version=auth_version)
        return conn
    key = kwargs.get("key")
    auth_url = kwargs.get("auth_url")
    tenant_name = kwargs.get("tenant_name")
    conn = swiftclient.Connection(user=user, key=key, authurl=auth_url, auth_version=auth_version,
                                  tenant_name=tenant_name)
    return conn


# TODO: This should support keystone auth token.
def get_auth_spec(data):
    auth_spec = {}
    try:
        if isinstance(data, unicode):
            data = json.loads(data)
        user = data.get('user')
        if not user:
            raise
        key = data.get('key')
        auth_url = ''
        if data.has_key('auth_url'):
            auth_url = data['auth_url']  # data.get('auth_url')
        else:
            auth_url = data['preauthurl']
        preauthtoken = ''
        if data.has_key('preauthtoken'):
            preauthtoken = data['preauthtoken']
        # auth api version is 2 by default.
        auth_version = data.get("auth_version", 2)
        tenant_name = data.get('tenant_name',user)  # data.get('tenant_name')
        if not tenant_name:
            tenant_name = user
        if not auth_version:
            auth_version = 2
        auth_spec = {
            "user": user,
            "key": key,
            "auth_url": auth_url,
            "tenant_name": tenant_name,
            "auth_version": auth_version,
            'preauthtoken':preauthtoken
        }
    except Exception as e:
        raise
        LOG.exception("Get auth spec failed, error is " + str(e))
    return auth_spec

# For api usage
def swift_container_exists(container_name,auth_spec):
    try:
        swift_api(**auth_spec).head_container(container_name)
        return True
    except swiftclient.client.ClientException:
        return False


def swift_object_exists(container_name, auth_spec, object_name):
    try:
        swift_api(**auth_spec).head_object(container_name, object_name)
        return True
    except swiftclient.client.ClientException:
        return False


class StorageObject(APIDictWrapper):
    def __init__(self, apidict, container_name, orig_name=None, data=None):
        super(StorageObject, self).__init__(apidict)
        self.container_name = container_name
        self.orig_name = orig_name
        self.data = data

    @property
    def id(self):
        return self.name


class PseudoFolder(APIDictWrapper):
    def __init__(self, apidict, container_name):
        super(PseudoFolder, self).__init__(apidict)
        self.container_name = container_name

    @property
    def id(self):
        return '%s/%s' % (self.container_name, self.name)

    @property
    def name(self):
        return self.subdir.rstrip(FOLDER_DELIMITER)

    @property
    def bytes(self):
        return None

    @property
    def content_type(self):
        return "application/pseudo-folder"

def _objectify(items, container_name):
    """Splits a listing of objects into their appropriate wrapper classes."""
    objects = []

    # Deal with objects and object pseudo-folders first, save subdirs for later
    for item in items:
        if item.get("subdir", None) is not None:
            object_cls = PseudoFolder
        else:
            object_cls = StorageObject

        objects.append(object_cls(item, container_name).to_dict())

    return objects

def swift_get_objects(container_name, auth_spec, prefix=None, marker=None,
                      limit=None):
    limit = limit or getattr(settings, 'API_RESULT_LIMIT', 1000)
    kwargs = dict(prefix=prefix,
                  marker=marker,
                  limit=limit + 1,
                  delimiter=FOLDER_DELIMITER,
                  full_listing=True)
    headers, objects = swift_api(**auth_spec).get_container(container_name,
                                                        **kwargs)
    object_objs = _objectify(objects, container_name)

    if(len(object_objs) > limit):
        return (object_objs[0:-1], True)
    else:
        return (object_objs, False)
