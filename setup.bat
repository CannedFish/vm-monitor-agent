@ECHO OFF

SET perm=T
IF "%1" EQU "" SET perm=F
IF "%2" EQU "" SET perm=F
IF "%perm%" EQU "F" (
    ECHO Usage: setup.bat username password
    GOTO EOF
)

SET usr=%1
SET pwd=%2

ECHO #1 Install code and configuration
python setup.py install || GOTO EOF
ECHO #2 Register and start ProcInfo service
sc create ProcInfo binPath= vm_agent.exe start= auto || GOTO EOF
ECHO #3 Register and start AgentRabbit service
sc create AgentRabbit binPath= agent_rabbit.exe start= auto obj= %usr% password= %pwd% || GOTO EOF
ECHO Setup successfully!!
ECHO Service name: ProcInfo, AgentRabbit

:EOF
