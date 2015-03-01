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
            BaseConstraint = self.AddConstraints('', table)
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
    
    
    
    def ProcessLine(self,Parts):    
        if Parts[0] == 'T_SeqScan':
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
        #Primary Key Constraint
        Rows = self.State.getNumberOfRowsForTestCase(TableName)
        for i in range(Rows):
            for j in range(i+1,Rows):
                for k in self.State.getPKColumnsForTestCase(TableName):
                    Condition = Condition + "self.State.getZ3ObjectForTableElement('"+TableName+"', "+k.__str__()+", "+i.__str__()+")" + " != " + "self.State.getZ3ObjectForTableElement('"+TableName+"', "+k.__str__()+", "+j.__str__()+")" + ", "
        
        return Condition
        
                