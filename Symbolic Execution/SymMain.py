from SymbolicExecutor import SymbolicExecutor
from Config import *
import psycopg2

proc_name = 'InsertTest'

DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
DB = DBConn.cursor()
try:
    DB.execute('Select * from pg_proc where prolang = 11899')
except:
    print('procedure list fetch failed')
    
for proc in DB.fetchall():
    proc_name = proc[0] 
    Executor = SymbolicExecutor(proc_name)
    Executor.run()
