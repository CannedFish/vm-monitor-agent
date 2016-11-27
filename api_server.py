# -*- coding: utf-8 -*-
import web
import json

import data_collector as dc

urls = (
    '/api/proc/list/(\d)', 'pslist',
    '/api/proc/watch', 'watch_process',
    '/api/proc/unwatch', 'unwatch_process',
    '/api/vm/status', 'vm_status'
)

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
            ret['title'] = ['pid', 'name', '%cpu', '%mem', 'diskIO MBps', 'netIO Mbps']
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
            print repr(e)
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
            print repr(e)
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

