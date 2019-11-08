#!/usr/bin/env python
import pypyodbc
import time
import Constants
from Constants import *


class dbconnection():
    def __init__(self):
        pass

    def connect(self):
        # ###Linux
        # self.conn = pypyodbc.connect('DSN=MyMSSQLServer;Database=' + Constants.db_name + ';uid=' + Constants.db_user + ';pwd=' + Constants.db_pwd + '')

         ##Windows
        self.conn = pypyodbc.connect('Driver={SQL Server};'
                                'Server=' + Constants.db_ip + ';'
                                                              'Database=' + Constants.db_name + ';'
                                                                                                'uid=' + Constants.db_user + ';pwd=' + Constants.db_pwd + '')
        return self.conn

    def closeconnect(self):
        self.conn.close()