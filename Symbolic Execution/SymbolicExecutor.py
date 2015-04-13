from Z3Solver import Z3Solver
from StateClass import StateClass
import psycopg2
from TestCaseParser import TestCaseParser
from Config import *

class SymbolicExecutor:
    
    def __init__(self, Procedure):
        self.Procedure = Procedure
        
    
    def run(self):
        self.CaseParser = TestCaseParser(self.Procedure)
        State = StateClass(self.Procedure)
        Z3 = Z3Solver(State, self.CaseParser)
        Data, Test = Z3.get_first_test_case()
        
        while True:
            self.ExecuteTest(Data)
            self.CleanUp()
            self.ExecuteTest(Test)
            self.SetupLog()
            Data, Test = Z3.Check()
            if Test == None:
                break;
            
    def CleanUp(self):      #Cleaning Up the Trace File
        T = open(Orignal_TraceFile,'w')
        T.close
        
    def ExecuteTest(self, T):       
        DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
        DB = DBConn.cursor()
        #print(T)
        try:
            DB.execute(open(T,'r').read())
        except Exception as SqlException:
            Error = (SqlException.args).__str__()
            Error = Error[2:-3]
            Error = Error.replace('\'','-')
            Log = "Insert into Test_Case_Exception_Log (proname, CaseFileName, Error) values ('" + self.Procedure.getName() +"', '"+T+"', '" +Error+ "')"
            print Log
            try:
                DB.execute("rollback")
                DB.execute(Log)
                DB.execute("commit")
            except Exception as e:
                print("failed:  " + (e.args).__str__())
        DB.close
        DBConn.close
    
    def SetupLog(self):
        TO = open(Orignal_TraceFile,'r')
        T = open(TraceFile,'w')
        T.write(TO.read())
        TO.close
        T.close
        
