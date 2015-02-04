from TestCaseParser import TestCaseParser
from Z3Solver import Z3Solver
import psycopg2

class SymbolicExecutor:
    
    def __init__(self, proc_name, ProcDetailFile, TraceFile):
        self.CaseParser = TestCaseParser(proc_name,ProcDetailFile)
        self.TraceFile = TraceFile
        self.proc_name = proc_name
        
    
    def run(self):
        T = self.CaseParser.get_first_test_case()
        Z3 = Z3Solver(self.CaseParser, self.TraceFile)
        
        while True:
            self.CleanUp()
            self.ExecuteTest(T)
            T = Z3.Check()
            if not isinstance(T, int):
                pass
            else:
                break
        
    def CleanUp(self):
        T = open(self.TraceFile,'w')
        T.close
        
        # Nothing to clean in DB right now
        # or Case parser od case can be used to selectvely clean the DB
            
    
    def ExecuteTest(self, T):
        DBConn = psycopg2.connect(dbname='CourseRegister', database='test', user='suleman', password='123', host='localhost', port='5432')
        DB = DBConn.cursor()
        print(T)
        DB.execute(open(T,'r').read())
        DB.close
        DBConn.close
    
