dbname ='CourseRegister' 
database='test'
user='suleman'
password='123'
host='localhost'
port='5432'
TestCasePath = '/home/suleman/Desktop/TestCases/'

Orignal_TraceFile = '/home/suleman/TraceLog.txt'
TraceFile = '/home/suleman/TraceLog1.txt'
MaximumStackDepth = 5

Log = True
LogLevel = 'Fine'

def PrintLog(log, level = 'Fine'):
    if Log == True:
        if LogLevel == 'Fine':
            print(log)
        elif LogLevel == 'Progress':
            if level == 'Progress':  # or level == '' other log levels may be added later
                print(log)
#         T = open("Joinlog.txt", 'a')
#         try:
#             T.write(log.__str__() + '\n')
#         except:
#             pass
#         finally:
#             T.flush()
#             T.close()
