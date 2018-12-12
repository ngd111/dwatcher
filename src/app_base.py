#-*- coding: utf-8 -*-
"""
    (C) Copyright Hansol Inticube co, Ltd. 2017
        Writer : Jin Kak, Jung
        Revision history :
            First released on Apr, 30, 2017
"""

from abc import ABCMeta, abstractmethod

import pyinotify
import Queue
import signal

from util_hs import log, util_hs

class directory_watcher(object):
    def __init__(self):
        #print 'directory_watcher __init__'
        super(directory_watcher, self).__init__()
        pass

    def __del__(self):
        #print 'directory_watcher __del__'
        self._release_resource()

    def __exit__(self):
        self._release_resource()
        
    def _release_resource(self):
        if self.q_files != None:
            del self.q_files
            self.q_files = None

    def set_directory_watcher_option(self, _data_directory):
        self.q_files = Queue.Queue()
        wm = pyinotify.WatchManager()
        mask = pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_MOVED_TO
        wm.add_watch(_data_directory, mask, rec=True)

        class NotifyHandler(pyinotify.ProcessEvent):
            def process_IN_CLOSE_WRITE(self_inner, event):
                try:
                    self.q_files.put(event.pathname)
                    #print "File was close write:", event.pathname
                except Exception, e:
                    raise e

            def process_IN_MOVED_TO(self_inner, event):
                try:
                    self.q_files.put(event.pathname)
                    #print "File was moved to directory:", event.pathname
                except Exception, e:
                    raise e

            def process_IN_DELETE(self_inner, event):
                pass

        self.notifier = pyinotify.ThreadedNotifier(wm, NotifyHandler())

class app_base(object):

    def __init__(self, _use_directory_watcher = False, _directory_name = ""): 
        #print 'app_base __init__'
        #super(app_base, self).__init__()
        if _use_directory_watcher == True and _directory_name == "":
            raise ValueError("_directory_name parameter is not set")

        self.utils = util_hs()

        if _use_directory_watcher == True:
            self.dw = directory_watcher()
            self.dw.set_directory_watcher_option(_directory_name)
        else:
            self.dw = None

        self.exit_directory_watcher_thread = False

    def __del__(self):
        #print 'app_base __del__'
        if self.dw != None:
            del self.dw
            self.dw = None
        if self.utils != None:
            del self.utils
            self.utils = None

    @abstractmethod
    def signal_handler(self, signal, frame):
        pass

    @abstractmethod
    def run(self):
        pass

    
