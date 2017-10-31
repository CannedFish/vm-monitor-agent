# -*- coding: utf-8 -*-
import main

import win32serviceutil
import win32service
import win32event

import logging
LOG = logging.getLogger(__name__)

class ProcInfoService(win32serviceutil.ServiceFramework):
    """ 
    Usage: 'CMD [options] install|update|remove|start [...]|stop|restart [...]|debug [...]' 
    Options for 'install' and 'update' commands only: 
     --username domain\username : The Username the service is to
       run under 
     --password password : The password for the username 
     --startup=[manual|auto|disabled|delayed] : How the service
       starts, default is manual 
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

    _svc_name_ = "AgentRabbitService"
    _svc_display_name_ = "Agent Rabbit Service"
    _svc_description_ = "Agent rabbit service to consume messages"

    def __init__(self, args):
        win32serviceutil.ServiceFramework\
                .__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isAlive = True

    def SvcDoRun(self):
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

