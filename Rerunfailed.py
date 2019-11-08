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
import xml.etree.ElementTree as ET
import shutil

def Usage():
    print 'Generate new task Usage is as folllowing:\n'
    print '-h,--help: print help message.\n'
    print '-s --statusFpath:esgstatus.properties file path. In jenkins server, it is under directory /share/root/legacyautomation \n'
    print '-e --esgip : esg ip .--esgip  10.226.38.1 \n'
    print '---------exemple-------------------\n'

    print 'python GenerateNewTask.py --statusFpath Z:\\legacyautomation  --esgip 10.226.38.1\n'

cwd=""




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
    task_name = oldtask_name + "_"+time.strftime("%m%d%H%M%S") + "Re"+old_taskid
    try:


        print "******************************************"
        print "Get old task case mapping list......"
        SQLCommand = "exec dbo.usp_esg_automation_get_task_items  " + old_taskid + " , 14"
        cursor.execute(SQLCommand)
        rows = []
        for row in cursor:
            rows.append(row)
        taskitems_dic = {"test_module_id": 0, "path": "", "class_name": "", "method_name": "", "test_case_id": "",
                         "test_case_name": "", "group_name": "", "case_seq": 0, "instance_ids": "",
                         "disable_checks": ""}
        taskitemlist = []
        for row in rows:
            taskitems_dic["test_module_id"] = row[0]
            taskitems_dic["path"] = row[1]
            taskitems_dic["class_name"] = row[2]
            taskitems_dic["method_name"] = row[3]
            taskitems_dic["test_case_id"] = str(row[4])
            taskitems_dic["test_case_name"] = row[5]
            taskitems_dic["group_name"] = row[6]
            taskitems_dic["case_seq"] = row[7]
            taskitems_dic["instance_ids"] = row[8]
            taskitems_dic["disable_checks"] = row[9]
            # print "taskitems_dic=",taskitems_dic
            taskitemlist.append(taskitems_dic)
            taskitems_dic = {"test_module_id": 0, "path": "", "class_name": "", "method_name": "", "test_case_id": 0,
                             "test_case_name": "", "group_name": "", "case_seq": 0, "instance_ids": "",
                             "disable_checks": ""}
        print "====================================="
        # print taskitemlist
        print "taskitemlist length=", len(taskitemlist)

        print "******************************************"
        print "Get old task failed case instance id list......"
        SQLCommand = "exec dbo.usp_esg_automation_get_failed_cases_from_log  " + old_taskid
        cursor.execute(SQLCommand)
        failedinstanceid_list = []
        for row in cursor:
            failedinstanceid_list.append(str(row))
        print "failedinstanceid_list=", failedinstanceid_list

        if len(failedinstanceid_list)==0:
            print "len(failedinstanceid_list) = ",len(failedinstanceid_list)
            return 0
        print "******************************************"
        print "Get old task failed case mapping list......"
        taskitemfailed_list = []
        for ins_id in failedinstanceid_list:
            ins_id = ins_id.replace("L,", "").strip("(").strip(")")
            for taskitem in taskitemlist:
                if ins_id in taskitem["instance_ids"]:
                    taskitemfailed_list.append(taskitem)
                    break
        # print "taskitemfailed_list=", taskitemfailed_list
        # print "length of taskitemfailed list=", len(taskitemfailed_list)
        print "******************************************"
        print "Get rerun instance id(not only failed instance id)......"
        ## Because one case may have many instances, if only fail one instance, all the other instances in this case also need to run
        reruninstanceids = ""
        for taskitem in taskitemfailed_list:
            if taskitem["instance_ids"] not in reruninstanceids:
                reruninstanceids = taskitem["instance_ids"] + reruninstanceids
        # print "reruninstanceid_list=", reruninstanceids
        reruninstanceids = reruninstanceids.strip(";")
        reruninstanceID_list = reruninstanceids.split(";")
        reruninstanceID_list_int = []
        # print "reruninstanceID_list=", reruninstanceID_list
        for value in reruninstanceID_list:
            reruninstanceID_list_int.append(int(value))
        # print "reruninstanceID_list_int=", reruninstanceID_list_int
        reruninstanceID_list_int.sort()
        print "reruninstanceID_list_int=", reruninstanceID_list_int
        print "******************************************"
        print "Get rerun case list(not only failed case list)......"
        reruncase_list = []
        for ins_id in reruninstanceID_list_int:
            SQLCommand = "SELECT  [id],[test_task_id],[test_case_id],[case_seq],[test_case_instance_id],[instance_seq] FROM [esgautomationdb].[dbo].[esg_test_task_case_mapping] where test_task_id=" + old_taskid + "  and test_case_instance_id=" + str(
                ins_id)
            # print "SQLCOMMAND=", SQLCommand
            cursor.execute(SQLCommand)
            for row in cursor:
                reruncase_list.append(row)
        print "reruncase_list=", reruncase_list

        print "Create new task......"
        SQLCommand = "execute  dbo.usp_esg_automation_new_task_insert 14, 1010, " + "'" + task_name + "'" + ", 'test', 1, 0, 0, 0, 1"
        cursor.execute(SQLCommand)
        cursor.commit()
        print "Get new task id......"
        SQLCommand = " select top 1 test_task_id FROM [esgautomationdb].[dbo].[esg_test_task]  where task_name='" + task_name + "' order by test_task_id desc "
        cursor.execute(SQLCommand)
        taskid = str(cursor.fetchone()[0])
        print "taskid=" + taskid

        print "******************************************"
        print "Insert rerun cases into new task......"
        for reruncase in reruncase_list:
            SQLCommand = "insert into [esgautomationdb].[dbo].[esg_test_task_case_mapping](test_task_id,test_case_id,case_seq,test_case_instance_id,instance_seq) " \
                         "values (" + taskid + "," + str(reruncase[2]) + "," + str(reruncase[3]) + "," + str(
                reruncase[4]) + "," + str(reruncase[5]) + ")"
            # print "SQLcOMMAND=", SQLCommand
            cursor.execute(SQLCommand)
            cursor.commit()
    except Exception as e:
        dbconnect.closeconnect()
        print "Execute SQL command failed. Exception -" + str(e)
    dbconnect.closeconnect()
    return taskid


