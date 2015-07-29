dbname ='Postgres' 
database='test'
user='suleman'
password='123'
host='localhost'
port='5432'

Orignal_TraceFile = '/home/suleman/TraceLog.txt'
TraceFile = '/home/suleman/TraceLog1.txt'
MaximumStackDepth = 15

Log = False

def PrintLog(log):
    if Log == True:
        print(log)
#         T = open("Joinlog.txt", 'a')
#         try:
#             T.write(log.__str__() + '\n')
#         except:
#             pass
#         finally:
#             T.flush()
#             T.close()
