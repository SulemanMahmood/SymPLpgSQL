from Table import Table
from ChoicesClass import ChoicesClass
from CombinationGenerater import CombinationGenerator
from Config import *
from ProcedureClass import *

class StateClass:    
    
    def __init__(self, Procedure, DataHandler):
        self.Current_State_id = 0
        self.PreviousChoice_State_ID = 0
        self.Call_ID_Seq = 0
        
        self.DataHandler = DataHandler
        
        self.State = {}
        self.State[self.Current_State_id] = {}
        self.State[self.Current_State_id]['CallStack'] = []
        self.State[self.Current_State_id]['Call_ID'] = 0
        self.State[self.Current_State_id]['Variables'] = {}
        self.State[self.Current_State_id]['Tables'] = {}
        self.State[self.Current_State_id]['CallStackNumber'] = 0
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
        #self.State[self.Current_State_id]['Results']     Added Later
        #self.State[self.Current_State_id]['Node']        Added Later
        self.State[self.Current_State_id]['Loops'] = []
        self.State[self.Current_State_id]['IFs'] = []
        self.TempFunctionCalls = []
        self.FunctionCalls = []
        self.State[self.Current_State_id]['IgnoreNodes'] = False
        
        self.Types = {}
        self.Current_Variables = {}
        self.Current_Tables = {}
        #self.Current_Choices        added later in current state setup
        #self.Current_Results        added later in Next Choice Function. Maybe useless.
        
        #Initialize Current State
        self.Set_Current_State()
         
        for Arg in Procedure.getArgList():
            self.SetupVariable(Arg)
            
        #Add Found Variable for Procedure
        self.State[self.Current_State_id]['Variables'][(self.CallStackNotoString() + 'found')] = False
        
    def SetupVariable(self, In):
        Type = In[0]
        Name = self.CallStackNotoString() + In[1]
        
        self.Types[Name] = Type            
        self.State[self.Current_State_id]['Variables'][Name] = self.DataHandler.getZ3Object(Type, Name)
        
    def CallStackNotoString(self):
        return 'P'+ self.State[self.Current_State_id]['Call_ID'].__str__() + '_'
    
    def TempCallStackNotoString(self, Call_ID):
        return 'P'+ Call_ID.__str__() + '_'
        
    def CallStackNotoStringForTestCase(self):
        return 'P'+ (0).__str__() + '_'
                
    def AddNewZ3ObjectForVariable(self,Name, Type):
        NewName = Name + "_" + self.Current_State_id.__str__()
        self.State[self.Current_State_id]['Variables'][Name] = self.DataHandler.getZ3Object(Type, NewName)
    
    def Set_Current_State(self):
        self.Current_Variables = self.State[self.Current_State_id]['Variables']
        self.Current_Tables = self.State[self.Current_State_id]['Tables']
        self.Current_Choices = self.State[self.Current_State_id]['Choices']
        
    def getTableListForTestCase(self):
        List = []
        for k in self.State[0]['Tables']:
            List.append(k)
            
        count = 0        
        FinalList = []        
        while List != []:
            count = count + 1
            if count > 50:
                raise Exception('Circular Foreign Key Relation Likely')
            
            for T in List:
                if self.getFKeyConsForTestCase(T) == []:
                    FinalList.append(T)
                else:
                    remove = True;
                    for FK in self.getFKeyConsForTestCase(T):
                        T1 = self.getTable(T)
                        ForeignTable = T1.getForeignTableName(FK)
                        if FinalList.__contains__(ForeignTable):
                            remove = remove & True
                        else:
                            remove = remove & False
                    if remove == True:
                        FinalList.append(T)                              
            
            for T in FinalList:
                if List.__contains__(T):
                    List.remove(T)
                    
        return FinalList
    
    def getTableName(self,table):
        return self.getTable(table).getName()
    
    def getDisabledConstraints(self,table):
        return self.getTable(table).getDisabledConstraints()
    
    def getColumnNamesListForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getColumnNameList()
    
    
    def getColumnTypesListForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getColumnTypeList()
    
    def getZ3ObjectFromNameForTestCase(self,Name):
        return self.State[0]['Variables'][self.CallStackNotoStringForTestCase() + Name]
        
    def getZ3ObjectFromName(self,Name):
        return self.State[self.Current_State_id]['Variables'][Name]
    
    def getOldZ3ObjectFromName(self,Name):
        return self.State[self.Current_State_id-1]['Variables'][Name]

    def getTypeFromNameForTestCase(self,Name):
        return self.Types[self.CallStackNotoStringForTestCase() + Name]
    
    def getTypeFromName(self,Name):
        return self.Types[Name]
    
    def getTableRowForTestCase(self, TableName):
        return self.State[0]['Tables'][TableName].getRows()
    
    def getNumberOfRowsForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getNumberOfRows()

    def getTraceLinesToDiscard(self):
        return self.Current_State_id
        
    def getUniqueConstaintsForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getUniqueConstaints()
    
    def getCheckConsForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getCheckCons()
    
    def getFKeyConsForTestCase(self,TableName):
        return self.State[0]['Tables'][TableName].getFKeyCons()
        
    def getZ3ObjectForTableElement(self,TableName, ColIndex, RowNum):
        return self.Current_Tables[TableName].getZ3ObjectForTableElement(ColIndex, RowNum)
    
    def getZ3ObjectForResultElement(self, ResultState, ColIndex, RowNum):
        return self.State[ResultState]['Results'].getZ3ObjectForTableElement(ColIndex, RowNum)
    
    def getZ3ObjectForTableElementForTestCase(self,TableName, ColIndex, RowNum):
        return self.State[0]['Tables'][TableName].getZ3ObjectForTableElement(ColIndex, RowNum)
    
    def getZ3ObjectFirstRowColumnFromPreviousResult(self,index):
        return self.State[self.Current_State_id - 1]['Results'].getZ3ObjectForTableElement(index,0)
        
    def isPreviousResultNULL(self):
        if self.State[self.Current_State_id - 1]['Results'] == None:
            return True
        else:
            return False
    
    def getPreviousResult(self):
        return self.State[self.Current_State_id-1]['Results']
        
    def AdvanceState(self):
        Old_State_id = self.Current_State_id
        self.Current_State_id = self.Current_State_id + 1
        self.State[self.Current_State_id] = {}
        self.State[self.Current_State_id]['Call_ID'] = self.State[Old_State_id]['Call_ID']
        self.State[self.Current_State_id]['Variables'] = {}
        self.State[self.Current_State_id]['Tables'] = {}
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
        self.State[self.Current_State_id]['CallStackNumber'] = self.State[Old_State_id]['CallStackNumber']
        self.State[self.Current_State_id]['IgnoreNodes'] = self.State[Old_State_id]['IgnoreNodes']
        self.State[self.Current_State_id]['Loops'] = self.State[Old_State_id]['Loops']
        self.State[self.Current_State_id]['IFs'] = self.State[Old_State_id]['IFs']
        self.State[self.Current_State_id]['CallStack'] = self.State[Old_State_id]['CallStack']
        
        for K in self.State[Old_State_id]['Variables']:
            self.State[self.Current_State_id]['Variables'][K] = self.State[Old_State_id]['Variables'][K]
            
        for K in self.State[Old_State_id]['Tables']:
            self.State[self.Current_State_id]['Tables'][K] = self.State[Old_State_id]['Tables'][K].Copy()
            
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
            
        self.Set_Current_State()
        
    def SubstituteVars(self,Condition):            
        for k, _ in self.Current_Variables.items():
            Condition = Condition.replace(' '+k+' ', " self.State.getZ3ObjectFromName('"+k+"') ")
            Condition = Condition.replace('('+k+' ', "(self.State.getZ3ObjectFromName('"+k+"') ")
            Condition = Condition.replace(' '+k+')', " self.State.getZ3ObjectFromName('"+k+"'))")
            Condition = Condition.replace('('+k+')', "(self.State.getZ3ObjectFromName('"+k+"'))")
        return Condition
            
    def SubstituteOldVars(self,Condition):
        for k, _ in self.Current_Variables.items():
            Condition = Condition.replace(' '+k+' ', " self.State.getOldZ3ObjectFromName('"+k+"') ")
            Condition = Condition.replace('('+k+' ', "(self.State.getOldZ3ObjectFromName('"+k+"') ")
            Condition = Condition.replace(' '+k+')', " self.State.getOldZ3ObjectFromName('"+k+"'))")
            Condition = Condition.replace('('+k+')', "(self.State.getOldZ3ObjectFromName('"+k+"'))")
        return Condition
    
    def NextChoice(self):
        Cond, Result_Table = self.Current_Choices.getNextCondition()
        self.State[self.Current_State_id]['Results'] = Result_Table
        self.Current_Results = Result_Table
        
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
    
    def MakeCondition(self,Parts,i,Condition, CalledFromNullTest = False):
        Node = Parts[i].split(' ')
        PrintLog(Node)
        if len(Node) == 1:
            if Node[0] in ['65', '67', '1048']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' == '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['144']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' != '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['147']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' > '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['66']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' > '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['150']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' >= '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['149']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' <= '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['177']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' + '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['181']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' - '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['141']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' * '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['154']:
                Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
                Condition = Condition + ' / '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['OR', 'or', 'Or']:
                Condition = Condition + ' Or( '
                Condition, i = self.MakeCondition(Parts, i+1, Condition)
                Condition = Condition + ' , '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['AND', 'and', 'And']:
                Condition = Condition + ' And( '
                Condition, i = self.MakeCondition(Parts, i+1, Condition)
                Condition = Condition + ' , '
                Condition, i = self.MakeCondition(Parts, i, Condition)
            
            elif Node[0] in ['Not', 'not']:
                Condition = Condition + 'Not( '
                Condition, i = self.MakeCondition(Parts, i + 1, Condition)
                
            elif Node[0] == 'T_NullTest':    ## this is a base case based on this we will treat booleans separately
                i = i + 1
                NullTestType = Parts[i]
                
                if NullTestType == 'IS_NULL':
                    Condition = Condition + '('
                    Condition, i = self.MakeCondition(Parts, i + 1, Condition, CalledFromNullTest = True)
                    Condition = Condition + ' == ' + self.DataHandler.NullValue.__str__()
                elif NullTestType == 'IS_NOT_NULL':
                    Condition = Condition + 'Not ('
                    Condition, i = self.MakeCondition(Parts, i + 1, Condition, CalledFromNullTest = True)
                    Condition = Condition + ' == ' + self.DataHandler.NullValue.__str__()
                    
            elif Node[0] == 'ARGUMENT_START':
                # Find Argument End
                starts_count = 1
                lookupindex = i
                while ( starts_count > 0):
                    lookupindex = lookupindex + 1
                    if Parts[lookupindex] == 'ARGUMENT_END':
                        starts_count = starts_count - 1
                    elif Parts[lookupindex] == 'ARGUMENT_START':
                        starts_count = starts_count + 1
                    
                PartsCopy = Parts[i+1 : lookupindex]
                Condition, _ = self.MakeCondition(PartsCopy, 0, '')
                return Condition, lookupindex + 1 
            
            else:
                raise Exception('Unkown Operator '+ Node[0])
            
            #Common operations for all operators
            Condition = Condition + ' )'
            if i < len(Parts) and Parts[i] != '' and (Condition.count('(') == Condition.count(')')): #support for multi-clause conditions
                Condition = 'And(' + Condition + ' , '
                Condition, i = self.MakeCondition(Parts, i, Condition)
                Condition = Condition + ' )'
            
            return Condition, i;
            
        else:
            if Node[0] == 'Col':
                Type = int(Node[1])
                Name = Node[2]
                Condition = Condition + self.DataHandler.ConditionHelper(Type, Name, CalledFromNullTest)
            
            elif Node[0] == 'Param':
                Type = int(Node[1])
                Name = self.CallStackNotoString() + Node[2]
                if Name == (self.CallStackNotoString() + 'found'):
                    Condition = Condition + self.Current_Variables[Name].__str__()
                else:
                    Condition = Condition + self.DataHandler.ConditionHelper(Type, Name, CalledFromNullTest)
            
            elif Node[0] == 'FunctionCall':
                Proc = getProcedureFromNumber(Node[1]) 
                ReturnType = Proc.getReturnType()
                
                #Making Function Call Condition
                self.Call_ID_Seq = self.Call_ID_Seq + 1 
                CallID = self.Call_ID_Seq
                    
                RetturnVariableName = self.TempCallStackNotoString(CallID) + 'RETURNVARIABLE'
                
                CallCondition = ''
                FunctionArgNames = []
                
                i = i + 1   # point to next node to be processed
                
                for Arg in Proc.getArgList() :
                    processedarg, i = self.MakeCondition(Parts, i, '')
                    ArgName = self.TempCallStackNotoString(CallID) + Arg[1]
                    Arg[1] = ArgName
                    FunctionArgNames.append(Arg)
                    C = ' ' + ArgName + " == " + processedarg
                    CallCondition = CallCondition + C + ' , '
                    
                CallCondition = CallCondition[:-2]
                
                FunctionCall = {}
                FunctionCall['FunctionID'] = Node[1]
                FunctionCall['CallCondition'] = CallCondition
                FunctionCall['ReturnVariableName'] = RetturnVariableName
                FunctionCall['ReturnType'] = ReturnType
                FunctionCall['ReturnStateID'] = None
                FunctionCall['Call_ID'] = CallID
                FunctionCall['FunctionArgNames'] = FunctionArgNames
                
                self.TempFunctionCalls.append(FunctionCall)
                
                Condition = Condition + ' ' + self.DataHandler.ConditionHelper(ReturnType, RetturnVariableName, CalledFromNullTest)
                i = i - 1  # to conform with logic of two part nodes
            
            else:   #Constants
                Type = int(Node[0])
                Value = Node[1];
                Condition = Condition + self.DataHandler.ProcessConstant(Type, Value).__str__()
                
            return Condition, i+1
    
    def SubstituteTableRow(self, Condition, TableName, RowNum):
        Table = self.Current_Tables[TableName]
        for Name in Table.getColumnNameList():
            Condition = Condition.replace(' '+Name+' ', " self.State.getZ3ObjectForTableElement('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+") ")
            Condition = Condition.replace('('+Name+' ', "(self.State.getZ3ObjectForTableElement('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+") ")
            Condition = Condition.replace(' '+Name+')', " self.State.getZ3ObjectForTableElement('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+"))")
            Condition = Condition.replace('('+Name+')', "(self.State.getZ3ObjectForTableElement('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+"))")
        return Condition
    
    def SubstituteTableRowForTestCase(self, Condition, TableName, RowNum):
        Table = self.State[0]['Tables'][TableName]
        for Name in Table.getColumnNameList():
            Condition = Condition.replace(' '+Name+' ', " self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+") ")
            Condition = Condition.replace('('+Name+' ', "(self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+") ")
            Condition = Condition.replace(' '+Name+')', " self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+"))")
            Condition = Condition.replace('('+Name+')', "(self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+"))")
        return Condition
    
    def SubstituteInnerResultRow(self, Condition, ResultState, RowNum):
        for i in range(self.State[ResultState]['Results'].getNumberOfCols()):
            Condition = Condition.replace(' INNER.' +i.__str__()+' ', " self.State.getZ3ObjectForResultElement(" + ResultState.__str__() + ", " + i.__str__() + ", " + RowNum.__str__() + ") ")
            Condition = Condition.replace('(INNER.' +i.__str__()+' ', "(self.State.getZ3ObjectForResultElement(" + ResultState.__str__() + ", " + i.__str__() + ", " + RowNum.__str__() + ") ")
            Condition = Condition.replace(' INNER.' +i.__str__()+')', " self.State.getZ3ObjectForResultElement(" + ResultState.__str__() + ", " + i.__str__() + ", " + RowNum.__str__() + "))")
            Condition = Condition.replace('(INNER.' +i.__str__()+')', "(self.State.getZ3ObjectForResultElement(" + ResultState.__str__() + ", " + i.__str__() + ", " + RowNum.__str__() + "))")
        return Condition
        
    def SubstituteOuterResultRow(self, Condition, ResultState, RowNum):
        for i in range(self.State[ResultState]['Results'].getNumberOfCols()):
            Condition = Condition.replace(' OUTER.' +i.__str__()+' ', " self.State.getZ3ObjectForResultElement(" + ResultState.__str__() + ", " + i.__str__() + ", " + RowNum.__str__() + ") ")
            Condition = Condition.replace('(OUTER.' +i.__str__()+' ', "(self.State.getZ3ObjectForResultElement(" + ResultState.__str__() + ", " + i.__str__() + ", " + RowNum.__str__() + ") ")
            Condition = Condition.replace(' OUTER.' +i.__str__()+')', " self.State.getZ3ObjectForResultElement(" + ResultState.__str__() + ", " + i.__str__() + ", " + RowNum.__str__() + "))")
            Condition = Condition.replace('(OUTER.' +i.__str__()+')', "(self.State.getZ3ObjectForResultElement(" + ResultState.__str__() + ", " + i.__str__() + ", " + RowNum.__str__() + "))")
        return Condition
        
    def AddConstraintsForTestCase(self, Condition, TableName):
        #Unique Constraints        also contains uniquness part of primary key
        Rows = self.getNumberOfRowsForTestCase(TableName)
        for eachcon in self.getUniqueConstaintsForTestCase(TableName):
            for i in range(Rows):
                for j in range(i+1,Rows):
                    C = 'Not(And('
                    for k in eachcon:
                        C = C + "self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', "+k.__str__()+", "+i.__str__()+")" + " == " + "self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', "+k.__str__()+", "+j.__str__()+")" + ", "
                    C = C[:-2]
                    C = C + ')), '    
                    Condition = Condition + C
                
        #Check Constraints
        for eachCon in self.getCheckConsForTestCase(TableName):
            C, _ = self.MakeCondition(eachCon.split('\t'), 0, '')
            for i in range(Rows):
                Condition = Condition + self.SubstituteTableRowForTestCase(C, TableName, i) + ', '
        
        #Foreign Key Handling                
        for ForeignKey in self.getFKeyConsForTestCase(TableName):
            T1 = self.getTable(TableName)
            Column = T1.getColumnIndexFromAttnum(ForeignKey)
            ForeignTable = T1.getForeignTableName(ForeignKey)
            T2 = self.getTable(ForeignTable)
            ForeginColumn = T2.getForeignColumnIndexFromAttnum(ForeignKey)
            
            Rows1 = self.getNumberOfRowsForTestCase(TableName)
            Rows2 = self.getNumberOfRowsForTestCase(ForeignTable)
            for i in range(Rows1):
                C = 'Or('
                for j in range(Rows2):
                    C = C + "self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', "+Column.__str__()+", "+i.__str__()+")" + " == " + "self.State.getZ3ObjectForTableElementForTestCase('"+ForeignTable+"', "+ForeginColumn.__str__()+", "+j.__str__()+")" + ", "
                C = C + "self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', "+Column.__str__()+", "+i.__str__()+")" + " == " + self.DataHandler.NullValue.__str__() + "), "
                Condition = Condition + C
        
        return Condition
    
    def AddConstraints(self, Condition, TableName):
        #Unique Constraints        also contains uniquness part of primary key
        Rows = self.getNumberOfRows(TableName)
        for eachcon in self.getUniqueConstaintsForTestCase(TableName):
            for i in range(Rows):
                for j in range(i+1,Rows):
                    C = 'Not(And('
                    for k in eachcon:
                        C = C + "self.State.getZ3ObjectForTableElement('"+TableName+"', "+k.__str__()+", "+i.__str__()+")" + " == " + "self.State.getZ3ObjectForTableElement('"+TableName+"', "+k.__str__()+", "+j.__str__()+")" + ", "
                    C = C[:-2]
                    C = C + ')), '    
                    Condition = Condition + C
        
        #Check Constraints        also contains not null part of primary key
        for eachCon in self.getCheckConsForTestCase(TableName):
            C, _ = self.MakeCondition(eachCon.split('\t'), 0, '')
            for i in range(Rows):
                Condition = Condition + self.SubstituteTableRow(C, TableName, i) + ', '
                
        #Foreign Key Handling                
        for ForeignKey in self.getFKeyConsForTestCase(TableName):
            T1 = self.getTable(TableName)
            Column = T1.getColumnIndexFromAttnum(ForeignKey)
            ForeignTable = T1.getForeignTableName(ForeignKey)
            T2 = self.getTable(ForeignTable)
            ForeginColumn = T2.getForeignColumnIndexFromAttnum(ForeignKey)
            
            Rows1 = self.getNumberOfRows(TableName)
            Rows2 = self.getNumberOfRows(ForeignTable)
            
            for i in range(Rows1):
                C = 'Or('
                for j in range(Rows2):
                    C = C + "self.State.getZ3ObjectForTableElement('"+TableName+"', "+Column.__str__()+", "+i.__str__()+")" + " == " + "self.State.getZ3ObjectForTableElement('"+ForeignTable+"', "+ForeginColumn.__str__()+", "+j.__str__()+")" + ", "
                C = C + "self.State.getZ3ObjectForTableElement('"+TableName+"', "+Column.__str__()+", "+i.__str__()+")" + " == " + self.DataHandler.NullValue.__str__() + "), "
                Condition = Condition + C
               
        return Condition[:-2]
    
    def AddTypeConstraintsOnVariablesForTestCase(self, Condition):
        for Name, Type in self.Types.items():
            C1 = self.DataHandler.getVariableTypeConstraint(Type, Name);
            if C1 != None:
                C, _ = self.MakeCondition(C1.split('\t'), 0, '')
                prefix = ' ' + self.CallStackNotoString()
                C = C.replace(prefix, ' ')
                Condition = Condition + self.SubstituteVars(C) + ', '
        
        return Condition
        
    def getNumberOfRows(self, TableName):
        return self.Current_Tables[TableName].getNumberOfRows()

    def AddAllBaseConditionsForTestCase(self, BaseConstraint):
        for table in self.getTableListForTestCase():
            BaseConstraint = self.AddConstraintsForTestCase(BaseConstraint, table)
        
        BaseConstraint = self.AddTypeConstraintsOnVariablesForTestCase(BaseConstraint)
        
        return BaseConstraint[:-2]
    
    def getPlanBottom(self,State_ID):
        NodeName = self.State[State_ID]['Node']
        if NodeName == 'T_SeqScan':
            return State_ID
        elif NodeName == 'T_Hash' or NodeName == 'T_Sort':
            return self.getPlanBottom(State_ID - 1)
        elif NodeName in ['T_HashJoin' , 'T_MergeJoin', 'T_NestLoop']:
            return self.getPlanBottom( self.getPlanBottom(State_ID - 1) - 1 )
        else:
            raise Exception('Unhandeld Node in get Plan Bottom '+ NodeName)
    
    def ProcessTargetList(self, ColList, Rows = None, Inner = None, Outer = None):
        TableRows = []
        if Rows == None:
            TableRows.append([])
        else:
            for _ in range(len(Rows)):
                TableRows.append([])
                
        T = Table('Result' + self.Current_State_id.__str__(),self.DataHandler, False, False);
        Condition = ''
        
        # Converting the list into a list of TargetEntries
        i = 0
        TargetList = []
        while i < len(ColList):
            if ColList[i] == 'TARGET_ENTRY':
                Entry = []
                i = i + 1
                while i < len(ColList) and ColList[i] != 'TARGET_ENTRY':
                    Entry.append(ColList[i])
                    i = i + 1
                TargetList.append(Entry)
        
        for row in range(len(TableRows)):
            for Target in TargetList:
                for Comps in Target:
                    Parts = Comps.split(' ')
                    if len(Parts) >= 2:
                        if Parts[0] == 'Col':
                            Type = Parts[1]
                            JoinParts = Parts[2].split('.')
                            
                            if Parts[1] == 'ctid':
                                InnerRow = Rows[row]
                                TableRows[row].append(InnerRow)
                                
                            elif len(JoinParts) == 2:
                                JoinTable = JoinParts[0]
                                ColIndex = int(JoinParts[1])
                                InnerRow = Rows[row][0]
                                OuterRow = Rows[row][1]
                                
                                if JoinTable == 'INNER':
                                    TableRows[row].append(Inner.getZ3ObjectForTableElement(ColIndex, InnerRow))
                                elif JoinTable == 'OUTER':
                                    TableRows[row].append(Outer.getZ3ObjectForTableElement(ColIndex, OuterRow)) 
                            
                            else:   # more conditions may be added later but right now else is a single table col supplied in Inner
                                ColIndex = Inner.getColumnIndexFromName(Parts[2])
                                InnerRow = Rows[row]
                                TableRows[row].append(Inner.getZ3ObjectForTableElement(ColIndex, InnerRow))
                                
                        elif Parts[0] == 'Param':
                            Name = self.CallStackNotoString() + Parts[2]
                            if self.Current_Variables.__contains__(Name):
                                TableRows[row].append(self.Current_Variables[Name])
                        
                        elif Parts[0] == 'AS':
                            Name = Parts[1]
                            IndexToAddName = len(TableRows[row]) - 1
                            T.setColumnName(IndexToAddName, Name)
                            
                        elif Parts[0] == 'FunctionCall':
                            if Rows != None:
                                raise Exception ('Target List Call not from T_Result')
                            
                            FunctionID = Parts[1]
                            
                            ColIndex = len(TableRows[row])
                            Last = Target[-1]
                            isAs = Last.split(' ')
                            if isAs[0] == 'AS':
                                Name = isAs[1]
                                T.setColumnName(ColIndex, Name)
                                Target = Target[:-1]                        
                            
                            # Now Play with Target
                            Expr , _ = self.MakeCondition(Target, 0, '')
                            Expr = self.SubstituteOldVars(' ' + Expr + ' ')
                                
                            for F in self.TempFunctionCalls:
                                F1, Expr = self.SubstituteInFunctionCall(F, Expr)
                                self.FunctionCalls.append(F1)
                                              
                            self.TempFunctionCalls = []
                            
                            ResultName = self.CallStackNotoString() + T.getName()
                            Type = getProcedureReturnType(FunctionID)
                            
                            TableRows[row].append(self.DataHandler.getZ3Object(Type, ResultName))
                            
                            C = "self.State.getZ3ObjectForResultElement( " + self.Current_State_id.__str__() + " , " + ColIndex.__str__() + " , " + row.__str__() +" )" + ' == ' + Expr
                            PrintLog(C)
                            Condition = Condition + C + ", "
                            break
                        
                        else:
                            Type = int(Parts[0])
                            Value = Parts[1]
                        
                            TableRows[row].append(self.DataHandler.ProcessConstant(Type, Value))
                            
                    else:   # Encountered an Operation. Find and remove the AS condition and pass the rest to make condition
                        if Rows != None:
                            raise Exception ('Target List Call not from T_Result')
                        
                        ColIndex = len(TableRows[row])
                        Last = Target[-1]
                        isAs = Last.split(' ')
                        if isAs[0] == 'AS':
                            Name = isAs[1]
                            T.setColumnName(ColIndex, Name)
                            Target = Target[:-1]                        
                        
                        # Now Play with Target
                        Expr , _ = self.MakeCondition(Target, 0, '')
                        Expr = self.SubstituteOldVars(' ' + Expr + ' ')
                            
                        for F in self.TempFunctionCalls:
                            F1, Expr = self.SubstituteInFunctionCall(F, Expr)
                            self.FunctionCalls.append(F1)
                                          
                        self.TempFunctionCalls = []
                        
                        ResultName = self.CallStackNotoString() + T.getName()
                        Type = getProcedureReturnType(Target[0])
                        
                        TableRows[row].append(self.DataHandler.getZ3Object(Type, ResultName))
                        
                        C = "self.State.getZ3ObjectForResultElement( " + self.Current_State_id.__str__() + " , " + ColIndex.__str__() + " , " + row.__str__() +" )" + ' == ' + Expr
                        PrintLog(C)
                        Condition = Condition + C + ", "
                        break
                        
        if Condition != '':
            Condition = Condition[:-2]
                    
        T.setRows(TableRows)
        return T, Condition ;
    
    def SubstituteInFunctionCall(self,F, Expr):
        # Process return variable
        ReturnVariableName = F['ReturnVariableName']
        ReturnType = F['ReturnType']
        self.Types[ReturnVariableName] = ReturnType
        self.State[self.Current_State_id]['Variables'][ReturnVariableName] = self.DataHandler.getZ3Object(ReturnType, ReturnVariableName)
        Expr = Expr.replace(' ' + ReturnVariableName + ' ', " self.State.getZ3ObjectFromName('" + ReturnVariableName + "') ")
        
        # Process Call Condition
        CallCondition = F['CallCondition']
        for FunctionArg in F['FunctionArgNames']:
            ArgName = FunctionArg[1]
            ArgType = FunctionArg[0]
            self.Types[ArgName] = FunctionArg[0]
            self.State[self.Current_State_id]['Variables'][ArgName] = self.DataHandler.getZ3Object(ArgType, ArgName)
            CallCondition = CallCondition.replace(' ' + FunctionArg[1] + ' ', " self.State.getZ3ObjectFromName('" + ArgName + "') ")
            
        CallCondition = self.SubstituteVars(CallCondition)
        PrintLog(CallCondition)   
        
        F['CallCondition'] = CallCondition
        
        return F, Expr
    
    def getTable(self, TableName):
        if self.Current_Tables.__contains__(TableName):
            return self.Current_Tables[TableName]
        else:
            return self.AddNewTable(TableName)
        
    def AddNewTable(self, TableName):
        T = Table(TableName, self.DataHandler)
        for state in range(self.Current_State_id + 1):
            T1 = T.Copy()
            self.State[state]['Tables'][TableName] = T1
        
        #Adding tables referenced by foreign key relations
        ForeignTables = T.getForeignTables()
        for FTable in ForeignTables:
            self.getTable(FTable)
        
        return self.Current_Tables[TableName]
    
    def ProcessLine(self,Line, AdvanceState = True):
        if AdvanceState == True:
            self.AdvanceState()
        
        Parts = Line.split('\t')
        self.State[self.Current_State_id]['Node'] = Parts[0]
        PrintLog(Parts)
        
        if self.State[self.Current_State_id]['IgnoreNodes'] == True:
            if Parts[0] == 'PLPGSQL_STMT_EXECSQL_END':
                self.State[self.Current_State_id]['IgnoreNodes'] = False
                self.Current_Choices.AddChoice('True', None)
                return True
            else:
                self.Current_Choices.AddChoice('True', None)
                return True
        
        # Here we interpret our instrumentation
        ######################################################################################################################
        ####################################################   IF   ##########################################################
        ######################################################################################################################
        if Parts[0] == 'PLPGSQL_STMT_IF':
            IF = {}
            IF['StartingState'] = self.Current_State_id
            if Parts[1] == 'COMPLEX_CONDITION':
                IF['COMPLEX'] = True
                self.State[self.Current_State_id]['IFs'].append(IF)
                self.Current_Choices.AddChoice('True', None)
                return True
                
            else:
                IF['COMPLEX'] = False
                self.State[self.Current_State_id]['IFs'].append(IF)
                    
                Condition, i = self.MakeCondition(Parts,1,'')
                PrintLog(Condition)
                
                Condition = self.SubstituteOldVars(' ' + Condition + ' ')
                
                for F in self.TempFunctionCalls:
                    F1, Condition = self.SubstituteInFunctionCall(F, Condition)
                    self.FunctionCalls.append(F1)
                        
                self.TempFunctionCalls = []
                
                PrintLog(Condition)
                   
                self.Current_Choices.AddChoice(Condition, None)
                self.Current_Choices.AddChoice('Not('+Condition+')', None)
                return False
            
        ######################################################################################################################
        ###########################################   PLPGSQL_STMT_IF_END   ##################################################
        ######################################################################################################################
        if Parts[0] == 'PLPGSQL_STMT_IF_END':
            if self.State[self.Current_State_id]['IFs'] == []:
                self.Current_Choices.AddChoice('True', None)
                return True
            
            IF = self.State[self.Current_State_id]['IFs'].pop()

            if IF['COMPLEX'] == True:
                IF['COMPLEX'] = True
                self.State[self.Current_State_id]['IFs'].append(IF)
                Condition = ' self.State.getZ3ObjectForResultElement( ' + (self.Current_State_id - 1).__str__() + ' , 0, 0) == ' + self.DataHandler.ProcessConstant(16,'True').__str__() + ' )'
                NotCondition = ' self.State.getZ3ObjectForResultElement( ' + (self.Current_State_id - 1).__str__() + ' , 0, 0) == ' + self.DataHandler.ProcessConstant(16,'False').__str__() + ' )'
                self.Current_Choices.AddChoice(Condition, None)
                self.Current_Choices.AddChoice(NotCondition, None)
                return False
                
            else:
                self.Current_Choices.AddChoice('True', None)
                return True
            
        ######################################################################################################################
        ###########################################  T_SeqScan & T_IndexScan  ################################################
        ######################################################################################################################        
        elif Parts[0] == 'T_SeqScan' or Parts[0] == 'T_IndexScan':
            TableName = Parts[1]
            i = 2
            if Parts[i] == 'TargetList':
                ColumnList = []
                i = i+1
                while (i < len(Parts) and Parts[i] != 'Conditions' and Parts[i] != '') :
                    ColumnList.append(Parts[i])
                    i = i+1
                    
            ConditionStartingValue_i = i + 1;
            
            if ((i < len(Parts) and Parts[i] == 'Conditions')):
                
                Condition, _ = self.MakeCondition(Parts, ConditionStartingValue_i, '')
                Condition = self.SubstituteVars(Condition)
                NoDataCond = 'Not('+Condition+')'
                PrintLog(Condition)
                
                if self.TempFunctionCalls != []:
                    raise Exception ('Function Call in Condition Processing')
                
                #No Data Found
                CompleteCondition = ''
                for j in range(self.getTable(TableName).getNumberOfRows()):
                    CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, j) + ', '
                
                CompleteCondition = CompleteCondition[:-2]
                PrintLog(CompleteCondition)
                
                self.Current_Choices.AddChoice(CompleteCondition, None)
                    
                #One Row Found
                for j in range(self.getTable(TableName).getNumberOfRows()):
                    CompleteCondition = ''
                    CompleteCondition = CompleteCondition + self.SubstituteTableRow(Condition, TableName, j) + ', '
                    for k in range(self.getTable(TableName).getNumberOfRows()):
                        if (j == k):
                            pass
                        else:
                            CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, k) + ', '
                    
                    CompleteCondition = CompleteCondition[:-2]
                    PrintLog(CompleteCondition)
                    InternalTable, TargetCondition = self.ProcessTargetList(ColList = ColumnList, Rows = [j], Inner = self.Current_Tables[TableName])
                    if TargetCondition != '':
                        CompleteCondition = CompleteCondition + ", " + TargetCondition
                    self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                
                #Two Rows Found
                CompleteCondition = ''
                for j in range(self.getTable(TableName).getNumberOfRows()):
                    ConditionPart1 = CompleteCondition + self.SubstituteTableRow(Condition, TableName, j) + ', '
                    for k in range(j+1, self.getTable(TableName).getNumberOfRows()):
                        CompleteCondition = ConditionPart1 + self.SubstituteTableRow(Condition, TableName, k) + ', '                    
                        for l in range(self.getTable(TableName).getNumberOfRows()):
                            if (l == j or l == k):
                                pass
                            else:
                                CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, l) + ', '
                                
                        CompleteCondition = CompleteCondition[:-2]
                        PrintLog(CompleteCondition)
                        InternalTable, TargetCondition = self.ProcessTargetList(ColList = ColumnList, Rows = [j,k], Inner = self.Current_Tables[TableName])
                        if TargetCondition != '':
                            CompleteCondition = CompleteCondition + ", " + TargetCondition 
                        self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                        CompleteCondition = ''
                
                
            else:
                #all rows selected
                RowCount = self.getTable(TableName).getNumberOfRows()
                if (RowCount > 0):
                    InternalTable, TargetCondition = self.ProcessTargetList(ColList = ColumnList, Rows = range(RowCount), Inner = self.Current_Tables[TableName])
                    if TargetCondition != '':
                        CompleteCondition = CompleteCondition + ", " + TargetCondition
                    self.Current_Choices.AddChoice('True', InternalTable)
                return True
                    
            return False
        
        ######################################################################################################################
        #####################################################  Into  #########################################################
        ###################################################################################################################### 
        elif Parts[0] == 'Into':
            Targets = []
            i = 1
            while i < len(Parts)-1:
                Targets.append(Parts[i])
                i = i+1
            
            ParsedTargets = []
            for Target in Targets:
                TargetParts = Target.split(' ')
                Type = int(TargetParts[0])
                Name = self.CallStackNotoString() + TargetParts[1]
                self.AddNewZ3ObjectForVariable(Name, Type)
                ParsedTargets.append(self.SubstituteVars(' '+Name+' '))

            if not self.isPreviousResultNULL():
                # Now we make the condition to be added
                Condition = ''
                i = 0
                for Target in ParsedTargets:
                    Condition = Condition + Target + ' == ' + "self.State.getZ3ObjectFirstRowColumnFromPreviousResult(" + i.__str__() + ")" + ", "
                    i = i + 1
                Condition = Condition[:-2]
                
                self.Current_Variables[(self.CallStackNotoString() + 'found')] = True
                self.Current_Choices.AddChoice(Condition, None)
            
            else: #previous result is None
                Condition = ''
                i = 0
                for Target in ParsedTargets:
                    Condition = Condition + Target + ' == ' + "self.State.DataHandler.NullValue" + ", "
                    i = i + 1
                Condition = Condition[:-2]
                
                self.Current_Variables[(self.CallStackNotoString() + 'found')] = False
                self.Current_Choices.AddChoice(Condition, None)
                
            return True
        
        ######################################################################################################################
        ##################################################  ASSIGNMENT  ######################################################
        ######################################################################################################################      
        elif Parts[0] == 'PLPGSQL_STMT_ASSIGN':
            Node = Parts[1].split(' ')
            Type = int(Node[0])
            Target = self.CallStackNotoString() + Node[1]

            Expr, _ = self.MakeCondition(Parts, 2, '')
            Expr = self.SubstituteOldVars(' ' + Expr + ' ')
            
            for F in self.TempFunctionCalls:
                F1, Expr = self.SubstituteInFunctionCall(F, Expr)
                self.FunctionCalls.append(F1)
                    
            self.TempFunctionCalls = []
            
            self.AddNewZ3ObjectForVariable(Target, Type)
            Target = self.SubstituteVars(' '+Target+' ')
            Condition = Target + ' == ' + Expr
            PrintLog(Condition)
            self.Current_Choices.AddChoice(Condition, None)
            return True
        
        ######################################################################################################################
        ###############################################  T_Hash or T_Sort  ###################################################
        ######################################################################################################################      
        elif (Parts[0] == 'T_Hash') or (Parts[0] == 'T_Sort'):
            self.Current_Choices.AddChoice('True', self.getPreviousResult())
            return True
        
        ######################################################################################################################
        ####################################  T_HashJoin or T_MergeJoin or T_NestLoop  #######################################
        ######################################################################################################################      
        elif (Parts[0] == 'T_HashJoin') or (Parts[0] == 'T_MergeJoin') or (Parts[0] == 'T_NestLoop'):
            JoinType = Parts[1]
            
            InnerPlanTop = self.Current_State_id - 1
            OuterPlanTop = self.getPlanBottom(InnerPlanTop) - 1
            
            
            if Parts[2] == 'TargetList':
                ColumnList = []
                i = 3
                while (i < len(Parts) and Parts[i] != 'Conditions' and Parts[i] != '') :
                    ColumnList.append(Parts[i])
                    i = i+1
            
            if ((i < len(Parts) and Parts[i] == 'Conditions')):
                
                Condition, i = self.MakeCondition(Parts, i+1, '')
                Condition = self.SubstituteVars(Condition)
                NoDataCond = 'Not('+Condition+')'
                
                InnerResult = self.State[InnerPlanTop]['Results']
                OuterResult = self.State[OuterPlanTop]['Results']
                
                if JoinType == 'JOIN_INNER':
                    if InnerResult == None or OuterResult == None:
                        self.Current_Choices.AddChoice('True', None)
                        return True
                    
                    InnerRows = InnerResult.getNumberOfRows()
                    OuterRows = OuterResult.getNumberOfRows()
                    PrintLog('Inner ' + InnerRows.__str__())
                    PrintLog('Outer ' + OuterRows.__str__())
                    Comb = CombinationGenerator(InnerRows, OuterRows)
                    
                    #No Data Found
                    PrintLog('No data condition')
                    CompleteCondition = ''
                    for RowPair in Comb.getAllSinglePairs():
                        C1 = self.SubstituteInnerResultRow(NoDataCond, InnerPlanTop, RowPair[0])
                        C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, RowPair[1])
                        CompleteCondition = CompleteCondition + C2 + ', '
                    CompleteCondition = CompleteCondition[:-2]
                    PrintLog(CompleteCondition)
                    self.Current_Choices.AddChoice(CompleteCondition, None)
                    
                    #One Row Found
                    PrintLog('One Row Conditions')
                    for RowPair in Comb.getAllSinglePairs():
                        CompleteCondition = ''
                        for R in Comb.getAllSinglePairs():
                            if RowPair == R:                       
                                C1 = self.SubstituteInnerResultRow(Condition, InnerPlanTop, R[0])
                                C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, R[1])
                                CompleteCondition = CompleteCondition + C2 + ', '
                            else:
                                C1 = self.SubstituteInnerResultRow(NoDataCond, InnerPlanTop, R[0])
                                C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, R[1])
                                CompleteCondition = CompleteCondition + C2 + ', '
                        CompleteCondition = CompleteCondition[:-2]
                        PrintLog(CompleteCondition)
                        InternalTable, TargetCondition = self.ProcessTargetList(ColList = ColumnList, Rows = [RowPair], Inner = InnerResult, Outer = OuterResult)
                        if TargetCondition != '':
                            CompleteCondition = CompleteCondition + ", " + TargetCondition
                        self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                    
                    #Two Rows Found
                    PrintLog('Two Row Conditions')
                    for RowComb in Comb.getAllTwoPairCombinations():
                        CompleteCondition = ''
                        for R in Comb.getAllSinglePairs():
                            if (RowComb[0] == R) or (RowComb[1] == R):                       
                                C1 = self.SubstituteInnerResultRow(Condition, InnerPlanTop, R[0])
                                C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, R[1])
                                CompleteCondition = CompleteCondition + C2 + ', '
                            else:
                                C1 = self.SubstituteInnerResultRow(NoDataCond, InnerPlanTop, R[0])
                                C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, R[1])
                                CompleteCondition = CompleteCondition + C2 + ', '
                        CompleteCondition = CompleteCondition[:-2]
                        PrintLog(CompleteCondition)
                        InternalTable, TargetCondition = self.ProcessTargetList(ColList = ColumnList, Rows = RowComb, Inner = InnerResult, Outer = OuterResult)
                        if TargetCondition != '':
                            CompleteCondition = CompleteCondition + ", " + TargetCondition
                        self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                
                else:
                    raise Exception('Join not implemeted '+ JoinType)
            
            else:
                #Cross Join not implemented yet
                raise Exception('Cross Join not implemeted yet')            
            
            return False
        
        ######################################################################################################################
        ##################################################  T_Result   #######################################################
        ######################################################################################################################
        elif (Parts[0] == 'T_Result'):
            if self.Current_State_id == 1:
                self.Current_Choices.AddChoice('True', None)
                return True
            
            else:
            
                ColumnList = []
                if Parts[1] == 'TargetList':
                    i = 2
                    while (i < len(Parts) and Parts[i] != 'Conditions' and Parts[i] != '') :                        
                        ColumnList.append(Parts[i])
                        i = i+1
                                       
                T, TargetCondition = self.ProcessTargetList(ColList = ColumnList)
                if TargetCondition != '':
                    self.Current_Choices.AddChoice(TargetCondition, T)
                    return True
                
            self.Current_Choices.AddChoice('True', T)
            return True
        
        ######################################################################################################################
        ###############################################  T_ModifyTable   #####################################################
        ######################################################################################################################
        elif (Parts[0] == 'T_ModifyTable'):
            PrevResult = self.getPreviousResult()
            TableName = Parts[2]
            
            self.State[self.Current_State_id]['IgnoreNodes'] = True
            
            if PrevResult != None:
                self.Current_Variables[(self.CallStackNotoString() + 'found')] = True
            
                if Parts[1] == 'CMD_INSERT':    
                    self.getTable(TableName).AddRowsFromTable(PrevResult)
                    Condition = self.AddConstraints('', TableName)
                    NotCondition = 'Not(And('+Condition+'))'
                    self.Current_Choices.AddChoice(Condition, None)
                    self.Current_Choices.AddChoice(NotCondition, None)
                    return False
                    
                elif Parts[1] == 'CMD_UPDATE':
                    self.getTable(TableName).UpdateRowsFromTable(PrevResult)
                    Condition = self.AddConstraints('', TableName)
                    NotCondition = 'Not(And('+Condition+'))'
                    self.Current_Choices.AddChoice(Condition, None)
                    self.Current_Choices.AddChoice(NotCondition, None)
                    return False
                
                elif Parts[1] == 'CMD_DELETE':
                    self.getTable(TableName).DeleteRowsInTable(PrevResult)
                    self.Current_Choices.AddChoice('True', None)
                    return True
                
            else:
                self.Current_Variables[(self.CallStackNotoString() + 'found')] = False
                self.Current_Choices.AddChoice('True', None)
                return True                
        
        ######################################################################################################################
        #############################################  PLPGSQL_STMT_RETURN   #################################################
        ######################################################################################################################
        elif Parts[0] == 'PLPGSQL_STMT_RETURN':
            # Not doing much for retun type yet. It will be handled when we work on sub procedure calls
                                   
            Node = Parts[1].split(' ')
            T = Table('Result' + self.Current_State_id.__str__(),self.DataHandler, False, False);
            TableRows = []
            Row = []
            
            self.State[self.Current_State_id]['CallStack'][-1]['ReturnStateID'] = self.Current_State_id
            
            if Node[0] == 'Param':
                Row.append(self.getZ3ObjectFromName(self.CallStackNotoString() + Node[2]))
                Condition = 'True'
                
            elif (Node[0] == 'FunctionCall') or (getProcedureReturnType(Node[0]) != None) :
                ResultName = self.CallStackNotoString() + T.getName()
                
                if Node[0] == 'FunctionCall':
                    Type = getProcedureReturnType(Node[1])
                else:
                    Type = getProcedureReturnType(Node[0])
                    
                Row.append(self.DataHandler.getZ3Object(Type, ResultName))
                
                Expr , _ = self.MakeCondition(Parts,1 , '')
                Expr = self.SubstituteOldVars(' ' + Expr + ' ')
                
                for FunctionCall in self.TempFunctionCalls:
                    ReturnVariableName = FunctionCall['ReturnVariableName']
                    ReturnType = FunctionCall['ReturnType']
                    self.Types[ReturnVariableName] = ReturnType
                    self.State[self.Current_State_id]['Variables'][ReturnVariableName] = self.DataHandler.getZ3Object(ReturnType, ReturnVariableName)
                    Expr = Expr.replace(' ' + ReturnVariableName + ' ', " self.State.getZ3ObjectFromName('" + ReturnVariableName + "') ")
                    
                    CallCondition = FunctionCall['CallCondition']
                    for FunctionArg in FunctionCall['FunctionArgNames']:
                        ArgName = FunctionArg[1]
                        ArgType = FunctionArg[0]
                        self.Types[ArgName] = FunctionArg[0]
                        self.State[self.Current_State_id]['Variables'][ArgName] = self.DataHandler.getZ3Object(ArgType, ArgName)
                        CallCondition = CallCondition.replace(' ' + FunctionArg[1] + ' ', " self.State.getZ3ObjectFromName('" + ArgName + "') ")
                        
                    CallCondition = self.SubstituteVars(CallCondition)   
                    FunctionCall['CallCondition'] = CallCondition
                    
                    self.FunctionCalls.append(FunctionCall) 
                
                self.TempFunctionCalls = []
                
                
                Condition = "self.State.getZ3ObjectForResultElement( " + self.Current_State_id.__str__() + " , " + (0).__str__() + " , " + (0).__str__() +" )" + ' == ' + Expr
                
                
            else:   # Node is a constant
                Type = int(Node[0])
                Value = Node[1]
                Row.append( self.DataHandler.ProcessConstant(Type, Value) )
                Condition = 'True'
            
            TableRows.append(Row)    
            T.setRows(TableRows)        
            self.Current_Choices.AddChoice(Condition, T)
            return False
        
        ######################################################################################################################
        ##############################################  PLPGSQL_STMT_RAISE   #################################################
        ######################################################################################################################
        elif Parts[0] == 'PLPGSQL_STMT_RAISE':
            # Not doing much here yet. May need to work on this but that is unlikely
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        #############################################  PLPGSQL_STMT_EXECSQL   ################################################
        ######################################################################################################################
        elif Parts[0] == 'PLPGSQL_STMT_EXECSQL':
            # Indicates Start of and SQL Statment Execution. May be helpful in some cases 
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        ###########################################  PLPGSQL_STMT_EXECSQL_END  ###############################################
        ######################################################################################################################        
        elif Parts[0] == 'PLPGSQL_STMT_EXECSQL_END':
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        ##############################################  PLPGSQL_STMT_FORS   ##################################################
        ######################################################################################################################
        elif Parts[0] == 'PLPGSQL_STMT_FORS':
            # ResultName may have to be extrated. May have add loop starting stuff.
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        ############################################  PLPGSQL_STMT_FORS_END   ################################################
        ######################################################################################################################
        elif Parts[0] == 'PLPGSQL_STMT_FORS_END':
            self.State[self.Current_State_id]['Loops'].pop()
            
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        ######################################  PLPGSQL_STMT_FORS_QUERY_COMPLETE   ###########################################
        ######################################################################################################################
        
        elif Parts[0] == 'PLPGSQL_STMT_FORS_QUERY_COMPLETE':
            Node = Parts[1].split(' ')
            Name = Node[1]
            
            Loop = {}
            Loop['Type'] = 'FORS'
            Loop['SELECT_RESULT'] = self.getPreviousResult()
            Loop['TargetVariableName'] = self.CallStackNotoString() + Name
            Loop['LoadedResultIndex'] = None
            
            if Loop['SELECT_RESULT'] == None:
                self.Current_Variables[(self.CallStackNotoString() + 'found')] = False
            else:
                self.Current_Variables[(self.CallStackNotoString() + 'found')] = True
            
            self.State[self.Current_State_id]['Loops'].append(Loop)
            
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        ########################################  PLPGSQL_STMT_FORS_LOOP_START   #############################################
        ######################################################################################################################
        
        elif Parts[0] == 'PLPGSQL_STMT_FORS_LOOP_START':
            Loop = self.State[self.Current_State_id]['Loops'][-1]
            TargetName = Loop['TargetVariableName']
            
            RowIndexToLoad = Loop['LoadedResultIndex']
            if RowIndexToLoad == None:
                RowIndexToLoad = 0
            else:
                RowIndexToLoad = RowIndexToLoad + 1
            # ideally the system should never come here if there are 
            # no more rows left so not handling overflow case here
            
            QueryResult = Loop['SELECT_RESULT']
            
            for ColumnIndex in range(QueryResult.getNumberOfCols()):
                Name = TargetName + '.' + QueryResult.getColumnNameFromIndex(ColumnIndex)
                self.Current_Variables[Name] = QueryResult.getZ3ObjectForTableElement(ColumnIndex, RowIndexToLoad)            
            
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        #########################################  PLPGSQL_STMT_FORS_LOOP_END   ##############################################
        ######################################################################################################################
        elif Parts[0] == 'PLPGSQL_STMT_FORS_LOOP_END':
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        ##############################################  PLPGSQL_STMT_LOOP  ###################################################
        ######################################################################################################################
