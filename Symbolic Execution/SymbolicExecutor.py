from Z3Solver import Z3Solver
from StateClass import StateClass
import psycopg2
from TestCaseParser import TestCaseParser

class SymbolicExecutor:
    
    def __init__(self, proc_name, TraceFile):
        self.TraceFile = TraceFile
        self.proc_name = proc_name
        
    
    def run(self):
        State = StateClass(self.proc_name)
        CaseParser = TestCaseParser(self.proc_name)
        Z3 = Z3Solver(State, CaseParser)
        T = Z3.get_first_test_case()
        
        while True:
            self.CleanUp()
            self.ExecuteTest(T)
            T = Z3.Check(self.TraceFile)
            if not isinstance(T, int):
                pass
            else:
                break
        
    def CleanUp(self):      #Cleaning Up the Trace File
        T = open(self.TraceFile,'w')
        T.close
        
            
    
    def ExecuteTest(self, T):
        DBConn = psycopg2.connect(dbname='CourseRegister', database='test', user='suleman', password='123', host='localhost', port='5432')
        DB = DBConn.cursor()
        print(T)
        DB.execute(open(T,'r').read())
        DB.close
        DBConn.close
    
