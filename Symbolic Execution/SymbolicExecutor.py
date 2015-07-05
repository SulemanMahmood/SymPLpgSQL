from Z3Solver import Z3Solver
from StateClass import StateClass
import psycopg2
from TestCaseParser import TestCaseParser
from Config import *
from DataHandlerClass import DataHandlerClass

class SymbolicExecutor:
    
    def __init__(self, Procedure):
        self.Procedure = Procedure
        
    
    def run(self):
        self.DataHandler = DataHandlerClass()
        self.CaseParser = TestCaseParser(self.Procedure, self.DataHandler)
        State = StateClass(self.Procedure, self.DataHandler)
        self.Z3 = Z3Solver(State, self.CaseParser)
        Data, Test = self.Z3.get_first_test_case()
        
        while True:
            self.ExecuteTest(Data)
            self.ExecuteTest(Test)
            Data, Test = self.Z3.Check()
            if Test == None:
                break;
            
    def CleanUp(self):      #Cleaning Up the Trace File
        T = open(Orignal_TraceFile,'w')
        T.close
        
    def ExecuteTest(self, T):       
        DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
        DB = DBConn.cursor()
        PrintLog(T)
        try:
            self.CleanUp()
            DB.execute(open(T,'r').read())
            self.SetupLog()
            Log = "Delete from Test_Case_Exception_Log where proname = '" + self.Procedure.getName() +"' and CaseFileName = '"+T+"' "
            DB.execute(Log)
            DB.execute("commit") 
        except Exception as SqlException:
            self.SetupLog()
            DB.execute('rollback');
            if SqlException.pgcode == '42883':
                raise Exception ('Function does not exist')
            Error = (SqlException.args).__str__()
            Error = Error[2:-3]
            Error = Error.replace('\'','-')
            Log = "Insert into Test_Case_Exception_Log (proname, CaseFileName, Error) values ('" + self.Procedure.getName() +"', '"+T+"', '" +Error+ "')"
            PrintLog (Log)
            DB.execute("rollback")
            try:
                DB.execute(Log)
            except Exception as e:
                PrintLog("failed:  " + (e.args).__str__())
                Log = "Update Test_Case_Exception_Log  set Error = '" +Error+ "' where proname = '" + self.Procedure.getName() +"' and CaseFileName = '"+T+"' "
                DB.execute(Log)
            finally:
                DB.execute("commit")
        DB.close
        DBConn.close
    
    def SetupLog(self):
        TO = open(Orignal_TraceFile,'r')
        T = open(TraceFile,'w')
        T.write(TO.read())
        TO.close
        T.close
        
    def getZ3CheckCount(self):
        return self.Z3.getCheckCount()
