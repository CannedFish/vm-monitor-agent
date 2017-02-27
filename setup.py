from setuptools import setup, find_packages
import os
import sys
import platform

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(HERE, 'vm_monitor_agent'))

SYSTEM = platform.system()

REQs = ['psutil==5.0.0', 'requests==2.11.1', 'web.py==0.38']

if SYSTEM == 'Linux':
    ENTRY = ['vm_agent = vm_monitor_agent.main:main',]
elif SYSTEM == 'Windows':
    REQs.append('pypiwin32==219')
    ENTRY = ['proc_info_service = vm_monitor_agent.win_service:win_main',]
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

if __name__ == '__main__':
    main()