def getTaskname(taskid):
    dbconnect = dbconnection();
    connection = dbconnect.connect();
    cursor = connection.cursor()
    try:
        print "Get Task name......"
        SQLCommand = " select top 1 task_name FROM [esgautomationdb].[dbo].[esg_test_task]  where test_task_id=" + taskid + " order by test_task_id desc "
        cursor.execute(SQLCommand)
        task_name = cursor.fetchone()[0]
        print "Task_name=" + task_name
    except Exception as e:
        dbconnect.closeconnect()
        print "Execute SQL command failed. Exception -" + str(e)
    dbconnect.closeconnect()
    return task_name

def generateReruntask(old_taskid,new_taskid,pid):
    dbconnect = dbconnection();
    connection = dbconnect.connect();
    cursor = connection.cursor()

    try:
        print "******************************************"
        print "Get old task case mapping list......"
        SQLCommand = "exec dbo.usp_esg_automation_get_task_items  "+ old_taskid + " , 14"
        cursor.execute(SQLCommand)
        rows = []
        # print "11111111111"
        for row in cursor:
            rows.append(row)
        taskitems_dic={"test_module_id":0,"path":"","class_name":"","method_name":"","test_case_id":"","test_case_name":"","group_name":"","case_seq":0,"instance_ids":"","disable_checks":""}
        taskitemlist=[]
        for row in rows:
            taskitems_dic["test_module_id"] = row[0]
            taskitems_dic["path"] = row[1]
            taskitems_dic["class_name"] = row[2]
            taskitems_dic["method_name"] = row[3]
            taskitems_dic["test_case_id"] = str(row[4])
            taskitems_dic["test_case_name"] = row[5]
            taskitems_dic["group_name"] = row[6]
            taskitems_dic["case_seq"] = row[7]
            taskitems_dic["instance_ids"] = row[8]
            taskitems_dic["disable_checks"] = row[9]
            # print "taskitems_dic=",taskitems_dic
            taskitemlist.append(taskitems_dic)
            taskitems_dic = {"test_module_id": 0, "path": "", "class_name": "", "method_name": "", "test_case_id": 0,
                             "test_case_name": "", "group_name": "", "case_seq": 0, "instance_ids": "",
                             "disable_checks": ""}
        print "====================================="
        # print taskitemlist
        # print "taskitemlist length=",len(taskitemlist)

        print "******************************************"
        print "Get old task failed case mapping list......"
        SQLCommand = "exec dbo.usp_esg_automation_get_failed_cases_from_log  " + old_taskid
        cursor.execute(SQLCommand)
        failedinstanceid_list = []
        for row in cursor:
            failedinstanceid_list.append(str(row))
        print "failedinstanceid_list=", failedinstanceid_list
        print "====================================="

        print "******************************************"
        taskitemfailed_list=[]
        for ins_id in failedinstanceid_list:
            ins_id = ins_id.replace("L,", "").strip("(").strip(")")
            for taskitem in taskitemlist:
                if ins_id in taskitem["instance_ids"]:
                    taskitemfailed_list.append(taskitem)
                    break

       
        print "====================================="

        taskitemfailed_list_removedup=[]
        for taskitem in taskitemfailed_list:
            if taskitem in taskitemfailed_list_removedup:
                continue
            else:
                taskitemfailed_list_removedup.append(taskitem)
                # if taskitem["instance_ids"].split(";"
        testcase_list=[]
        for item in taskitemfailed_list_removedup:
            if item["test_case_id"] not in testcase_list:
                testcase_list.append(item["test_case_id"])
        # print "testcase_list=",testcase_list

        n_taskitemfailed_list = []
        for case in testcase_list:
            for i, item in enumerate(taskitemfailed_list_removedup):
                if n_taskitemfailed_list == []:
                    n_taskitemfailed_list.append(item)
                elif item["test_case_id"] == case:
                    for j, item1 in enumerate(n_taskitemfailed_list):
                        # print "case----", case
                        # print "item1[test_case_id]-------", item1["test_case_id"]
                        if case == item1["test_case_id"] and item["case_seq"] < n_taskitemfailed_list[j]["case_seq"]:
                            n_taskitemfailed_list.insert(j, item)
                            break
                        if case == item1["test_case_id"] and item["case_seq"] > n_taskitemfailed_list[j]["case_seq"] and j == len(n_taskitemfailed_list) - 1:
                            n_taskitemfailed_list.append(item)
                            break
                        elif j == len(n_taskitemfailed_list) - 1:
                            n_taskitemfailed_list.append(item)
                            break

        # print "n_taskitemfailed_list=",n_taskitemfailed_list

        for taskitem in n_taskitemfailed_list:
            taskitem["test_case_id"] = str(taskitem["test_case_id"]) + "_" + str(taskitem["case_seq"])
        print "n_taskitemfailed_list=", n_taskitemfailed_list
        taskname = getTaskname(new_taskid)
        # pid = getpid(esgip)
        generateRerunxml(taskname,new_taskid,pid,n_taskitemfailed_list)
    except Exception as e:
        dbconnect.closeconnect()
        print "Execute SQL command failed. Exception -" + str(e)
    dbconnect.closeconnect()

