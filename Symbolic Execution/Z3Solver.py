from z3 import *
from TestCaseParser import TestCaseParser
from Table import Table

class Z3Solver:
    
    def __init__(self,proc_name):
        self.S = Solver()       # Actaul Solver Object
        self.Z3depth = 0        # also represents trace file lines to skip
        self.proc_name = proc_name
        self.DepthChoiceOptions = {}
        self.CaseParser = TestCaseParser(self.proc_name)
        
        #initializing the variables for z3
        self.Alaises = {}           # key = alais       value = Name
        self.Variables = {}         # key = Name        value = Object
        self.Types = {}             # key = Name        value = Type
        self.Tables = {}            # key = Tablename   value = Table Object 
        self.InternalTables = {}    # key =             value = 
        
        
        DetailsFile = './Resources/'+proc_name+'Details.txt'
        Details = open(DetailsFile,'r')
        
        NumberOfInputs = int(Details.readline())
        for i in range(NumberOfInputs):
            Line = Details.readline()
            In = Line.split()
            self.SetupVariable(In)
                     
        NumberOfLocals = int(Details.readline())
        for i in range(NumberOfLocals):
            Line = Details.readline()
            Local = Line.split()
            self.SetupVariable(Local)    
        
        NumberOfTables = int(Details.readline())
        for i in range(NumberOfTables):
            Tablename = Details.readline()
            if not (self.Tables.__contains__(Tablename)):
                self.Tables[Tablename] = Table(Tablename, True)
            
        Details.close
        
              
        
    def Check(self, TraceFile):
        Trace = open(TraceFile, 'r')
        
        #set back variables with name
        for k, v in self.Variables.items():
            code = k+" = v[-1]"
            print(code)
            exec(code)
        
        for i in range(self.Z3depth):
            Trace.readline()
        
        Line = (Trace.readline())[:-1]
        while Line != '':
            Parts = Line.split('\t')
            if Parts[0] == 'IF':
                self.S.push()
                Condition = Parts[1] 
                code = "self.S.add("+Condition+")"
                print(code)
                exec(code)
                ##Bookkeeping
                self.Z3depth = self.Z3depth + 1
                self.DepthChoiceOptions[self.Z3depth] = ['Not('+Condition+')']
                
                
            elif Parts[1] == 'Ssdjsk':
                pass
            else:
                pass
            Line = (Trace.readline())[:-1]
        
        Trace.close()
        print(self.S)
        
        while True:
            broken = False        
            while self.DepthChoiceOptions.__len__() != 0:
                self.S.pop()
                if len(self.DepthChoiceOptions[self.Z3depth]) != 0:
                    Condition = self.DepthChoiceOptions[self.Z3depth].pop(0)
                    code = code = "self.S.add("+Condition+")"
                    print(code)
                    self.S.push()
                    exec(code)
                    broken = True
                    break
                else:
                    del self.DepthChoiceOptions[self.Z3depth]
                    self.Z3depth = self.Z3depth - 1
            
            if broken == True:    
                print(self.S)
                check = self.S.check()
                print(check)
                if check.r == 1:
                    M = self.S.model()
                    T = self.CaseParser.getCase(M, self.Variables, self.Types, self.Alaises, self.Tables)
                    return T
            else:
                return 0        #search completed
        
        
        
    def SetupVariable(self, In):
        Type = In[0]
        Name = In[1]
        
        if not (self.Variables.__contains__(Name)):
            self.Variables[Name] = []
            self.Types[Name] = Type
                
        if (Type == 'Int'):
            self.Variables[Name].append(Int(Name))
            
        elif (Type == 'String'):
            pass
        
        elif (Type == 'Date'):
            pass
        
        if (len(In) > 2):
            Alais = In[2]
            self.Alaises[Alais] = Name
        
    def get_first_test_case(self):
        self.S.check()
        M = self.S.model()
        return self.CaseParser.getCase(M, self.Variables, self.Types, self.Alaises, self.Tables)