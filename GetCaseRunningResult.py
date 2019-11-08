import getopt
import os
import sys
import time
from DBconnection.dbconnection import dbconnection
from util.util import *
from Constants import *
import logging
import xlsxwriter

def Usage():
    print 'Generate new task Usage is as folllowing:\n'
    print '-h,--help: print help message.\n'
    print '-i --xmlfile : xmlfile \n'
    print '---------exemple-------------------\n'

    print 'python Task_ID.py --taskid 11608  \n'

def main(argv):
    LOG_FILE = 'getcaseResult.log'
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p', filename=LOG_FILE,level=logging.DEBUG)
    xmlfile = ""
    #print "----argv----",argv
    if len(argv)<3:
        Usage()
        sys.exit(2)
    try:
        options, args = getopt.getopt(argv[1:], 'i:h', ["xmlfile=", "--help"])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    for opt, arg in options:
        if opt in ('-h', '--help'):
            Usage()
            sys.exit(0)
        elif opt in ('-i', '--xmlfile'):
            xmlfile = arg
        else:
            print 'unhandled option'
            Usage()
            sys.exit(2)
    logging.debug('Get case result list......')
    print "Get case result list......"
    taskid=get_task_id(xmlfile)
    taskname=get_task_name(taskid)
    caseresultlist=getCaseresultlist(taskid)
    logging.debug('Get case result list Done......')
    print "Get case result list Done......"
    logging.debug('Begin to generate excel report......')
    print "Begin to generate excel report......"
    excelname=taskid+"_"+taskname
    writeToexcel(caseresultlist,excelname);
    logging.debug('Write to excel done......')
    print "Write to excel done......"

def get_task_id(xmlfile):
    try:
        # file = xmlfile_path + xmlfile_name
        namevalue = xmlParserFile(xmlfile).get_parameter_dic()
        taskid = namevalue['taskid']
        print "taskid=", taskid
    except Exception as e:
        print "Get  task id failed. Exception -" + str(e)
    return taskid

def get_task_name(taskid):
    taskname="test"
    try:
        dbconnect = dbconnection();
        connection = dbconnect.connect();
        cursor = connection.cursor()
        print "Get task name......"
        SQLCommand = " select top 1 task_name FROM [esgautomationdb].[dbo].[esg_test_task]  where test_task_id=" + taskid + " order by test_task_id desc "
        cursor.execute(SQLCommand)
        taskname = cursor.fetchone()[0]
        print "taskname=" + taskname
    except Exception as e:
        dbconnect.closeconnect()
        print "Execute SQL command failed. Exception -" + str(e)
        return taskname
    dbconnect.closeconnect()
    return taskname

def getCaseresultlist(taskid):
    logging.debug('Connect with db......')
    dic_case_result = {}
    list_dic_case_result = []
    dbconnect = dbconnection();
    connection = dbconnect.connect();
    try:
        cursor = connection.cursor()
        print "Get task result list......"
        SQLCommand = "with log_automation_temp([id],[test_task_id],[test_case_id],[test_instance_id],[info_level] ,[result_content],[test_status])" \
                     "as" \
                     "(select [id],[test_task_id],[test_case_id],[test_instance_id],[info_level] ,[result_content],[test_status] " \
                     "from [esgautomationdb].[dbo].[log_automation] where test_task_id=" + taskid + " and info_level='case' and test_status in ('skip','pass','fail')) " \
                                                                                                    "select  b.test_case_id ,test_case_name,test_task_id,test_instance_id ,info_level,result_content,test_status " \
                                                                                                    "from [esgautomationdb].[dbo].[esg_test_case] as a right join log_automation_temp as b on a.test_case_id = b.test_case_id  order by id "
        logging.debug('Begin to search from DB......')
        cursor.execute(SQLCommand)
        rows = []
        for row in cursor:
            # print "row=", row
            rows.append(row)
        # print "rows=", rows
        for row in rows:
            dic_case_result = {}
            dic_case_result[cons_test_case_id] = str(row[0])
            dic_case_result[cons_test_case_name] = str(row[1])
            dic_case_result[cons_test_task_id] = str(row[2])
            dic_case_result[cons_test_instance_id] = str(row[3])
            dic_case_result[cons_info_level] = str(row[4])
            dic_case_result[cons_result_content] = str(row[5])
            dic_case_result[cons_test_status] = str(row[6])
            if dic_case_result[cons_result_content] != "":
                dic_case_result[cons_test_instance_name] = (dic_case_result[cons_result_content].split(",")[1]).split(":")[1]
            else:
                dic_case_result[cons_test_instance_name] = ""
            # print '3333333----------',dic_case_result
            list_dic_case_result.append(dic_case_result)
    except Exception as e:
        dbconnect.closeconnect()
        print "Execute SQL command failed. Exception -" + str(e)
    dbconnect.closeconnect()
    # print list_dic_case_result
    return list_dic_case_result

def writeToexcel(caseresultlist,excelname):
    try:
        cwd = os.getcwd()
        filepath = os.path.join(cwd, taskresult_folder)
        file_name = excelname + ".xlsx"
        file = os.path.join(filepath, file_name)
        workbook = xlsxwriter.Workbook(file)
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, 0, 13)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 13)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 60)
        worksheet.set_column(5, 5, 10)
        format_head = workbook.add_format({'bold': True})
        format_head.set_align('center')
        format_head.set_valign("vcenter")
        format_head.set_text_wrap()
        format_head.set_border()

        format_body = workbook.add_format({'bold': False})
        format_body.set_align('center')
        format_body.set_valign("vcenter")
        format_body.set_text_wrap()
        format_body.set_border()

        format_pass = workbook.add_format({'bold': False})
        format_pass.set_align('center')
        format_pass.set_valign("vcenter")
        format_pass.set_text_wrap()
        format_pass.set_border()
        format_pass.set_bg_color('green')

        format_fail = workbook.add_format({'bold': False})
        format_fail.set_align('center')
        format_fail.set_valign("vcenter")
        format_fail.set_text_wrap()
        format_fail.set_border()
        format_fail.set_bg_color('red')

        worksheet.write(0, 0, cons_test_case_id, format_head)
        worksheet.write(0, 1, cons_test_case_name, format_head)
        worksheet.write(0, 2, cons_test_task_id, format_head)
        worksheet.write(0, 3, cons_test_instance_id, format_head)
        worksheet.write(0, 4, cons_test_instance_name, format_head)
        worksheet.write(0, 5, cons_test_status, format_head)
        row = 1;
        col = 0;
        for item in caseresultlist:
            worksheet.write(row, 0, item[cons_test_case_id], format_body)
            worksheet.write(row, 1, item[cons_test_case_name], format_body)
            worksheet.write(row, 2, item[cons_test_task_id], format_body)
            worksheet.write(row, 3, item[cons_test_instance_id], format_body)
            worksheet.write(row, 4, item[cons_test_instance_name], format_body)
            if item[cons_test_status] == 'pass':
                worksheet.write(row, 5, item[cons_test_status], format_pass)
            else:
                worksheet.write(row, 5, item[cons_test_status], format_fail)
            row += 1
            # print "item=======",item
        workbook.close()
    except Exception as e:
      print "Generate excel report failed. Exception -" + str(e)

if __name__ == '__main__':
    main(sys.argv)