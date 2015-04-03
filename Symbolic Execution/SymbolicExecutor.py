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
            Data, Test = Z3.Check()
            if Test == None:
                break;
            
        
    def CleanUp(self):      #Cleaning Up the Trace File
        T = open(TraceFile,'w')
        T.close
        self.CaseParser.ClearExceptionLog()
        
    def ExecuteTest(self, T):       
        DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
        DB = DBConn.cursor()
        print(T)
        try:
            DB.execute(open(T,'r').read())
        except:
            self.CaseParser.LogExceptionforCase() 
        DB.close
        DBConn.close
    
