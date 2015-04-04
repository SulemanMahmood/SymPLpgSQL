from SymbolicExecutor import SymbolicExecutor
from Config import *
from ProcedureClass import ProcedureClass
import psycopg2

DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
DB = DBConn.cursor()
DB.execute("Select proname, proargtypes, prorettype from pg_proc where prolang = 11899")

    
for proc in DB.fetchall():
    Procedure = ProcedureClass(proc[0], proc[1], proc[2])
    Executor = SymbolicExecutor(Procedure)
    Executor.run()
