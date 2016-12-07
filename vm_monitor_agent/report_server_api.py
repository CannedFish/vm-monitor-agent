# -*- coding: utf-8 -*-
# Wrapper APIs of server to be reported
import logging

LOG = logging.getLogger()

from config import settings
from common import do_get, do_post
import data_collector as dc

_METHOD_TYPE = {
    'vm': '116116',
    'proc': '116117'
}

def send_report(data, mode):
    if not isinstance(data, dict) \
            and not isinstance(data, list):
        raise ValueError('Bad value, must be dict or list' % type(data))
    if not mode == 'vm' and not mode == 'proc':
        raise ValueError('% is send, must be vm or proc' % mode)
    if mode == 'vm':
        data['instance_id'] = settings['instance_id']
    else:
        data = {
            'instance_id': settings['instance_id'],
            'data': data
        }
    s_data = {
        'method': _METHOD_TYPE[mode],
        'data': data,
        'session_id': '11111111'
    }
    # re = do_post(settings['metadata_server_ip'], s_data)
    # if not re['success']:
        # return do_post(settings['host_server_ip'], s_data)
    # return re
    LOG.debug("send %s report:\n%s" % (mode, s_data))
    return True

# For metadata type
from common import MyThread
import time

import data_collector as dc

class MetadataChecker(MyThread):
    def __init__(self, delay):
        super(MetadataChecker, self).__init__('MetadataChecker', 2)
        self._delay = delay

    def work(self):
        ret = self._check_watch_list()
        if ret['success']:
            watch_list = ret['data']
            watched = dc.proc_watched()
            LOG.debug(watch_list, watched)
            dc.proc_watch(filter(lambda x: x not in watched, watch_list))
            dc.proc_unwatch(filter(lambda x: x not in watch_list, watched))
        time.sleep(self._delay)
    
    def _check_watch_list(self):
        url = settings['metadata_server_ip'] + 'watchlist/'
        # return __do_get(url)
        return {
            'success': True,
            'data': [1, 2, 3, 4, 5, 6]
        }

if settings['cmd_way'] == 'meta_serv':
    meta_checker = MetadataChecker(3)

class DataReport(MyThread):
    def __init__(self, delay):
        super(DataReport, self).__init__('DataReport', 3)
        self._delay = delay

    def work(self):
        # If use metadata server, send all alive proc's info in interal
        send_report(dc.get_proc_list(1), 'proc')
        send_report(dc.get_vm_status(), 'vm')
        time.sleep(self._delay)

reporter = DataReport(settings['report_interval'])

