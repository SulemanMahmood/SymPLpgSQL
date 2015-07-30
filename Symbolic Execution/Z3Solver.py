from z3 import *
from Config import *


class Z3Solver:
    
    def __init__(self, State, CaseParser):
        self.S = Solver()       # Actaul Solver Object
        self.DepthChoiceOptions = {}
        self.State = State
        self.CaseParser = CaseParser
        self.checkcount = 0;
                     
    def Check(self):        
        Trace = open(TraceFile, 'r')
        
        for _ in range(self.State.getTraceLinesToDiscard()):   # Discard lines when we are at base depth
            Trace.readline()
        
        Line = Trace.readline()
        while Line != '':
            Line = Line[:-1]
            try:       
                ProceedToNextLine = self.ProcessLine(Line)
            except Exception as e:
                if e.message == 'Symbolic Executor: Maximum Stack Depth Reached':
                    self.CaseParser.IncrementCaseNumber()
                    ProceedToNextLine = False
#                     raise
                else:
                    raise
                
            if ProceedToNextLine:
                Line = Trace.readline()
                continue
            else:
                break
        Trace.close()
        
        # Advance Case Number
        if Line == '':
            self.CaseParser.IncrementCaseNumber()
        
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
                    PrintLog(code)
                    exec(code)
                    Condition = self.State.AddAllBaseConditionsForTestCase('')
                    code = 'self.S.add('+Condition+')'
                    PrintLog(code)
                    self.S.push()   # establishing save point before adding base contraints
                    exec(code)
                    PrintLog(self.S)
                    broken = True
                    break
                
            if broken == True:
                self.checkcount = self.checkcount + 1   #just for fun    
                check = self.S.check()
                PrintLog(check)
                self.S.pop()    #poping out base constraints
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
        PrintLog(self.S)
        self.S.check()
        self.S.pop()
        M = self.S.model()
        return self.CaseParser.getCase(M, self.State)
        
    def ProcessLine(self, Line):
        ProcessFurther = self.State.ProcessLine(Line)
        if ProcessFurther:
            Condition, _ = self.State.NextChoice()
            code = 'self.S.add('+Condition+')'
            self.S.push()
            PrintLog(code)
            exec(code)
            return True
        else:
            return False
        
    def getCheckCount(self):
        return self.checkcount
        