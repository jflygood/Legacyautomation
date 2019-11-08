#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author=lihan
@version=2.0
Current this only can run in linux, if want to run in windows, need to modify dbconnection.py
"""

import getopt
import os
import sys
import time
from DBconnection.dbconnection import dbconnection
from util.util import *
from Constants import *

def Usage():
    print 'Generate new task Usage is as folllowing:\n'
    print '-h,--help: print help message.\n'
    print '-s --statusFpath:esgstatus.properties file path. In jenkins server, it is under directory /share/root/legacyautomation \n'
    print '-e --esgip : esg ip .--esgip  10.226.38.1 \n'
    print '---------exemple-------------------\n'

    print 'python GenerateNewTask.py --statusFpath Z:\\legacyautomation  --esgip 10.226.38.1\n'

def main(argv):
    esgip=""
    status_file_path = ""

    #print "----argv----",argv
    if len(argv)<3:
        Usage()
        sys.exit(2)
    try:
        options, args = getopt.getopt(argv[1:], 's:e:h',["statusFpath=","esgip=","--help"])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    for opt, arg in options:
        if opt in ('-h', '--help'):
            Usage()
            sys.exit(0)
        elif opt in ('-s', '--statusFpath'):
            status_file_path = arg
        elif opt in ('-e','--esgip'):
            esgip = arg
        else:
            print 'unhandled option'
            Usage()
            sys.exit(2)

    # xmlfile_path = "U:\\LegacyAutomation\\regression\\"
    # xmlfile_name="test.xml"
    casefile=getxmlfilepath(status_file_path,esgip)
    pid=getpid(esgip)
    old_taskid = getold_task_id(casefile)
    new_taskid=generateNewTask(old_taskid)
    print "type of new_taskid",type(new_taskid)
    print "new_taskid=",new_taskid
    # pid='1014'
    updated_task_id(casefile,new_taskid)
    updated_pid(casefile,pid)

def updated_task_id(xmlfile,task_id):
    try:
        # file = xmlfile_path + xmlfile_name
        para_namevalue = {}
        para_namevalue['taskid'] = task_id

        # para_namevalue['pid'] = '1013'
        # new_file = xmlfile_path + new_xmlfilename
        xmlParserFile(xmlfile).update_parameter_value(para_namevalue, xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        # print root.tag
        # print root.attrib
        for child in root:
            print "taskid=", child.tag, child.attrib
        print child.attrib
    except Exception as e:
        print "Update task id failed. Exception -" + str(e)


def updated_pid(xmlfile,pid):
    try:
        # file = xmlfile_path + xmlfile_name
        para_namevalue = {}
        para_namevalue['pid'] = pid
        # para_namevalue['pid'] = '1013'
        # new_file = xmlfile_path + new_xmlfilename
        xmlParserFile(xmlfile).update_parameter_value(para_namevalue, xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        # print root.tag
        # print root.attrib
        for child in root:
            print "pid=", child.tag, child.attrib
        print child.attrib
    except Exception as e:
        print "Update pid failed. Exception -" + str(e)


def getold_task_id(xmlfile):
    try:
        # file = xmlfile_path + xmlfile_name
        namevalue = xmlParserFile(xmlfile).get_parameter_dic()
        old_taskid = namevalue['taskid']
        print "old_taskid=", old_taskid
    except Exception as e:
        print "Get old task id failed. Exception -" + str(e)
    return old_taskid

def generateNewTask(old_taskid):
    dbconnect=dbconnection();
    connection = dbconnect.connect();
    cursor = connection.cursor()
    print "Get old task name......"
    SQLCommand = " select top 1 task_name FROM [esgautomationdb].[dbo].[esg_test_task]  where test_task_id=" + old_taskid + " order by test_task_id desc "
    cursor.execute(SQLCommand)
    oldtask_name = cursor.fetchone()[0]
    print "oldtask_name=" + oldtask_name
    task_name = oldtask_name + time.strftime("_%m%d%H%M%S")
    try:
        print "Create new task......"
        SQLCommand = "execute  dbo.usp_esg_automation_new_task_insert 14, 1010, " + "'" + task_name + "'" + ", 'test', 1, 0, 0, 0, 1"
        cursor.execute(SQLCommand)
        cursor.commit()
        print "Get new task id......"
        SQLCommand = " select top 1 test_task_id FROM [esgautomationdb].[dbo].[esg_test_task]  where task_name='" + task_name + "' order by test_task_id desc "
        cursor.execute(SQLCommand)
        taskid = str(cursor.fetchone()[0])
        print "taskid=" + taskid
        print "Get old task case mapping list......"
        SQLCommand = "SELECT  [id],[test_task_id],[test_case_id],[case_seq],[test_case_instance_id],[instance_seq] FROM [esgautomationdb].[dbo].[esg_test_task_case_mapping] where test_task_id=" + old_taskid
        cursor.execute(SQLCommand)
        rows = []
        for row in cursor:
            print "row=", row
            rows.append(row)
        print "rows=", rows
        for row in rows:
            test_case_id = row[2]
            print "test_case_id=", str(test_case_id)
            print "---", type(test_case_id)
            print "---taskid=", type(taskid)
            case_seq = row[3]
            print "----case_seq=", type(case_seq)
            test_case_instance_id = row[4]
            print "----test_case_instance_id=", type(test_case_instance_id)
            instance_seq = row[5]
            print "----instance_seq=", type(instance_seq)
            print "insert new records to DB"
            SQLCommand = "insert into [esgautomationdb].[dbo].[esg_test_task_case_mapping](test_task_id,test_case_id,case_seq,test_case_instance_id,instance_seq) " \
                         "values (" + taskid + "," + str(test_case_id) + "," + str(case_seq) + "," + str(
                test_case_instance_id) + "," + str(instance_seq) + ")"
            print "SQLcOMMAND=", SQLCommand
            cursor.execute(SQLCommand)
            cursor.commit()
    except Exception as e:
        dbconnect.closeconnect()
        print "Execute SQL command failed. Exception -" + str(e)
    dbconnect.closeconnect()
    return taskid

def getpid(esgip):
    global cwd
    try:
        cwd = os.getcwd()
        pid = ""
        file_ops = FileOperations(cwd, esg_pid_map, 'r')
        content = file_ops.readfile()
        listline = content.split("\n")
        find_esg = esgip
        for index, value in enumerate(listline):
            if find_esg in value:
                print "find_esg=", find_esg
                esgpidmap = value.strip().split("=")
                pid = esgpidmap[1]
                break
    except Exception as e:
        print "Get pid failed. Exception -" + str(e)
    return pid

"""
Read from esgstatus.properties to get test case file
"""
def getxmlfilepath(status_file_path,esgip):
    try:
        file_ops = FileOperations(status_file_path, status_file_name, 'r')
        content = file_ops.readfile()
        listline = content.split("\n")
        find_xml = esgip + "_xml"
        casefile=""
        for index, value in enumerate(listline):
            if find_xml in value:
                casefile=value.split("=")[1]
    except Exception as e:
        print "Get case file failed. Exception -" + str(e)
    print "case file=",casefile
    casefile.replace("\\\\","\\")
    print "case file=", casefile
    return casefile


if __name__ == '__main__':
    main(sys.argv)