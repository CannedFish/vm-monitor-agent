# -*- coding: utf-8 -*-
import web
import json
import logging

LOG = logging.getLogger()

import data_collector as dc
import agent
from report_server_api import reporter
from config import settings

urls = (
    '/api/cmd', 'cmd',
    # '/api/proc/list/(\d)', 'pslist',
    # '/api/proc/watch', 'watch_process',
    # '/api/proc/unwatch', 'unwatch_process',
    # '/api/vm/status', 'vm_status'
)

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
            if settings['reserv_id'] == data['reserv_id']:
                CMD[data['method']]()
                return web.ok()
            else:
                return web.forbidden("Bad reserv_id")
        except KeyError, e:
            return web.notfound("No such method: %s" % data['method'])

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

