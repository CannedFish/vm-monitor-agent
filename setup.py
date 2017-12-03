# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import sys
import platform

from vm_monitor_agent.agent_rabbit import setup as agent_rabbit_setup 

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(HERE, 'vm_monitor_agent'))

SYSTEM = platform.system()

REQs = ['psutil==5.0.0', \
        'requests>=2.11.1', \
		'web.py==0.38', \
		'pika==0.10.0', \
		'python-swiftclient==3.1.0', \
		'python-keystoneclient==3.5.1',]

if SYSTEM == 'Linux':
    REQs.append('pyinotify==0.9.4')
    ENTRY = [
        'vm_agent = vm_monitor_agent.main:main',
        'agent_rabbit = vm_monitor_agent.agent_rabbit.main:main'
    ]
elif SYSTEM == 'Windows':
    REQs.append('pypiwin32==219')
    ENTRY = [
        'vm_agent = vm_monitor_agent.main:main',
        'proc_info_service = vm_monitor_agent.win_service:win_main',
        'agent_rabbit_service = vm_monitor_agent.agent_rabbit.win_service:win_main',
        'agent_rabbit = vm_monitor_agent.agent_rabbit.main:main'
    ]
else:
    raise ValueError("We are not support %s now." % SYSTEM)

def main():
    setup_args = dict(
        name="vm_monitor_agent",
        version="0.5.1",
        description="Process infomation collection",
        author="CannedFish Liang",
        author_email="lianggy0719@126.com",
        url="https://github.com/CannedFish/vm-monitor-agent",
        platforms="Windows, Linux",
        license="BSD",
        packages=find_packages(),
        install_requires=REQs,
        package_data={'': ['etc/vma.conf']},
        entry_points={
            'console_scripts': ENTRY
        }
    )
    setup(**setup_args)

    agent_rabbit_setup.main()

if __name__ == '__main__':
    main()

