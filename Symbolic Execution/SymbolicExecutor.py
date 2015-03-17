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
        Data, Test = Z3.get_first_test_case()
        
        while True:
            self.ExecuteTest(Data)
            self.CleanUp()
            self.ExecuteTest(Test)
            Data, Test = Z3.Check(self.TraceFile)
            if Test == None:
                break;
            
        
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
    
