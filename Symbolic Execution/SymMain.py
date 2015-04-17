from SymbolicExecutor import SymbolicExecutor
from Config import *
from ProcedureClass import ProcedureClass
import psycopg2

DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
DB = DBConn.cursor()
DB.execute("Truncate Table Exception_Log")
DB.execute("Truncate Table Test_Case_Exception_Log")
DB.execute("commit")
DB.execute("Select proname, proargtypes, prorettype from pg_proc p where p.oid not in (select t.tgfoid from pg_trigger t) and prolang = 11899;")

    
for proc in DB.fetchall():
    Procedure = ProcedureClass(proc[0], proc[1], proc[2])
    try:
        Executor = SymbolicExecutor(Procedure)
        Executor.run()
        DB.execute("Insert into Exception_Log (proname, status) values ('" + Procedure.getName() +"', 'Completed')")
        DB.execute("commit")
    except Exception as e:
        Error = (e.args).__str__()
        Error = Error[2:-3]
        Error = Error.replace('\'','-')
        insertexpr = "Insert into Exception_Log (proname, status) values ('" + Procedure.getName() +"', '"+ Error +"')"
        print(insertexpr)
        DB.execute(insertexpr)
        DB.execute("commit")