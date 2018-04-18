#!/usr/bin/python

import os
import sys
import time
import sqlite3
import subprocess

if len(sys.argv) != 4:
    print("usage:  python3 automake.py [dbname] [new/continue] [all/总线/数据库/前置/SCADA/新产品]")
    sys.exit()
try:
    conn = sqlite3.connect(sys.argv[1])
except:
    print ("conn fail ,please check ",sys.argv[2]," if created")
    sys.exit()
else:
    print ("connect database success!")
c = conn.cursor()
if sys.argv[3] == "all":
    if sys.argv[2] == "new":
        all_row = c.execute("SELECT makeorder,app_name,proc_name,proc_dir,make_status,make_clean,make,make_install,check_dir,depart from auto_make order by makeorder;")
    elif sys.argv[2] == "continue":
        all_row = c.execute("SELECT makeorder,app_name,proc_name,proc_dir,make_status,make_clean,make,make_install,check_di,departr from auto_make where make_status = 0 order by makeorder;")
    else:
        print (10*"*","fail ,input '",sys.argv[2],"' undefine")
        conn.close()
        sys.exit()
elif sys.argv[3] in ("总线","数据库","前置","SCADA","新产品"):
    if sys.argv[2] == "new":
        all_row = c.execute("SELECT makeorder,app_name,proc_name,proc_dir,make_status,make_clean,make,make_install,check_dir,depart from auto_make where depart='"+str(sys.argv[3])+"' order by makeorder;")
    elif sys.argv[2] == "continue":
        all_row = c.execute("SELECT makeorder,app_name,proc_name,proc_dir,make_status,make_clean,make,make_install,check_dir,depart from auto_make where make_status = 0 and depart='"+str(sys.argv[3])+"' order by makeorder;")
    else:
        print (10*"*","fail ,input '",sys.argv[2],"' undefine")
        conn.close()
        sys.exit()
else:
    print (10*"*","fail ,input '",sys.argv[3],"' undefine")
    conn.close()
    sys.exit()

for row in all_row.fetchall():
    print (100*"*")
    print (10*"*","making order = ", row[0])
    print (10*"*","Department = ", row[9])
    print (10*"*","making app_name = ", row[1])
    print (10*"*","making proc_name = ", row[2])
    print (10*"*","making proc_dir = ", row[3])
    #print (10*"*","making status = ", row[4])
    cd_str='cd '
    add_str=';'
    print (10*"*","clean command = ", cd_str+row[3]+add_str+row[5])
    status, output = subprocess.getstatusoutput(cd_str+row[3]+add_str+row[5])
    #if status != 0:
        #print (output)
        #conn.close()
        #sys.exit()
    print (10*"*","make command = ", cd_str+row[3]+add_str+row[6])
    status,output = subprocess.getstatusoutput(cd_str+row[3]+add_str+row[6])
    if status != 0:
        print (output)
        conn.close()
        sys.exit()
    print (10*"*","make_install = ", cd_str+row[3]+add_str+row[7])
    status,output = subprocess.getstatusoutput(cd_str+row[3]+add_str+row[7])
    #if status != 0:
        #print (output)
        #conn.close()
        #sys.exit()
    print (10*"*","check dir = ", row[8])
    add_str='/'
    make_success=0
    proc_name_list=row[2].split(",")
    for proc_name in proc_name_list:
        file_str= os.path.expandvars(row[8])+add_str+proc_name
        create_time = os.stat(file_str).st_ctime
        check_time = time.time()-3600
        if create_time > check_time:
            make_success = make_success + 1
        else:
            print (10*"*","can`t find file in ",file_str,"please check !!!")
            conn.close()
            sys.exit(0)
    if make_success == len(proc_name_list):
        update_sql="update auto_make set make_status = 1 where proc_name ='"+str(row[2])+"' and makeorder ="+str(row[0])+";"
        #print (10*"*" ,"update sql = ",update_sql)
        cursor = c.execute(update_sql)
        conn.commit()
        print (10*"*","file make success ")
    else:
        print (100*"*","can`t find file in ",file_str,"please check !!!")
else:
    print("nothing to be make")
if make_success > 0:
    print(100*"*")
    print(100*"*")
    print(20*"*",20*" ","MAKE SUCCEED!!!!",20*" ",20*"*")
    print(100*"*")
    print(100*"*")

if sys.argv[3] == "all":
    cursor = c.execute("update auto_make set make_status = 0;")
    conn.commit()
    conn.close()
else:
    cursor = c.execute("update auto_make set make_status = 0 where depart = '"+str(sys.argv[3])+"';")
    conn.commit()
    conn.close()
