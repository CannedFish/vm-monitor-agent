# -*- coding: utf-8 -*-

from vm_monitor_agent import swift
from settings import dir_to_be_monitored

print "Test upload:"
swift.upload_object('', {
    'user': "yes", 
    'key': '123',
    'auth_url': 'http://192.168.1.89:5000/v2.0',
    'tenant_name': 'yes', 
    'container_name': 'dongdong',
    'object_name': 'test-abc',
    'orig_file_name': 'setuptools-36.6.0.zip'
}, {
    'upload_file': ('setuptools-36.6.0.zip', open('/root/clouddoc/setuptools-36.6.0.zip', 'rb'))
})

