import web
import json

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
            ret['list'] = [(1, 'a'), (2, 'b')]
            return json.dumps(ret)
        elif mode == '1':
            ret['success'] = True
            ret['title'] = ['pid', 'name', '%cpu', '%mem', '%diskIO', '%netIO']
            ret['list'] = [(1, 'a', 0.5, 0.5, 0.5, 0.5), (2, 'b', 0.5, 0.5, 0.5, 0.5)]
            return json.dumps(ret)
        else:
            ret['success'] = False
            ret['msg'] = "bad argument [0-1]"
            return json.dumps(ret)

class watch_process:
    def POST(self):
        data = web.input()
        return "%s watched" % data.procs

class unwatch_process:
    def POST(self):
        data = web.input()
        return "%s unwatched" % data.procs

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

app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()

