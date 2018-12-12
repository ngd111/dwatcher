# -*- coding: utf-8 -*-
"""
    (C) Copyright Hansol Inticube co, Ltd 2018
        Writer : Jin Kak, Jung
            Revision History :
            First released on July, 20, 2018
"""
from abc import ABCMeta, abstractmethod
import logging
import os
import weakref
from util_hs import log, util_hs


# for future use

class proc_base(object):
    __metaclass__ = ABCMeta

    def __init__(self, _log_filename, _parent):
        self.parent = weakref.ref(_parent)
        self.utils = util_hs()
        self.logger = _parent.logger
        self.logger.write_log("debug", "Base object initialized")

    def __del__(self):
        del self.utils

    def _get_pure_filename(self, _fullfilename):
        if isinstance(_fullfilename, str) == False:
            raise TypeError("_fullfilename must be str type")

        if len(_fullfilename) == 0:
            raise ValueError("_fullfilename must be set")

        return os.path.basename(_fullfilename.rstrip('/'))
        
    @abstractmethod
    def do_job(self, _filename_list):
        pass
