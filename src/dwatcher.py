# -*- coding: utf-8 -*-
"""
   (C) Copyright Hansol Inticube Ltd,
   Writer : Jin Kak, Jung
   Revision history : 
       First released on July, 21, 2018
"""

# Import OS related packages
from os import listdir, _exit
from os.path import isfile
import signal, sys, time

from db_handler import db_handler
from app_base import app_base, directory_watcher

import json
from util_hs import log

class dwatcher(app_base):

    def __init__(self, _name):
        global process_name
        global log_filename
        global data_directory

        process_name = _name
        try:
            self._read_config("./" + process_name + ".conf")
        except Exception, e:
            sys.exit(-1)

        log_filename = self.dir_log + "/" + self.logfilename + ".log"
        data_directory = self.dir_data
        self.CONST_PINGINTERVAL=60

        super(dwatcher, self).__init__(
                _use_directory_watcher = True, _directory_name = data_directory)

    def __enter__(self):
        self.logger = log(process_name.upper() + " main", log_filename)
        self.logger.set_loglevel(self.loglevel)

        # print configuration setting
        self._print_config_setting()

        # set signal handler
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGUSR1, self.signal_handler)

        self.db_proc = db_handler(log_filename, self.db_host, self.db_port, self.db_user,
                self.db_password, _parent=self)
        self.reload_config = False

        self.logger.write_log("debug", "Enter to app")

    def __exit__(self, type, value, traceback):
        self.logger.write_log("debug", "Exit from app")

    def _read_config(self, _filename):
        try:
            with open(_filename) as f:
                data  = json.load(f)
            self.dir_log = data["directory"]["log"]
            self.dir_data = data["directory"]["recording_storage"]
            self.dir_webdav_base = data["directory"]["webdav_base"]
            self.logfilename = data["log"]["filename"]
            self.loglevel = data["log"]["level"]
            self.db_host = data["db"]["host"]
            self.db_port = data["db"]["port"]
            self.db_user = data["db"]["user"]
            self.db_password = data["db"]["password"]
            self.filecopy_use = data["filecopy"]["use"]
            self.filecopy_target = data["filecopy"]["target"]
        except Exception as e:
            self.logger.write_log("critical", ("config file open error => {0}:".format(e)))
            raise e

    def _print_config_setting(self):
        self.logger.write_log("info", ("Log directory : %s" % self.dir_log))
        self.logger.write_log("info", ("Recording storage : %s" % self.dir_data))
        self.logger.write_log("info", ("WebDav Base URI : %s" % self.dir_webdav_base))
        self.logger.write_log("info", ("Log filename  : %s" % self.logfilename))
        self.logger.write_log("info", ("Log level     : %s" % self.loglevel))

    def signal_handler(self, signal, frame):
        self.logger.write_log("warning", "signal caught %d" % signal)
        if signal == 15:
            self.logger.write_log("critical", ("Program is terminated %d" % signal))
            self.exit_directory_watcher_thread = True
        elif signal == 10:
            self.reload_config = True

    def run(self):
        self.dw.notifier.start()
        pinginterval = self.CONST_PINGINTERVAL
        while True:
            filenames = []
            while not self.dw.q_files.empty():
                filename = self.dw.q_files.get()
                if filename[-4:] != ".mp3":
                    pass
                else:
                    self.logger.write_log("debug", ("event collector : %s" % filename))
                    filenames.append(filename)

                self.dw.q_files.task_done()

            if len(filenames) > 0:
                # DB insert function
                self.logger.write_log("debug", ('start time : %f' % time.time()))
                self.db_proc.do_job(filenames, self.dir_webdav_base, self.filecopy_use, self.filecopy_target)
                self.logger.write_log("debug", ('end   time : %f' % time.time()))
            if self.exit_directory_watcher_thread == True:
                self.dw.q_files.join()
                break

            if self.reload_config == True:
                try:
                    self._read_config("./" + process_name + ".conf")
                    print('loglevel : %s' % self.loglevel)
                    self.logger.set_loglevel(self.loglevel)
                    self.logger.write_log("warning", "configuration file reloaded")
                except Exception, e:
                    self.logger.write_log("error", e)
                finally:
                    self.reload_config = False

            time.sleep(700.0 / 1000.0)
            pinginterval-=1
            if pinginterval == 0:
                self.db_proc.do_ping()
                pinginterval = self.CONST_PINGINTERVAL

        self.dw.notifier.stop()

if __name__=='__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    app = dwatcher("dwatcher")

    try:
        with app:
            app.run()
    except KeyboardInterrupt:
        try:
            app.logger.write_log('warning','Interrupt occurred. Program is terminated')
            sys.exit(0)
        except SystemExit:
            _exit(0)

    sys.exit(0)
