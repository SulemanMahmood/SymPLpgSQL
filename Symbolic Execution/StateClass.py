from z3 import Int
from Table import Table
from ChoicesClass import ChoicesClass

class StateClass:
    Current_Variables = {}
    Current_Tables = {}
    #Current_Choices
    Current_State_id = 0
    PreviousChoice_State_ID = 0
    
    Types = {}
    Alaises = {}
    
    State = {}
    
    def __init__(self, proc_name):
        DetailsFile = './Resources/'+proc_name+'Details.txt'
        Details = open(DetailsFile,'r')
        
        self.State[self.Current_State_id] = {}
        self.State[self.Current_State_id]['Variables'] = {}
        self.State[self.Current_State_id]['Tables'] = {}
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
         
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
            if not (self.State[self.Current_State_id]['Tables'].__contains__(Tablename)):
                self.State[self.Current_State_id]['Tables'][Tablename] = Table(Tablename, True)
                     
        Details.close
        
        #Initialize Current State
        self.Set_Current_State()      
        
    def SetupVariable(self, In):
        Type = In[0]
        Name = In[1]
        
        self.Types[Name] = Type
                
        if (Type == 'Int'):
            self.State[self.Current_State_id]['Variables'][Name] = Int(Name)
            
        elif (Type == 'String'):
            pass
        
        elif (Type == 'Date'):
            pass
        
        if (len(In) > 2):
            Alais = In[2]
            self.Alaises[Alais] = Name
                
    def Set_Current_State(self):
        self.Current_Variables = self.State[self.Current_State_id]['Variables']
        self.Current_Tables = self.State[self.Current_State_id]['Tables']
        self.Current_Choices = self.State[self.Current_State_id]['Choices']
        
    def getTableListForTestCase(self):
        List = []
        for k in self.State[0]['Tables']:
            List.append(k)
        return List
    
    def getColumnNamesListForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getColumnNameList()
    
    def getNoOfInputs(self):
        return len(self.Alaises)
    
    def getColumnTypesListForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getColumnTypeList()
    
    def getZ3ObjectFromNameForTestCase(self,Name):
        if self.Alaises.__contains__(Name):
            return self.State[0]['Variables'][self.Alaises[Name]]
        else:
            return self.State[0]['Variables'][Name]
        
    def getZ3ObjectFromName(self,Name):
        if self.Alaises.__contains__(Name):
            return self.State[self.Current_State_id]['Variables'][self.Alaises[Name]]
        else:
            return self.State[self.Current_State_id]['Variables'][Name]

    def getTypeFromNameForTestCase(self,Name):
        if self.Alaises.__contains__(Name):
            return self.Types[self.Alaises[Name]]
        else:
            return self.Types[Name]
    
    def getTableRowForTestCase(self, TableName):
        return self.State[0]['Tables'][TableName].getRows()
    
    def getNumberOfRowsForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getNumberOfRows()

    def getTraceLinesToDiscard(self):
        return self.Current_State_id
        
    def getPKColumnsForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getPKColumns()
        
    def getZ3ObjectForTableElement(self,TableName, ColIndex, RowNum):
        return self.State[0]['Tables'][TableName].getZ3ObjectForTableElement(ColIndex, RowNum)
        
    def AdvanceState(self):
        Old_State_id = self.Current_State_id
        self.Current_State_id = self.Current_State_id + 1
        self.State[self.Current_State_id] = {}
        self.State[self.Current_State_id]['Variables'] = {}
        self.State[self.Current_State_id]['Tables'] = {}
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
        
        for K in self.State[Old_State_id]['Variables']:
            self.State[self.Current_State_id]['Variables'][K] = self.State[Old_State_id]['Variables'][K]
            
        for K in self.State[Old_State_id]['Tables']:
            self.State[self.Current_State_id]['Tables'][K] = self.State[Old_State_id]['Tables'][K].Copy()
            
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
            
        self.Set_Current_State()
        
    def ProcessLine(self,Line):
        self.AdvanceState()
        Parts = Line.split('\t')
        
        # Here we interpret our instrumentation
        if Parts[0] == 'IF':    
            Condition = Parts[1]
            Condition = self.SubstituteVars(Condition)
               
            self.State[self.Current_State_id]['Choices'].AddChoice(Condition, {}, {})
            self.State[self.Current_State_id]['Choices'].AddChoice('Not('+Condition+')', {}, {})
            
            return False
        
    def SubstituteVars(self,Condition):
        for k, v in self.Alaises.items():
            Condition = Condition.replace(' '+k+' ', ' '+self.Alaises[k]+' ')
            Condition = Condition.replace('('+k+' ', '('+self.Alaises[k]+' ')
            Condition = Condition.replace(' '+k+')', ' '+self.Alaises[k]+')')
            Condition = Condition.replace('('+k+')', '('+self.Alaises[k]+')')
        
        for k, v in self.Current_Variables.items():
            Condition = Condition.replace(' '+k+' ', " self.State.getZ3ObjectFromName('"+k+"') ")
            Condition = Condition.replace('('+k+' ', "(self.State.getZ3ObjectFromName('"+k+"') ")
            Condition = Condition.replace(' '+k+')', " self.State.getZ3ObjectFromName('"+k+"'))")
            Condition = Condition.replace('('+k+')', "(self.State.getZ3ObjectFromName('"+k+"'))")
            
        return Condition
    
    def NextChoice(self):
        Cond, Var_upd, Tbl_upd = self.Current_Choices.getNextCondition()
        # No idea what to do with others yet
        
        State_Advanced = self.Current_State_id > self.PreviousChoice_State_ID
        self.PreviousChoice_State_ID = self.Current_State_id
        return Cond, State_Advanced
    
    def BackTrack(self):
        del self.State[self.Current_State_id]
        self.Current_State_id = self.Current_State_id - 1
        self.Set_Current_State()
        if (self.Current_State_id == 0):
            return True
        else:
            return False
        