def generateRerunxml(taskname,taskid,pid,taskitemfailed_list):
    suit=ET.Element("suite")
    tree=ET.ElementTree(suit)
    suit.set("name",taskname)
    parameter=ET.SubElement(suit,"parameter",{"name":"pid","value":pid})
    parameter = ET.SubElement(suit, "parameter", {"name":"hasPrepareReset","value":"1"})
    parameter = ET.SubElement(suit, "parameter", {"name":"taskid","value":taskid})
    parameter = ET.SubElement(suit, "parameter", {"name":"xml-file","value":"esg.xml"})
    parameter = ET.SubElement(suit, "parameter", {"name": "apitest", "value": "true"})
    parameter = ET.SubElement(suit, "parameter", {"name": "isDisableTraffic", "value": "0"})
    parameter = ET.SubElement(suit, "parameter", {"name": "myfolder", "value": "yzhu"})
    parameter = ET.SubElement(suit, "parameter", {"name": "disableChecks", "value": "false"})

    main_test= ET.SubElement(suit, "test", {"annotations":"JDK","name":"testSuite","verbose":"1"})
    main_classes= ET.SubElement(main_test,"classes")
    main_subclass1 = ET.SubElement(main_classes,"class",{"name":"com.websense.esg.qc.BaseEsgTestCase"})
    main_subclass2 = ET.SubElement(main_classes, "class", {"name":"com.websense.esg.openapi.ESGOpenAPI"})
    # seq = 1
    for taskitem in taskitemfailed_list:
        sub_test = ET.SubElement(suit, "test", {"annotations": "JDK", "name": taskitem["test_case_id"], "verbose": "1"})
        parameter = ET.SubElement(sub_test, "parameter", {"name": "sequence", "value": str(taskitem["case_seq"])})
        classes = ET.SubElement(sub_test, "classes")
        subclass = ET.SubElement(classes, "class",{"name":taskitem["class_name"] })
        methods = ET.SubElement(subclass, "methods")
        # include = ET.SubElement(methods, "include", {"name": taskitem["method_name"]})
        include  = [ET.Element('include',name=taskitem["method_name"])]
        methods.extend(include)
        # seq = seq + 1
    cwd = os.getcwd()
    base_dir = join(cwd, regression_folder)
    rerun_dir = join(base_dir, rerunxml_folder)

    file_name =taskname + ".xml"
    file = os.path.join(rerun_dir, file_name)
    tree.write(open(file,'w'))
    print "file=",file
    tree1 = ET.parse(file)
    root = tree1.getroot()
    prettyXml(root, '\t', '\n')
    tree1.write(open(file, 'w'))

