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
            ProceedToNextLine = self.ProcessLine(Line)
            if ProceedToNextLine:
                Line = (Trace.readline())[:-1]
                continue
            else:
                break
        Trace.close()
        
        while True:
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
                    print(code)
                    exec(code)
                    Condition = self.State.AddAllBaseConditionsForTestCase('')
                    code = 'self.S.add('+Condition+')'
                    self.S.push()
                    exec(code)
                    print(self.S)
                    broken = True
                    break
                
            if broken == True:    
                check = self.S.check()
                print(check)
                self.S.pop()
                if check.r == 1:
                    M = self.S.model()
                    return self.CaseParser.getCase(M, self.State)
            else:
                return None, None        #search completed
            
    def get_first_test_case(self):
        BaseConstraint = self.State.AddAllBaseConditionsForTestCase('')
        code = 'self.S.add('+BaseConstraint+')'
        self.S.push()
        exec(code)
        print(self.S)
        self.S.check()
        self.S.pop()
        M = self.S.model()
        return self.CaseParser.getCase(M, self.State)
        
    def ProcessLine(self, Line):
        ProcessFurther = self.State.ProcessLine(Line)
        if ProcessFurther:
            Condition, StateAdvanced = self.State.NextChoice()
            code = 'self.S.add('+Condition+')'
            self.S.push()
            exec(code)
            return True
        else:
            return False