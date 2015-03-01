from z3 import *


class Z3Solver:
    State = {}
    
    def __init__(self, State, CaseParser):
        self.S = Solver()       # Actaul Solver Object
        self.DepthChoiceOptions = {}
        self.State = State
        self.CaseParser = CaseParser
             
              
        
    def Check(self, TraceFile):        
        Trace = open(TraceFile, 'r')
        
        for i in range(self.State.getTraceLinesToDiscard()):   # Discard lines when we are at base depth
            Trace.readline()
        
        Line = (Trace.readline())[:-1]
        while Line != '':       
            ProceedToNextLine = self.State.ProcessLine(Line)
            if not ProceedToNextLine:
                break
            Line = (Trace.readline())[:-1]
        Trace.close()
        
        while True:
            broken = False
            Condition, StateAdvanced = self.State.NextChoice()
            if not StateAdvanced:
                self.S.pop()       
            if (Condition == ''):   # if all choices are exhausted then Backtrack
                Terminate = self.State.BackTrack()
                if Terminate:
                    break
            else:
                code = 'self.S.add('+Condition+')'
                self.S.push()
                exec(code)
                print(self.S)
                broken = True
                break
            
        if broken == True:    
            check = self.S.check()
            print(check)
            if check.r == 1:
                M = self.S.model()
                T = self.CaseParser.getCase(M, self.State)
                return T
        else:
            return 0        #search completed
        
        
        
    def get_first_test_case(self):
        BaseConstraint = ''
        
        for table in self.State.getTableListForTestCase():
            BaseConstraint = self.State.AddConstraints('', table)
        BaseConstraint = BaseConstraint[:-2]
        code = 'self.S.add('+BaseConstraint+')'
        self.S.push()
        exec(code)
        print(self.S)
        self.S.check()
        M = self.S.model()
        T = self.CaseParser.getCase(M, self.State)
        self.S.pop()
        return T
        
                