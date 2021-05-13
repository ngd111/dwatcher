#-*- encoding:utf-8 -*-
from datetime import datetime, timedelta, date

import logging
import logging.handlers
import os

class util_hs:
    def get_today(self):
        return datetime.now().strftime("%Y%m%d")

    def get_yesterday(self):
        return self.add_days(self.get_today(), -1)

    def get_current_timeline_datehour(self):
        _datehour = datetime.now().strftime("%Y%m%d%H")
        return self.add_hours(_datehour + "0000", -1)[:10]

    def get_pure_filename(self, _fullfilename):
        if isinstance(_fullfilename, str) == False:
            raise TypeError("_fullfilename must be str type")

        if len(_fullfilename) == 0:
            raise ValueError("_fullfilename must be set")

        return os.path.basename(_fullfilename.rstrip('/'))

class log(object):

    def __init__(self, _loggerName, _logFileName):
        #self.logger = logging.getLogger(_loggerName)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        filehandler = logging.handlers.RotatingFileHandler(_logFileName, mode='a',
                maxBytes=1024*1024, backupCount=2, encoding="UTF-8")

        #filehandler = logging.FileHandler(_logFileName, "a", encoding="UTF-8")
        filehandler.setLevel(logging.INFO)

        streamhandler = logging.StreamHandler()
        #streamhandler.setLevel(logging.INFO)
        streamhandler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        filehandler.setFormatter(formatter)

        self.logger.addHandler(filehandler)
        self.logger.addHandler(streamhandler)
        self.level = "debug"

    def __del__(self):
        try:
            del self.logger
        except NameError as e:
            print('exception: ', e.args)

    # level : standard, debug
    def set_loglevel(self, _level):
        self.level = _level

    def write_log(self, _level, _text):
        if _level == "info":
            self.logger.info(_text)
        elif _level == "warning":
            self.logger.warning(_text)
        elif _level == "error":
            self.logger.error(_text)
        elif _level == "critical":
            self.logger.critical(_text)
        elif _level == "debug":
            if self.level == "debug":
                self.logger.debug(_text)
                #self.logger.setLevel(logging.DEBUG)
            else:
                pass
        else:
            raise ValueError("_level must be set one of [\"info\", \"warning\", \"error\", \"critical\", \"debug\"]")

