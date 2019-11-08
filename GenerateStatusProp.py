#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import shutil
import sys
import getopt
from util.util import *
from Constants import *
cwd=""

def Generatestatusconf(esglist,ifAzure,version,filepath):
    try:
        content=""
        content = content + "INSTALL_VERSION="+version  + os.linesep
        content = content + "Azurestatus=" + ifAzure + os.linesep
        for esg in esglist:
            content  = content + os.linesep
            content = content  + esg+"_status=none"+ os.linesep
            content = content  + esg+"_xml=W:\\\\LegacyAutomation\\\\regression\\\\working\\\\none"+ os.linesep

        file_ops = FileOperations(filepath, status_file_name, 'ab')
        file_ops.open_file()
        file_ops.deleteContent()
        file_ops.write_to_files(content)
    except Exception as e:
        print "update status in property file failed. Exception -" + str(e)
        sys.exit(1)

# Generatestatusconf(["172.16.1.4","172.16.1.5"],"True","8_5_0","E:\\tmp")
def Usage():
    print 'Update esgstatus.properties :\n'
    print '-h,--help: print help message.\n'
    print '-e --esgip: esgips, format is esgip1,esgip2,esgip3......\n'
    print '-i --ifAzure:if test Azure. True | False \n'
    print '-v --version: 8_4_0  |8_5_0 |8_6_0\n'

    print '-p --filepath: esgstatus.properties full path. Z:\\legacyautomation     \n'


    #print '---------exemple-------------------\n'
    print "python GenerateStatusProp.py  --esgip 10.226.38.7,10.226.38.10,10.226.38.13 --ifAzure False --version 8_5_0 --filepath Z:\\legacyautomation  \n"

def main(argv):
    global cwd
    esglist=[]
    ifAzure="False"
    version=""
    filepath=""

    print "----argv----",argv
    if len(argv)<3:
        Usage()
        sys.exit(2)
    try:
        options, args = getopt.getopt(argv[1:], 'e:i:v:p:h',["esgip=","ifAzure=","status=","version=","filepath=","help"])
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
        elif opt in ('-i','--ifAzure'):
            ifAzure = arg
        elif opt in ('-v','--version'):
            version = arg
        elif opt in ('-f','--filepath'):
            filepath = arg
        else:
            print 'unhandled option'
            Usage()
            sys.exit(2)

    if esgip.__contains__(","):
        esglist = esgip.split(",")
    else:
        esglist.append(esgip)
    Generatestatusconf(esglist,ifAzure,version,filepath)

if __name__ == '__main__':
    main(sys.argv)