def prettyXml(element, indent, newline, level = 0):
    if 'elem is not None':
        if element.text == None or element.text.isspace():
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
    temp = list(element)
    for subelement in temp:
        if temp.index(subelement) < (len(temp) - 1):
            subelement.tail = newline + indent * (level + 1)
        else:
            subelement.tail = newline + indent * level
        prettyXml(subelement, indent, newline, level = level + 1)



def getxmllist():
    try:
        xmlfilelist = []
        base_dir = join(cwd, regression_folder)
        # print "base_dir=",base_dir
        xml_dir = join(base_dir, failedxml_folder)
        print "xml_dir=", xml_dir
        xmlfilelist = [f for f in os.listdir(xml_dir) if isfile(join(xml_dir, f))]
        # print "xmlfilelist=",list
        # if len(list) > 0:
        #     xmlfile = list[0]

    except Exception as e:
        print "Get xmlfilelist. Exception -" + str(e)
        sys.exit(1)
    print "xmlfilelist=",xmlfilelist
    return xmlfilelist

def movexml_toworking(case_file_name):
    try:
        base_dir = join(cwd, regression_folder)
        working_dir = join(base_dir, failedworling_folder)
        xml_dir = join(base_dir, failedxml_folder)
        if not os.path.isdir(working_dir):
            os.mkdir(working_dir)
            # if os.path.isfile(floppy_path):
            #     os.remove(floppy_path)
        list = os.listdir(xml_dir)
        print list
        for idx, f1 in enumerate(list):
            if case_file_name in f1:
                shutil.move(join(xml_dir, f1), join(working_dir, f1))
                print "move failed xml file ",f1," to failed working folder"
                break
    except Exception as e:
        print "Move failed xml file to failed working folder. Exception -" + str(e)
        sys.exit(1)

def getold_task_id(xmlfile):
    try:
        # file = xmlfile_path + xmlfile_name
        namevalue = xmlParserFile(xmlfile).get_parameter_dic()
        old_taskid = namevalue['taskid']
        print "old_taskid=", old_taskid
    except Exception as e:
        print "Get old task id failed. Exception -" + str(e)
    return old_taskid

def getold_pid(xmlfile):
    try:
        # file = xmlfile_path + xmlfile_name
        namevalue = xmlParserFile(xmlfile).get_parameter_dic()
        old_pid = namevalue['pid']
        print "old_pid=", old_pid
    except Exception as e:
        print "Get old pid failed. Exception -" + str(e)
    return old_pid

def main():


    xmlfilelist=getxmllist()
    for xml in xmlfilelist:
        movexml_toworking(xml)

        base_dir = join(cwd, regression_folder)
        working_dir = join(base_dir, failedworling_folder)
        xmlfullpath = join(working_dir, xml)
        print "xmlfullpath=",xmlfullpath
        old_taskid=getold_task_id(xmlfullpath)
        old_pid=getold_pid(xmlfullpath)

        newtaskid=generateNewTask(old_taskid)    #13107
        if newtaskid==0:
            continue
        generateReruntask(old_taskid, newtaskid, old_pid)


if __name__ == '__main__':
    main(sys.argv)
