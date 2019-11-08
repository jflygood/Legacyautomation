#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import shutil
import sys
import getopt
from util.util import *
from Constants import *
cwd=""
class updatESGStatus():
    def __init__(self,esgip,filepath,filename):
        self.__esgip__ =  esgip
        self.__filepath__= filepath
        self.__filename__= filename
    def updateStatus(self,status):
        try:
            file_ops = FileOperations(self.__filepath__, self.__filename__, 'r')
            print "filepath=",self.__filepath__
            content = file_ops.readfile()
            listline = content.split("\n")
            find_status = self.__esgip__ + "_status"
            for index, value in enumerate(listline):
                if find_status in value:
                    listline[index] = find_status + "=" + status
            file_ops = FileOperations(self.__filepath__, self.__filename__, 'ab')
            file_ops.open_file()
            # file_ops.deleteContent()
            new_content = ""
            for index, value in enumerate(listline):
                new_content = new_content + value + "\n"
            file_ops.deleteContent()
            file_ops.write_to_files(new_content)
        except Exception as e:
            print "update status in property file failed. Exception -" + str(e)
            sys.exit(1)

    def checkstatus(self,status):
        try:
            file_ops = FileOperations(self.__filepath__, self.__filename__, 'r')
            print "filepath=", self.__filepath__
            content = file_ops.readfile()
            listline = content.split("\n")
            find_status = self.__esgip__ + "_status"
            for index, value in enumerate(listline):
                if find_status in value:
                    statusstring=value
            if statusstring.split("=")[1]==status:
                print "Status update successfully!!!"
            else:
                print "Status update failed!!"
                sys.exit(1)
        except Exception as e:
            print "Check status in property file failed. Exception -" + str(e)
            sys.exit(1)

    def updatexml(self,casefilename):
        try:
            cwd = os.getcwd()
            base_dir=join(cwd,regression_folder)
            # xml_dir=join(base_dir,xml_folder)
            file_ops = FileOperations(self.__filepath__, self.__filename__,  'r')
            content = file_ops.readfile()
            listline = content.split("\n")
            find_xml = self.__esgip__ + "_xml"
            for index, value in enumerate(listline):
                if find_xml in value:
                    # xmlfile=(join(join(cwd,working_folder),casefilename)).replace("\\","\\\\")
                    xmlfile = (join(join(base_dir, working_folder), casefilename)).replace("\\","\\\\")
                    listline[index] = find_xml + "=" + xmlfile
            file_ops = FileOperations(self.__filepath__, self.__filename__, 'ab')
            file_ops.open_file()
            # file_ops.deleteContent()
            new_content = ""
            for index, value in enumerate(listline):
                new_content = new_content + value + "\n"
            file_ops.deleteContent()
            file_ops.write_to_files(new_content)

        except Exception as e:
            print "update xml file name in property file failed. Exception -" + str(e)
            sys.exit(1)

def getxml():
    try:
        xmlfile = "none"
        base_dir = join(cwd, regression_folder)
        # print "base_dir=",base_dir
        xml_dir = join(base_dir, xml_folder)
        # print "xml_dir=", xml_dir
        list = os.listdir(xml_dir)
        if len(list) > 0:
            xmlfile = list[0]
    except Exception as e:
        print "Get xmlfile. Exception -" + str(e)
        sys.exit(1)
    return xmlfile

class processxml:
    def __init__(self):
        pass

    def movexml_toworking(self,case_file_name):
        try:
            base_dir = join(cwd, regression_folder)
            working_dir = join(base_dir, working_folder)
            xml_dir = join(base_dir, xml_folder)
            if not os.path.isdir(working_dir):
                os.mkdir(working_dir)
            # if os.path.isfile(floppy_path):
            #     os.remove(floppy_path)
            list = os.listdir(xml_dir)
            print list
            for idx, f1 in enumerate(list):
                if case_file_name in f1:
                    shutil.move(join(xml_dir, f1), join(working_dir, f1))
                    break
        except Exception as e:
            print "Move xml file to working folder. Exception -" + str(e)
            sys.exit(1)
    def moveworking_todone(self,case_filename_fullpath):
        try:
            base_dir = join(cwd, regression_folder)
            done_dir = join(base_dir, done_folder)
            working_dir = join(base_dir, working_folder)
            if not os.path.isdir(done_dir):
                os.mkdir(done_dir)
            list = os.listdir(working_dir)
            # print "list=",list
            head, tail = os.path.split(case_filename_fullpath)
            # case_filename = tail
            # print "case_filename111=", tail
            for idx, f1 in enumerate(list):
                if tail == f1:
                    print "f1=", f1
                    shutil.move(join(working_dir, f1), join(done_dir, f1))
                    break
        except Exception as e:
            print "Move xml file from working folder to done folder. Exception -" + str(e)
            sys.exit(1)

