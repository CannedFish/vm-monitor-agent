@ECHO OFF

IF "%1" EQU "" (
    ECHO Usage: setup.bat path_to_python_script
    GOTO EOF
)

SET python_path=%1

SET svc1="ProcInfoService"
SET svc2="AgentRabbitService"

ECHO #1 Install code and configuration
python setup.py install || GOTO EOF
ECHO #2 Register and start ProcInfo service
sc create %svc1% binPath= "%python_path%/vm_agent.exe" start= auto || GOTO EOF
ECHO #3 Register and start AgentRabbit service
sc create %svc2% binPath= "%python_path%/agent_rabbit.exe" start= auto || GOTO EOF
ECHO Setup successfully!!
ECHO Service name: %svc1%, %svc2%

:EOF
