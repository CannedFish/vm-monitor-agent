# api test
import requests, json

r = requests.get('http://0.0.0.0:9999/api/proc/list/0')
print "proc list mode 0: %s" % r.json()

r = requests.get('http://0.0.0.0:9999/api/proc/list/1')
print "proc list mode 1: %s" % r.json()

data = [0, 1, 2, 3, 4]
r = requests.post('http://0.0.0.0:9999/api/proc/watch', data='procs='+json.dumps(data))
print "proc watch: %s" % r.json()

r = requests.post('http://0.0.0.0:9999/api/proc/unwatch', data='procs='+json.dumps(data))
print "proc watch: %s" % r.json()

# TODO: test data collection

