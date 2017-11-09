# -*- coding: utf-8 -*-

from settings import app_data_root, conf_file_path, dir_to_be_monitored \
        , db_file_path, SYSTEM, conf_dir

import sqlite3
import os

def main():
    if not os.path.exists(app_data_root):
        os.makedirs(app_data_root)

    if not os.path.exists(conf_file_path):
        if SYSTEM == 'Linux':
            if not os.path.exists(conf_dir):
                os.makedirs(conf_dir)
            os.system("cp etc/agent-rabbit.conf %s" % conf_dir)
        elif SYSTEM == 'Windows':
            import win32file
            win32file.CopyFile('etc/agent-rabbit.conf', conf_file_path, 0)
        else:
            raise ValueError("We are not support %s now." % SYSTEM)

    if not os.path.exists(dir_to_be_monitored):
        os.makedirs(dir_to_be_monitored)

    db_conn = sqlite3.connect(db_file_path)
    for sql_file in ['vm_monitor_agent/agent_rabbit/scripts/info.sql', 'vm_monitor_agent/agent_rabbit/scripts/messages.sql']:
        with file(sql_file, 'r') as fd:
            sql_str = fd.read()
            cur = db_conn.cursor()
            cur.execute(sql_str)
    db_conn.commit()
    db_conn.close()
