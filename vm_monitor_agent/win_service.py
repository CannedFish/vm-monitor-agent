# -*- coding: utf-8 -*-
import win32serviceutil
import win32service
import win32event

from config import settings
import main

import logging
LOG = logging.getLogger()

class ProcInfoService(win32serviceutil.ServiceFramework):
    """ 
    Usage: 'CMD [options] install|update|remove|start [...]|stop|restart [...]|debug [...]' 
    Options for 'install' and 'update' commands only: 
     --username domain\username : The Username the service is to
       run under 
     --password password : The password for the username 
     --startup [manual|auto|disabled|delayed] : How the service
       starts, default = manual 
     --interactive : Allow the service to interact with the desktop. 
     --perfmonini file: .ini file to use for registering performance
       monitor data 
     --perfmondll file: .dll file to use when querying the service for 
       performance data, default = perfmondata.dll 
    Options for 'start' and 'stop' commands only: 
     --wait seconds: Wait for the service to actually start or stop. 
                     If you specify --wait with the 'stop' option, 
                     the service and all dependent services will be 
                     stopped, each waiting the specified period.
    """

    _svc_name_ = "ProcInfoService"
    _svc_display_name_ = "Process Information Collect Service"
    _svc_description_ = "Process information collect service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework\
                .__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isAlive = True

    def SvcDoRun(self):
        import time
        LOG.info("Service start...")
        main.main()

    def SvcStop(self):
        LOG.info("Service stop...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.isAlive = False
        main.exit_handler(2, None)

def win_main():
    win32serviceutil.HandleCommandLine(ProcInfoService)

if __name__ == '__main__':
    win_main()