#         elif Parts[0] == 'PLPGSQL_STMT_LOOP':
#             # Loop statement is really nothing till we reach the exit statement
#             self.Current_Choices.AddChoice('True', None)
#             return True
                
        
        ######################################################################################################################
        ###############################################  START_FUNCTION   ####################################################
        ######################################################################################################################
        
        elif Parts[0] == 'START_FUNCTION':
            if self.Current_State_id in [1, 2]:
                
                FunctionCall = {}
                FunctionCall['FunctionID'] = Parts[1]
                FunctionCall['CallCondition'] = ''
                FunctionCall['ReturnVariableName'] = ''
                FunctionCall['ReturnType'] = ''
                FunctionCall['ReturnStateID'] = None
                FunctionCall['Call_ID'] = 0
                FunctionCall['FunctionArgNames'] = None
                
                self.State[self.Current_State_id]['CallStack'].append(FunctionCall)
                
                self.Current_Choices.AddChoice('True', None)
                return True
            else:
                if self.State[self.Current_State_id]['CallStack'].__len__() >= MaximumStackDepth:
                    #Clear Log
                    PrintLog('Maximum Stack depth reached. Clearing log.')
                    LogFile = open(TraceFile, 'w')
                    LogFile.close()
                    self.Current_Choices.AddChoice('False', None)
                    raise Exception("Symbolic Executor: Maximum Stack Depth Reached")
                
                FunctionCall = None
                for F in self.FunctionCalls:
                    if F['FunctionID'] == Parts[1]:
                        FunctionCall = F
                        break
                self.FunctionCalls.remove(FunctionCall)
                self.State[self.Current_State_id]['CallStack'].append(FunctionCall)
                
                CallCondition = FunctionCall['CallCondition']
                
                self.State[self.Current_State_id]['Call_ID'] = FunctionCall['Call_ID']    
                self.State[self.Current_State_id]['Variables'][(self.CallStackNotoString() + 'found')] = False
                
                self.Current_Choices.AddChoice(CallCondition, None)
                return True
        
        ######################################################################################################################
        ################################################  END_FUNCTION   #####################################################
        ######################################################################################################################
        
        elif Parts[0] == 'END_FUNCTION':
            if self.State[self.Current_State_id]['CallStack'].__len__() == 1:
                # End
                self.Current_Choices.AddChoice('True', None)
                return False
            else:
                FunctionCall = self.State[self.Current_State_id]['CallStack'].pop()
                ReturnVariableName = FunctionCall['ReturnVariableName']
                ReturnStateID = FunctionCall['ReturnStateID']
                
                #set call id to returning function call id
                self.State[self.Current_State_id]['Call_ID'] = self.State[self.Current_State_id]['CallStack'][-1]['Call_ID']
                
                Condition = ' ' + ReturnVariableName + ' '
                Condition = self.SubstituteVars(Condition)
                Condition = Condition + ' == self.State.getZ3ObjectForResultElement( + ' + ReturnStateID.__str__() + ' , 0, 0)'
                
                T = Table('Result' + self.Current_State_id.__str__(),self.DataHandler, False, False);
                TableRows = []
                Row = []
                Row.append(self.Current_Variables[ReturnVariableName])
                TableRows.append(Row)
                T.setRows(TableRows)
                
                self.Current_Choices.AddChoice(Condition, T)
                return True

        ######################################################################################################################
        ##################################################  Blank Line  ######################################################
        ######################################################################################################################
        elif Parts[0] == '':
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        ##############################################  COMPLEX_CONDITION  ###################################################
        ######################################################################################################################
        elif Parts[0] == 'COMPLEX_CONDITION':
            self.Current_Choices.AddChoice('True', None)
            return True
        
        ######################################################################################################################
        ########################################  Invalid OR Unimplemented Node   ############################################
        ######################################################################################################################
        else:
            raise Exception('Unkown Node ' + Parts[0])