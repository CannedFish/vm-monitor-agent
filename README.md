# vm-monitor-agent

## Setup
1. Download this pageage.
2. Run "python setup.py install" at root path of this package.

### Configuration on Windows
3. Configure environment virable of "win32" and "pywin32_system32" which are located in "%PYTHON%/Lib/site-packages".
4. Move etc directory to the root path of python installed like "C:\etc".
5. Make some configuration on etc/vma.conf.
6. Execute "proc_info_service.exe --startup auto install" with admin.
7. Execute "proc_info_service.exe start" with admin.
8. Check log file which is configured at vma.conf.

### Configuration on Linux
3. Move etc directory to the root path.
4. Make some confiuration.
5. Execute "vm_agent" to startup.
6. Configure to a daemon process.

## Development
```shell
pip install virtualenv
virtualenv .venv
.venv/bin/pip install -r requirements.txt
```
