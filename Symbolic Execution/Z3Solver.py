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
        
        for i in range(self.Z3depth):   # Discard lines when we are at base depth
            Trace.readline()
        
        Line = (Trace.readline())[:-1]
        while Line != '':
            self.S.push()
            self.Z3depth = self.Z3depth + 1
            if not self.DepthChoiceOptions.__contains__(self.Z3depth):
                self.DepthChoiceOptions[self.Z3depth] = []
            
            Parts = Line.split('\t')
            self.ProcessLine(Parts)
            
            Line = (Trace.readline())[:-1]
        
        Trace.close()
        
        while True:
            broken = False        
            while self.DepthChoiceOptions.__len__() != 0:
                self.S.pop()
                if len(self.DepthChoiceOptions[self.Z3depth]) != 0:
                    ConStruct = self.DepthChoiceOptions[self.Z3depth].pop(0)
                    Condition = ConStruct[0]
                    self.S.push()
                    if (Condition != ''):
                        code = code = "self.S.add("+Condition+")"
                        print(code)
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
    
    
    
    def ProcessLine(self,Parts):
        if Parts[0] == 'IF':
            
            Condition = Parts[1]
            Condition = self.SubstituteVars(Condition)   
            code = "self.S.add("+Condition+")"
            print(code)
            exec(code)
            
            ConStruct = ['Not('+Condition+')', []]
            self.DepthChoiceOptions[self.Z3depth].append(ConStruct)
            
            
        elif Parts[0] == 'T_SeqScan':
            i = 1
            TableName = Parts[i]
            i = i+1
            
            if (Parts[i] == 'Conditions'):
                #Conditions exist
                (self.Tables[TableName]).addRow()
                (self.Tables[TableName]).addRow()
                
                Condition, i = self.MakeCondition(Parts, i+1, '')
                Condition = self.SubstituteVars(Condition)
                NoDataCond = 'Not('+Condition+')'
                
                print(Condition)
                
                #No Data Found
                CompleteCondition = ''
                for j in range((self.Tables[TableName]).getNumberOfRows()):
                    CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, j) + ', '
                
                CompleteCondition = self.AddConstraints(CompleteCondition, TableName)
                CompleteCondition = CompleteCondition[:-2]
                print(CompleteCondition)
                ConStruct = [CompleteCondition, []]
                self.DepthChoiceOptions[self.Z3depth].append(ConStruct)
                    
                    
                #One Row Found
                for j in range((self.Tables[TableName]).getNumberOfRows()):
                    CompleteCondition = ''
                    CompleteCondition = CompleteCondition + self.SubstituteTableRow(Condition, TableName, j) + ', '
                    for k in range((self.Tables[TableName]).getNumberOfRows()):
                        if (j == k):
                            pass
                        else:
                            CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, k) + ', '
                    
                    CompleteCondition = self.AddConstraints(CompleteCondition, TableName)
                    CompleteCondition = CompleteCondition[:-2]
                    print(CompleteCondition)
                    ConStruct = [CompleteCondition, []]
                    self.DepthChoiceOptions[self.Z3depth].append(ConStruct)
                
                #Two Rows Found
                for j in range((self.Tables[TableName]).getNumberOfRows()):
                    CompleteCondition = ''
                    CompleteCondition = CompleteCondition + self.SubstituteTableRow(Condition, TableName, j) + ', '
                    for k in range(j+1, (self.Tables[TableName]).getNumberOfRows()):
                        CompleteCondition = CompleteCondition + self.SubstituteTableRow(Condition, TableName, k) + ', '
                    
                        for l in range((self.Tables[TableName]).getNumberOfRows()):
                            if (l == j or l == k):
                                pass
                            else:
                                CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, k) + ', '
                                
                        CompleteCondition = self.AddConstraints(CompleteCondition, TableName)
                        CompleteCondition = CompleteCondition[:-2]
                        print(CompleteCondition)
                        ConStruct = [CompleteCondition, []]
                        self.DepthChoiceOptions[self.Z3depth].append(ConStruct)
                
                
            else:
                #all rows selected
                RowCount = (self.Tables[TableName]).getNumberOfRows()
                if (RowCount > 0):
                    #table in not Null so need to construct internal table
                    pass
        else:
            pass
        
        
    
    def MakeCondition(self,Parts,i,Condition):
        if Parts[i] == '=':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '(')
            Condition = Condition + ' = '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ')', i+1
        
        elif Parts[i] == '>':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '(')
            Condition = Condition + ' > '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ')', i+1
        
        elif Parts[i] == '<':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '(')
            Condition = Condition + ' > '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ')', i+1
        
        else:
            Condition = Condition + Parts[i]
            return Condition, i
        
        
        
    def SubstituteVars(self,Condition):
        for k, v in self.Alaises.items():
            Condition = Condition.replace(' '+k+' ', ' '+(self.Alaises[k])[-1]+' ')
            Condition = Condition.replace('('+k+' ', '('+(self.Alaises[k])[-1]+' ')
            Condition = Condition.replace(' '+k+')', ' '+(self.Alaises[k])[-1]+')')
            Condition = Condition.replace('('+k+')', '('+(self.Alaises[k])[-1]+')')
        
        for k, v in self.Variables.items():
            Condition = Condition.replace(' '+k+' ', " (self.Variables['"+k+"'])[-1] ")
            Condition = Condition.replace('('+k+' ', "((self.Variables['"+k+"'])[-1] ")
            Condition = Condition.replace(' '+k+')', " (self.Variables['"+k+"'])[-1])")
            Condition = Condition.replace('('+k+')', "((self.Variables['"+k+"'])[-1])")
            
        return Condition
    
    
    
    def SubstituteTableRow(self, Condition, TableName, RowNum):
        T = self.Tables[TableName]
        Cols = T.ColumsByIndex
        for i in range(len(Cols)):
            Name = (Cols[i])[1]
            Condition = Condition.replace(' '+Name+' ', " (((self.Tables['"+TableName+"']).Rows)["+RowNum.__str__()+"])["+i.__str__()+"] ")
            Condition = Condition.replace('('+Name+' ', "((((self.Tables['"+TableName+"']).Rows)["+RowNum.__str__()+"])["+i.__str__()+"] ")
            Condition = Condition.replace(' '+Name+')', " (((self.Tables['"+TableName+"']).Rows)["+RowNum.__str__()+"])["+i.__str__()+"])")
            Condition = Condition.replace('('+Name+')', "((((self.Tables['"+TableName+"']).Rows)["+RowNum.__str__()+"])["+i.__str__()+"])")
        
        return Condition
    
    
    def AddConstraints(self, Condition, TableName):
        T = self.Tables[TableName]
        #Primary Key Constraint
        Rows = T.getNumberOfRows()
        for i in range(Rows):
            for j in range(i+1,Rows):
                for k in T.PK:
                    Condition = Condition + "(((self.Tables['"+TableName+"']).Rows)["+i.__str__()+"])["+k.__str__()+"]" + " != " + "(((self.Tables['"+TableName+"']).Rows)["+j.__str__()+"])["+k.__str__()+"]" + ", "
        
        return Condition
        
        
        
        