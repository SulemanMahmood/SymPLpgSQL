from z3 import *

class Z3Solver:
    
    def __init__(self, CaseParser, TraceFile):
        self.S = Solver()
        self.Z3depth = 0        # also represents trace file lines to skip
        self.CaseParser = CaseParser
        self.TraceFile = TraceFile
        self.DepthChoiceOptions = {}
        
        #initializing the inputs for z3
        self.Inputs = {}
        
        for i in range(self.CaseParser.IndexByOrder.__len__()):
            var = self.CaseParser.IndexByOrder[i]
            Type = var[0];
            Name = var[1];
            
            if not (self.Inputs.__contains__(Name)):
                self.Inputs[Name] = []
            
            if Type == 'Int':
                self.Inputs[Name].append(Int(Name))
                
            elif Type == 'Sonedjsdf':
                pass
            else:
                pass
                
        
    def Check(self):
        Trace = open(self.TraceFile, 'r')
        
        #set back variables with name
        for k, v in self.Inputs.items():
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
                    T = self.CaseParser.ParseModel(M,self.Inputs)
                    return T
            else:
                return 0        #search completed
            