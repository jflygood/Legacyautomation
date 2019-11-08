#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import shutil
import sys
import getopt
from util.util import *
from Constants import *
import time
cwd=""



def move_toNewfolder(originaldir,filename,foldername):
    try:
        # base_dir = join(cwd, regression_folder)
        # working_dir = join(base_dir, working_folder)
        new_dir=join(originaldir, foldername)
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        list = os.listdir(originaldir)
        # print list
        for idx, f1 in enumerate(list):
            if filename in f1:
                shutil.move(join(originaldir, f1), join(new_dir, f1))
                # print "move working folder file ",f1," to new folder",new_dir
                break
    except Exception as e:
        print "move working folder file ", f1, " to new folder", new_dir, "Exception -" + str(e)
        sys.exit(1)

def main():
    cwd = os.getcwd()
    base_dir = join(cwd, regression_folder)

    print "====================Move /regression/working files to one new folder to backup"
    working_dir = join(base_dir, working_folder)
    workingxmlfile_l = [f for f in os.listdir(working_dir) if isfile(join(working_dir, f))]
    new_foldername=time.strftime("%y%m%d%H%M%S")
    # if not os.path.isdir(foldername):
    #     os.mkdir(foldername)
    for xml in workingxmlfile_l:
        move_toNewfolder(working_dir,xml,new_foldername)

    print "====================Delete all the xml files in /regression/xml folder"
    xml_dir=join(base_dir, xml_folder)
    xmlfile_list = [f for f in os.listdir(xml_dir) if isfile(join(xml_dir, f))]
    for xml in xmlfile_list:
        # print "xml=",xml
        os.remove(join(xml_dir,xml))

    print "===================Copy files from /regression/bak folder to /regression/xml"
    bak_dir = join(join(base_dir, "bak"),"8_5")
    file_list = [f for f in os.listdir(bak_dir) if isfile(join(bak_dir, f))]
    for xml in file_list:
        # print "xml=",xml
        shutil.copy(join(bak_dir,xml),xml_dir)
    print "====================Move taskResult files to one new folder to backup"
    taskresult_dir=join(cwd, taskresult_folder)
    taskresult_f = [f for f in os.listdir(taskresult_dir) if isfile(join(taskresult_dir, f))]
    new_foldername = time.strftime("%y%m%d%H%M%S")
    new_dir = join(taskresult_dir, new_foldername)
    for file in taskresult_f:
        move_toNewfolder(taskresult_dir,file, new_foldername)

if __name__ == '__main__':
    main(sys.argv)


