dbname ='Postbook' 
database='test'
user='suleman'
password='123'
host='localhost'
port='5432'

Orignal_TraceFile = '/home/suleman/TraceLog.txt'
TraceFile = '/home/suleman/TraceLog1.txt'

Log = False

def PrintLog(log):
    if Log == True:
        print(log)