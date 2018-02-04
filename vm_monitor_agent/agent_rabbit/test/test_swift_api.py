# -*- coding: utf-8 -*-

from vm_monitor_agent import swift

print "Test upload:"
ret = swift.upload_object('', {
    'user': "yes", 
    'key': '123',
    'auth_url': 'http://192.168.1.52:5000/v2.0',
    'tenant_name': 'yes', 
    'container_name': 'test',
    'object_name': 'answer-20180204121800.txt',
    'orig_file_name': 'answer.txt'
}, {
    'upload_file': open('C:\\test_config\\clouddoc\\answer.txt', 'rb')
})
print ret

