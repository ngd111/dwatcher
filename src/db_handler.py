# -*- coding: utf-8 -*-
"""
    (C) Copyright Hansol Inticube 2018
        Writer : Jin Kak, Jung
            Revision History :
            First released on July, 20, 2018
"""
import logging

#import sqlite3
import pymysql
import re
from proc_base import proc_base
import shutil
from util_hs import util_hs

class db_handler(proc_base):

    def __init__(self, _log_filename, _db_host, _db_port, _db_user, _db_password, _parent):
        proc_base.__init__(self, _log_filename, _parent)
        self.connect_database(_db_host, _db_port, _db_user, _db_password)
        self.regex_pattern = re.compile(r'[A-Z0-9]*_(\d{4})-(\d\d)-(\d\d)_(\d\d)')
        self.regex_pattern_calluuid = re.compile(r'[A-Z0-9]*')
        self.CONST_FILEKEY_LEN = 43
        self.logger.write_log("debug", "DB handler object initialized")
        self.util_hsobj = util_hs()

    def __del__(self):
        self.disconnect_database()
        self.logger.write_log("debug", "DB handler object deinitalized")

    def connect_database(self, _db_host, _db_port, _db_user, _db_password):
	self.conn = pymysql.connect(host=_db_host, port=_db_port, user=_db_user,
                password=_db_password, db='recording',charset='utf8', autocommit=False)
        self.curs = self.conn.cursor()
        #self.conn = sqlite3.connect("recording.db", isolation_level=None)
        #self.conn = sqlite3.connect("/recordings/data/recording.db")
        ##self.conn.execute('pragma journal_mode=wal;')
        #self.conn.execute('pragma journal_mode=OFF;')
        #self.conn.execute('pragma synchronous=OFF;')
        #self.conn.execute('pragma cache_size=10000;')

    def disconnect_database(self):
        self.conn.close()

    def do_ping(self):
        self.conn.ping(reconnect=True)

    def insert_recording(self, _datum):
        #sql = "insert into recording(calluuid, filepath, calldate) values(?, ?, ?)"
        #sql = "insert into recording(calluuid, filepath, calldate) values(%s, %s, %s)"
        sql = "insert into recording(calluuid, filepath, calldate) values(%s, %s, %s)"
        try:
            self.curs.executemany(sql, _datum)
            self.conn.commit()
            self.logger.write_log('info', ("%d records committed" % len(_datum)))
        except Exception, e:
            self.conn.rollback()
            msg = "exception : insert error => {0}, calluuid => {1}".format(e, _datum)
            self.logger.write_log("error", msg)


    # get recording file directory
    def _get_recording_path(self, _filename, _webdav_base):
        if len(_filename) < self.CONST_FILEKEY_LEN:
            raise ValueError("Filename length is not valid")

        basefilename = self._get_pure_filename(_filename)

        try:
            matchobj = self.regex_pattern.search(basefilename)
            rec_key = matchobj.group()
            yyyy = matchobj.group(1)
            mm = matchobj.group(2)
            dd = matchobj.group(3)
            hh = matchobj.group(4)

            matchobj = self.regex_pattern_calluuid.search(rec_key)
            calluuid = matchobj.group()
        except Exception, e:
            msg = "exception : regex error => {0}, _filename => {1}".format(e, _filename)
            self.logger.write_log("error", msg)
            return ()


        fullpath = _webdav_base + "/" + yyyy + "/" + mm + "/" + dd + "/" + hh + "/" + basefilename
        calldate = yyyy + mm + dd
        return (calluuid, fullpath, calldate)

    def do_job(self, _filename_list, _webdav_base, _filecopy_use, _filecopy_target):
        n = len(_filename_list)
        if n <= 0:
            return

        temp_list = []
        
        while n > 0:
            ret_tup = self._get_recording_path(_filename_list[n-1], _webdav_base)
            if len(ret_tup) > 0:
                temp_list.append(ret_tup)
                if _filecopy_use == "Y":
                    print(_filename_list[n-1])
                    _basefilename = self.util_hsobj.get_pure_filename(_filename_list[n-1])
                    _calldate = ret_tup[2]
                    print(_basefilename)
                    print(_calldate)
                    shutil.copyfile(_filename_list[n-1], _filecopy_target + '/' + _calldate[0:4] +
                            '/' + _calldate[4:6] + '/' + _calldate[6:8] + '/' + _basefilename)
                    #shutil.copyfile(_filename_list[n-1], _filecopy_target + '/' + _basefilename)
            n -= 1


        result_tup = tuple(temp_list)
        # db insert
        self.insert_recording(result_tup)


