dbname ='Postbook' 
database='test'
user='suleman'
password='123'
host='localhost'
port='5432'
TestCasePath = '/home/suleman/Desktop/TestCases/'

Orignal_TraceFile = '/home/suleman/TraceLog.txt'
TraceFile = '/home/suleman/TraceLog1.txt'
MaximumStackDepth = 5
CombinationsLimit = 3

Log = True
ExecutionMode = 'Update'   ## Update / Full
LogLevel = 'Progress'           # Fine / Progress
LogLocation = 'Console'        ## File / Console


def Print(log):
    if LogLocation == 'Console':
        print(log)
    elif LogLocation == 'File':
        T = open("/home/suleman/Desktop/savelog.txt", 'a')
        try:
            T.write(log.__str__() + '\n')
        except:
            pass
        finally:
            T.flush()
            T.close()
    
def PrintLog(log, level = 'Fine'):
    if Log == True:
        if LogLevel == 'Fine':
            Print(log)
        elif LogLevel == 'Progress':
            if level == 'Progress':  # or level == '' other log levels may be added later
                print(log)
                