def Usage():
    print 'Update send domain in base_mta.conf Usage is as folllowing:\n'
    print '-h,--help: print help message.\n'
    print '-e --esgip: interface E ip\n'
    print '-p --statusFpath:esgstatus.properties file path. In jenkins server, it is under directory /share/root/legacyautomation \n'
    print '-s --status: ESG satus:none|ready|fail\n'
    # print '--case_xml_name: case xml file name. This is put in current directory\\regression\\xml \n'
    print '-c --casepath: case xml file name full path. E:\\robot_bq\\LegacyAutomation\\working\\testpolicy2.xml \n'
    print '--setstatus: Update esg status in esgstatus.properties\n'
    print '--setcasefile: Update esg case file in esgstatus.properties\n'
    print '-a --processxml: one value done.if processxml=done,will move xml file from working folder to done folder\n'

    #print '---------exemple-------------------\n'
    print "python updateStatus.py  --esgip 10.226.38.7 --statusFpath  X:\\legacyautomation  --status ready --setstatus\n"
    print "python updateStatus.py--esgip 10.226.38.7  -statusFpath  X:\\legacyautomation --setcasefile \n"
    # print "python updateStatus.py --processxml work --case_xml_name testpolicy1.xml "
    print "python updateStatus.py --processxml done --casepath E:\\robot_bq\\LegacyAutomation\\working\\testpolicy2.xml \n"

def main(argv):
    global cwd
    esgip = ""
    status_file_path=""
    esg_status=""
    case_xmlname_fullpath=""
    setstatus=False
    checkstatus=False
    processxmlaction=""
    setcasefile=False

    print "----argv----",argv
    if len(argv)<3:
        Usage()
        sys.exit(2)
    try:
        options, args = getopt.getopt(argv[1:], 'e:p:s:c:a:h',["esgip=","statusFpath=","status=","casepath=","processxml=","setstatus","checkstatus","setcasefile","help"])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    for opt, arg in options:
        if opt in ('-h', '--help'):
            Usage()
            sys.exit(0)
        elif opt in ('-e','--esgip'):
            esgip = arg
        elif opt in ('-p','--statusFpath'):
            status_file_path = arg
        elif opt in ('-s','--status'):
            esg_status = arg
        elif opt in ('-c','--casepath'):
            case_xmlname_fullpath = arg
        elif opt in ('-a','--processxml'):
            processxmlaction = arg
        elif opt in ( '--setstatus'):
            setstatus = True
        elif opt in ( '--checkstatus'):
            checkstatus = True
        elif opt in ( '--setcasefile'):
            setcasefile = True

        else:
            print 'unhandled option'
            Usage()
            sys.exit(2)
        cwd = os.getcwd()
        if setstatus:
            updateESGstatus = updatESGStatus(esgip,status_file_path,status_file_name)
            updateESGstatus.updateStatus(esg_status)
        if checkstatus:
            updateESGstatus = updatESGStatus(esgip, status_file_path, status_file_name)
            updateESGstatus.checkstatus(esg_status)
        if setcasefile:
            case_file_name=getxml()
            print "case_file_name=",case_file_name
            processxml_obj = processxml()
            processxml_obj.movexml_toworking(case_file_name)
            updateESGstatus = updatESGStatus(esgip,status_file_path, status_file_name)
            updateESGstatus.updatexml(case_file_name)
        if processxmlaction=="done":
            processxml_obj=processxml()
            processxml_obj.moveworking_todone(case_xmlname_fullpath)

if __name__ == '__main__':
    main(sys.argv)
