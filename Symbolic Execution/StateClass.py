from z3 import Int
from Table import Table
from ChoicesClass import ChoicesClass

class StateClass:    
    
    def __init__(self, proc_name):   
        self.Current_State_id = 0
        self.PreviousChoice_State_ID = 0
        
        self.Types = {}
        self.Alaises = {}
        
        self.State = {}
        self.State[self.Current_State_id] = {}
        self.State[self.Current_State_id]['Variables'] = {}
        self.State[self.Current_State_id]['Tables'] = {}
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
        #self.State[self.Current_State_id]['Results']     Added Later
        #self.State[self.Current_State_id]['Node']        Added Later
        
        self.Current_Variables = {}
        self.Current_Tables = {}
        #self.Current_Choices        added later in current state setup
        #self.Current_Results        added later in Next Choice Function. Maybe useless.
         
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
            if Tablename[-1] == '\n':
                Tablename = Tablename[:-1] 
            if not (self.State[self.Current_State_id]['Tables'].__contains__(Tablename)):
                self.State[self.Current_State_id]['Tables'][Tablename] = Table(Tablename, True)
                     
        Details.close
        
        #Initialize Current State
        self.Set_Current_State()      
        
    def SetupVariable(self, In):    #Works only for State 0
        Type = In[0]
        Name = In[1]
        
        self.Types[Name] = Type
        
        if (len(In) > 2):
            Alais = In[2]
            self.Alaises[Alais] = Name
                    
        self.State[self.Current_State_id]['Variables'][Name] = self.getZ3Object(Type, Name)
        
        
    def getZ3Object(self, Type, Name):
        if (Type == 'Int'):
            return Int(Name)
            
        elif (Type == 'String'):
            pass
        
        elif (Type == 'Date'):
            pass    
                
    def AddNewZ3ObjectForVariable(self,Name):
        if self.Alaises.__contains__(Name):
            Name = self.Alaises[Name]
        Type = self.Types[Name]
        NewName = Name + self.Current_State_id.__str__()
        
        self.State[self.Current_State_id]['Variables'][Name] = self.getZ3Object(Type, NewName)
        
    
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
    
    def getOldZ3ObjectFromName(self,Name):
        if self.Alaises.__contains__(Name):
            return self.State[self.Current_State_id-1]['Variables'][self.Alaises[Name]]
        else:
            return self.State[self.Current_State_id-1]['Variables'][Name]

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
        self.State[self.Current_State_id]['Variables'] = {}
        self.State[self.Current_State_id]['Tables'] = {}
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
        
        for K in self.State[Old_State_id]['Variables']:
            self.State[self.Current_State_id]['Variables'][K] = self.State[Old_State_id]['Variables'][K]
            
        for K in self.State[Old_State_id]['Tables']:
            self.State[self.Current_State_id]['Tables'][K] = self.State[Old_State_id]['Tables'][K].Copy()
            
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
            
        self.Set_Current_State()
        
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
            
    def SubstituteOldVars(self,Condition):
        for k, v in self.Alaises.items():
            Condition = Condition.replace(' '+k+' ', ' '+self.Alaises[k]+' ')
            Condition = Condition.replace('('+k+' ', '('+self.Alaises[k]+' ')
            Condition = Condition.replace(' '+k+')', ' '+self.Alaises[k]+')')
            Condition = Condition.replace('('+k+')', '('+self.Alaises[k]+')')
        
        for k, v in self.Current_Variables.items():
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
    
    def MakeCondition(self,Parts,i,Condition):
        if Parts[i] == '=':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '(')
            Condition = Condition + ' == '
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
        Table = self.Current_Tables[TableName]
        for Name in Table.getColumnNameList():
            Condition = Condition.replace(' '+Name+' ', " self.State.getZ3ObjectForTableElement('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+") ")
            Condition = Condition.replace('('+Name+' ', "(self.State.getZ3ObjectForTableElement('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+") ")
            Condition = Condition.replace(' '+Name+')', " self.State.getZ3ObjectForTableElement('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+"))")
            Condition = Condition.replace('('+Name+')', "(self.State.getZ3ObjectForTableElement('"+TableName+"', " + Table.getColumnIndexFromName(Name).__str__() + ", " +RowNum.__str__()+"))")
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
        #Primary Key Constraint
        Rows = self.getNumberOfRowsForTestCase(TableName)
        for i in range(Rows):
            for j in range(i+1,Rows):
                for k in self.getPKColumnsForTestCase(TableName):
                    Condition = Condition + "self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', "+k.__str__()+", "+i.__str__()+")" + " != " + "self.State.getZ3ObjectForTableElementForTestCase('"+TableName+"', "+k.__str__()+", "+j.__str__()+")" + ", "
        
        return Condition

    def AddAllBaseConditionsForTestCase(self, BaseConstraint):
        for table in self.getTableListForTestCase():
            BaseConstraint = self.AddConstraintsForTestCase(BaseConstraint, table)
        return BaseConstraint[:-2]
    
    def getPlanBottom(self,State_ID):
        NodeName = self.State[State_ID]['Node']
        if NodeName == 'T_SeqScan':
            return State_ID
        elif NodeName == 'T_Hash' or NodeName == 'T_Sort':
            return self.getPlanBottom(State_ID - 1)
        elif NodeName == 'T_HashJoin' or NodeName == 'T_MergeJoin':
            return self.getPlanBottom( self.getPlanBottom(State_ID - 1) - 1 )
    
    def MakeJoinResult(self, Inner, Outer, RowJoins, TargetList):
        T = Table('Result', False, False);
        T.CopyRowsForJoin(Inner, Outer, RowJoins, TargetList)
    
    def ProcessLine(self,Line):
        self.AdvanceState()
        Parts = Line.split('\t')
        self.State[self.Current_State_id]['Node'] = Parts[0]
        print(Parts)
        # Here we interpret our instrumentation
        ######################################################################################################################
        ####################################################   IF   ##########################################################
        ######################################################################################################################
        if Parts[0] == 'IF':    
            Condition = Parts[1]
            Condition = self.SubstituteVars(Condition)
               
            self.Current_Choices.AddChoice(Condition, None)
            self.Current_Choices.AddChoice('Not('+Condition+')', None)
            return True
            
        ######################################################################################################################
        ##################################################  T_SeqScan   ######################################################
        ######################################################################################################################        
        elif Parts[0] == 'T_SeqScan':
            TableName = Parts[1]
            
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
                
                #print(Condition)
                
                #No Data Found
                CompleteCondition = ''
                for j in range(self.Current_Tables[TableName].getNumberOfRows()):
                    CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, j) + ', '
                
                CompleteCondition = CompleteCondition[:-2]
                print(CompleteCondition)
                
                self.Current_Choices.AddChoice(CompleteCondition, None)
                    
                #One Row Found
                for j in range(self.Current_Tables[TableName].getNumberOfRows()):
                    CompleteCondition = ''
                    CompleteCondition = CompleteCondition + self.SubstituteTableRow(Condition, TableName, j) + ', '
                    for k in range(self.Current_Tables[TableName].getNumberOfRows()):
                        if (j == k):
                            pass
                        else:
                            CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, k) + ', '
                    
                    CompleteCondition = CompleteCondition[:-2]
                    print(CompleteCondition)
                    
                    InternalTable = self.Current_Tables[TableName].CreateSelectiveCopy(ColumnList,[j])
                    self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                
                #Two Rows Found
                CompleteCondition = ''
                for j in range(self.Current_Tables[TableName].getNumberOfRows()):
                    ConditionPart1 = CompleteCondition + self.SubstituteTableRow(Condition, TableName, j) + ', '
                    for k in range(j+1, self.Current_Tables[TableName].getNumberOfRows()):
                        CompleteCondition = ConditionPart1 + self.SubstituteTableRow(Condition, TableName, k) + ', '                    
                        for l in range(self.Current_Tables[TableName].getNumberOfRows()):
                            if (l == j or l == k):
                                pass
                            else:
                                CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, l) + ', '
                                
                        CompleteCondition = CompleteCondition[:-2]
                        print(CompleteCondition)
                        InternalTable = self.Current_Tables[TableName].CreateSelectiveCopy(ColumnList,[j,k])
                        self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                        CompleteCondition = ''
                
                
            else:
                #all rows selected
                RowCount = self.Current_Tables[TableName].getNumberOfRows()
                if (RowCount > 0):
                    InternalTable = self.Current_Tables[TableName].CreateSelectiveCopy(ColumnList,range(RowCount))
                    self.Current_Choices.AddChoice('True', InternalTable)
                return True
                    
            return False
        
        ######################################################################################################################
        #####################################################  Into  #########################################################
        ###################################################################################################################### 
        elif Parts[0] == 'Into':
            if not self.isPreviousResultNULL():
                Targets = []
                i = 1
                while i < len(Parts)-1:
                    Targets.append(Parts[i])
                    i = i+1
                
                ParsedTargets = []
                for Target in Targets:
                    self.AddNewZ3ObjectForVariable(Target)
                    ParsedTargets.append(self.SubstituteVars(' '+Target+' '))
                
                # Now we make the condition to be added
                Condition = ''
                i = 0
                for Target in ParsedTargets:
                    Condition = Condition + Target + ' == ' + "self.State.getZ3ObjectFirstRowColumnFromPreviousResult(" + i.__str__() + ")" + ", "
                    i = i + 1
                Condition = Condition[:-2]
                
                self.Current_Choices.AddChoice(Condition, None)
                
            return True
        
        ######################################################################################################################
        ##################################################  ASSIGNMENT  ######################################################
        ######################################################################################################################      
        elif Parts[0] == 'ASSIGNMENT':
            Target = Parts[1]
            Expr = Parts[2]
            
            Expr = self.SubstituteOldVars(' ' + Expr + ' ')
            
            self.AddNewZ3ObjectForVariable(Target)
            Target = self.SubstituteVars(' '+Target+' ')
            Condition = Target + ' == ' + Expr
            self.Current_Choices.AddChoice(Condition, None)
            return True
        
        ######################################################################################################################
        ###############################################  T_Hash or T_Sort  ###################################################
        ######################################################################################################################      
        elif (Parts[0] == 'T_Hash') or (Parts[0] == 'T_Sort'):
            self.Current_Choices.AddChoice('True', self.getPreviousResult())
            return True
        
        ######################################################################################################################
        ###########################################  T_HashJoin or T_MergeJoin ###############################################
        ######################################################################################################################      
        elif (Parts[0] == 'T_HashJoin') or (Parts[0] == 'T_MergeJoin'):
            JoinType = Parts[1]
            
            InnerPlanTop = self.Current_State_id - 1
            OuterPlanTop = self.getPlanBottom(InnerPlanTop) - 1
            
            
            if Parts[2] == 'TargetList':
                ColumnList = []
                i = 3
                while (i < len(Parts) and Parts[i] != 'Conditions' and Parts[i] != '') :
                    col = Parts[i].split('.')
                    ColumnList.append([col[0], col[1]])
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
                    
                    #No Data Found
                    CompleteCondition = ''
                    for j in range(InnerResult.getNumberOfRows()):
                        for k in range(OuterResult.getNumberOfRows()):
                            C1 = self.SubstituteInnerResultRow(NoDataCond, InnerPlanTop, j)
                            C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, k)
                            CompleteCondition = CompleteCondition + C2 + ', '
                    CompleteCondition = CompleteCondition[:-2]
                    print(CompleteCondition)
                    self.Current_Choices.AddChoice(CompleteCondition, None)
                    
                    #One Row Found
                    for j in range(InnerResult.getNumberOfRows()):
                        for k in range(OuterResult.getNumberOfRows()):
                            CompleteCondition = ''
                            C1 = self.SubstituteInnerResultRow(Condition, InnerPlanTop, j)
                            C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, k)
                            CompleteCondition = CompleteCondition + C2 + ', '
                            for l in range(OuterResult.getNumberOfRows()):
                                if (l == k):
                                    pass
                                else:
                                    C1 = self.SubstituteInnerResultRow(NoDataCond, InnerPlanTop, j)
                                    C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, l)
                                    CompleteCondition = CompleteCondition + C2 + ', '
                            CompleteCondition = CompleteCondition[:-2]
                            print(CompleteCondition)
                            InternalTable = self.MakeJoinResult(InnerResult, OuterResult, [[j, k]], ColumnList)
                            self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                    
                    #Two Rows Found
                    print('Inner ' + InnerResult.getNumberOfRows().__str__())
                    print('Outer ' + OuterResult.getNumberOfRows().__str__())
                    for j in range(InnerResult.getNumberOfRows()):
                        for k in range(OuterResult.getNumberOfRows()):
                            for l in range(k+1, OuterResult.getNumberOfRows()):
                                CompleteCondition = ''
                                C1 = self.SubstituteInnerResultRow(Condition, InnerPlanTop, j)
                                C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, k)
                                CompleteCondition = CompleteCondition + C2 + ', '
                                C1 = self.SubstituteInnerResultRow(Condition, InnerPlanTop, j)
                                C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, l)
                                CompleteCondition = CompleteCondition + C2 + ', '
                                for m in range(OuterResult.getNumberOfRows()):
                                    if (m == k or m == l):
                                        pass
                                    else:
                                        C1 = self.SubstituteInnerResultRow(NoDataCond, InnerPlanTop, j)
                                        C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, m)
                                        CompleteCondition = CompleteCondition + C2 + ', '
                                CompleteCondition = CompleteCondition[:-2]
                                print(CompleteCondition)
                                InternalTable = self.MakeJoinResult(InnerResult, OuterResult, [[j, k], [j, l]], ColumnList)
                                self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                    
                    print('Section 2')            
                    for j in range(OuterResult.getNumberOfRows()):
                        for k in range(InnerResult.getNumberOfRows()):
                            for l in range(k+1, InnerResult.getNumberOfRows()):
                                CompleteCondition = ''
                                C1 = self.SubstituteInnerResultRow(Condition, OuterPlanTop, j)
                                C2 = self.SubstituteOuterResultRow(C1, InnerPlanTop, k)
                                CompleteCondition = CompleteCondition + C2 + ', '
                                C1 = self.SubstituteInnerResultRow(Condition, OuterPlanTop, j)
                                C2 = self.SubstituteOuterResultRow(C1, InnerPlanTop, l)
                                CompleteCondition = CompleteCondition + C2 + ', '
                                for m in range(InnerResult.getNumberOfRows()):
                                    if (m == k or m == l):
                                        pass
                                    else:
                                        C1 = self.SubstituteInnerResultRow(NoDataCond, OuterPlanTop, j)
                                        C2 = self.SubstituteOuterResultRow(C1, InnerPlanTop, m)
                                        CompleteCondition = CompleteCondition + C2 + ', '
                                CompleteCondition = CompleteCondition[:-2]
                                print(CompleteCondition)
                                InternalTable = self.MakeJoinResult(InnerResult, OuterResult, [[k, j], [l, j]], ColumnList)
                                self.Current_Choices.AddChoice(CompleteCondition, InternalTable)    
                
            else:
                #Cross Join
                RowCount = self.Current_Tables[TableName].getNumberOfRows()
                if (RowCount > 0):
                    InternalTable = self.Current_Tables[TableName].CreateSelectiveCopy(ColumnList,range(RowCount))
                    self.Current_Choices.AddChoice('True', InternalTable)
            
            return False
        
        ######################################################################################################################
        ########################################  Invalid OR Unimplemented Node   ############################################
        ######################################################################################################################
        else:
            print('unknown node')
            self.Current_Choices.AddChoice('True', None)
            return True