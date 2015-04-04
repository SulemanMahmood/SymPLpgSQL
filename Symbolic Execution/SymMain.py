from SymbolicExecutor import SymbolicExecutor
from Config import *
from ProcedureClass import ProcedureClass
import psycopg2

DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
DB = DBConn.cursor()
DB.execute("Select * from pg_proc where prolang = 11899 and proname = 'readnum2'")

    
for proc in DB.fetchall():
    Procedure = ProcedureClass(proc[0], proc[18], proc[17])
    Executor = SymbolicExecutor(Procedure)
    Executor.run()
