#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import os

import pexpect
import re
import sys
import time
import getopt


class setinfo():
    def __init__(self):
        pass
    def delete_known_host_entry(self,hostip):
        filename = '%s/.ssh/known_hosts' % os.path.expanduser("~")
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

            with open(filename, 'w') as newf:
                for line in lines:
                    if not re.match(hostip, line):
                        newf.write(line)
        except:
            pass


    def ssh_login(self,hostip,username,password):
        self.delete_known_host_entry(hostip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -l %s %s' % (username, hostip), timeout=120)
            child.logfile_read = sys.stdout
            child.delaybeforesend = 1
            child.expect('password:')
            child.sendline(password)
        except Exception as error:
            print 'ssh log in Caught the error:',error
            sys.exit(1)
        return child

    def restartesg(self,host, user, password):
        try:
            child = self.ssh_login(host, user, password)
            # child.sendline("ssh esg")
            # cmdm = 'sed  -i  s/LatestVaBuild=.*/LatestVaBuild=%s/g %s' % (f1, PropertyFilePath)

            child.sendline("esg_restart.sh;")
            ret = child.expect(['esg', pexpect.TIMEOUT, pexpect.EOF])
            if ret == 0:
                print "Restart esg Successfully!"
            elif ret == 1:
                print "Restart esg timeout"
                sys.exit(1)
            elif ret == 2:
                print "Restart esg error"
                sys.exit(1)
            child.sendline("exit")
            child.expect('closed')
            child.close(force=True)
        except Exception as e:
            print "esg restart failed. Exception -" + str(e)
            sys.exit(1)


def Usage():
    print 'Restart esg.  Usage is as folllowing:\n'
    print '-h,--help: print help message.\n'
    print '-p, --eip: interface E ip\n'
    print '-s,--restart: restart esg \n'


    #print '---------exemple-------------------\n'
    print "python esgoperation.py -p 10.226.38.4 --restart"

def main(argv):
    global cwd
    eip = ""
    restart=False

    #print "----argv----",argv
    if len(argv)<3:
        Usage()
        sys.exit(2)
    try:
        options, args = getopt.getopt(argv[1:], 'h:p:s',["eip=","restart","help"])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    for opt, arg in options:
        if opt in ('-h', '--help'):
            Usage()
            sys.exit(0)
        elif opt in ('-p', '--eip'):
            eip = arg
        elif opt in ('-s', '--restart'):
            restart = True
        else:
            print 'unhandled option'
            Usage()
            sys.exit(2)
        if restart:
            setinfo_obj = setinfo()
            setinform = setinfo_obj.restartesg(eip, "root", "password")

if __name__ == '__main__':
    main(sys.argv)
