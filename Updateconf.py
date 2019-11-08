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
            child.expect('assword:')
            child.sendline(password)
        except Exception as error:
            print 'ssh log in Caught the error:',error
            sys.exit(1)
        return child

    def setSenderDomain(self,host, user, password,setAzure):
        try:
            # print "setAzure=",setAzure
            child = self.ssh_login(host, user, password)
            # child.sendline("ssh esg")
            # cmdm = 'sed  -i  s/LatestVaBuild=.*/LatestVaBuild=%s/g %s' % (f1, PropertyFilePath)
            child.readline()
            child.readline()
            cmd=""
            if setAzure.lower()=="true":
                cmd = "lxc-attach -n esg -- sed  -i  's/smtpd_sender_domain_validation =.*/smtpd_sender_domain_validation =0/g' /etc/postfix/base_mta.conf;echo $?"
            else:
                cmd = "sed  -i  's/smtpd_sender_domain_validation =.*/smtpd_sender_domain_validation =0/g' /etc/postfix/base_mta.conf;echo $?"
            print "cmd=",cmd
            child.sendline(cmd)
            child.readline()
            a = child.readline()
            if a.strip() == "0":
                retvalue = "Modify file /etc/postfix/base_mta.conf successfully"
                print "retvalue=", retvalue
            else:
                retvalue = "Modify file /etc/postfix/base_mta.conf failed"
                print "retvalue=", retvalue
                sys.exit(1)
            if setAzure.lower()=="true":
                child.sendline("lxc-attach -n esg -- esg_stop.sh;")
                ret = child.expect(['Email protection service has stopped', pexpect.TIMEOUT, pexpect.EOF])
                if ret == 0:
                    print "Stop esg Successfully!"
                elif ret == 1:
                    print "Stop esg timeout"
                    sys.exit(1)
                elif ret == 2:
                    print "Stop esg error"
                    sys.exit(1)
                child.sendline("lxc-attach -n esg -- esg_boot.sh;")
                ret = child.expect(['Email protection service is started', pexpect.TIMEOUT, pexpect.EOF])
                if ret == 0:
                    print "Start esg Successfully!"
                elif ret == 1:
                    print "Start esg timeout"
                    sys.exit(1)
                elif ret == 2:
                    print "Start esg error"
                    sys.exit(1)
            else:
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
            print "Set senderdomain failed. Exception -" + str(e)
            sys.exit(1)


def Usage():
    print 'Update send domain in base_mta.conf Usage is as folllowing:\n'
    print '-h,--help: print help message.\n'
    print '-p, --eip: interface E ip\n'
    print '-s,--setmta: Set senderdomain in base_mta file\n'


    #print '---------exemple-------------------\n'
    print "python Updateconf.py -p 10.226.38.4 --setmta"

def main(argv):
    global cwd
    eip = ""
    setmta=False
    setAzure="False"

    #print "----argv----",argv
    if len(argv)<3:
        Usage()
        sys.exit(2)
    try:
        options, args = getopt.getopt(argv[1:], 'h:p:sa',["eip=","setmta","setazure","help"])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    for opt, arg in options:
        # print "====opt===",opt
        if opt in ('-h', '--help'):
            Usage()
            sys.exit(0)
        elif opt in ('-p', '--eip'):
            eip = arg
        elif opt in ('-s', '--setmta'):
            setmta = True
        elif opt in ('-a', '--setazure'):
            setAzure = "True"
        else:
            print 'unhandled option'
            Usage()
            sys.exit(2)
        if setmta:
            setinfo_obj = setinfo()
            setinform = setinfo_obj.setSenderDomain(eip, "root", "password",setAzure)

if __name__ == '__main__':
    main(sys.argv)
