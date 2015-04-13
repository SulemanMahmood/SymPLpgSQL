from z3 import Int
from Table import Table
from ChoicesClass import ChoicesClass
from CombinationGenerater import CombinationGenerator
from Z3Solver import getZ3Object

class StateClass:    
    
    def __init__(self, Procedure):   
        self.Current_State_id = 0
        self.PreviousChoice_State_ID = 0
        
        self.State = {}
        self.State[self.Current_State_id] = {}
        self.State[self.Current_State_id]['Variables'] = {}
        self.State[self.Current_State_id]['Tables'] = {}
        self.State[self.Current_State_id]['Choices'] = ChoicesClass()
        #self.State[self.Current_State_id]['Results']     Added Later
        #self.State[self.Current_State_id]['Node']        Added Later
        
        self.Types = {}
        self.Current_Variables = {}
        self.Current_Tables = {}
        #self.Current_Choices        added later in current state setup
        #self.Current_Results        added later in Next Choice Function. Maybe useless.
         
        for Arg in Procedure.getArgList():
            self.SetupVariable(Arg)
             
        #Initialize Current State
        self.Set_Current_State()      
        
    def SetupVariable(self, In):
        Type = In[0]
        Name = In[1]
        
        self.Types[Name] = Type            
        self.State[self.Current_State_id]['Variables'][Name] = getZ3Object(Type, Name)    
                
    def AddNewZ3ObjectForVariable(self,Name, Type):
        NewName = Name + "_" + self.Current_State_id.__str__()
        self.State[self.Current_State_id]['Variables'][Name] = getZ3Object(Type, NewName)
    
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
        return self.State[0]['Variables'][Name]
        
    def getZ3ObjectFromName(self,Name):
        return self.State[self.Current_State_id]['Variables'][Name]
    
    def getOldZ3ObjectFromName(self,Name):
        return self.State[self.Current_State_id-1]['Variables'][Name]

    def getTypeFromNameForTestCase(self,Name):
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
        for k, v in self.Current_Variables.items():
            Condition = Condition.replace(' '+k+' ', " self.State.getZ3ObjectFromName('"+k+"') ")
            Condition = Condition.replace('('+k+' ', "(self.State.getZ3ObjectFromName('"+k+"') ")
            Condition = Condition.replace(' '+k+')', " self.State.getZ3ObjectFromName('"+k+"'))")
            Condition = Condition.replace('('+k+')', "(self.State.getZ3ObjectFromName('"+k+"'))")
        return Condition
            
    def SubstituteOldVars(self,Condition):
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
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' == '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == '>':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' > '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == '<':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' > '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == '>=':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' >= '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == '<=':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' <= '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == '+':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' + '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == '-':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' - '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == '*':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' * '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == '/':
            Condition, i = self.MakeCondition(Parts, i+1, Condition + '( ')
            Condition = Condition + ' / '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        elif Parts[i] == 'Not':
            Condition = Condition + 'Not( '
            Condition, i = self.MakeCondition(Parts, i+1, Condition)
            return Condition + ' )', i+1
        
        else:
            Node = Parts[i].split(' ')
            if len(Node) == 1:
                raise Exception('Unkown Operator')
            else:
                if Node[0] == 'Col':
                    Condition = Condition + Node[1]
                elif Node[0] == 'Param':
                    Condition = Condition + Node[1]
                else:
                    Type = int(Node[0])
                    if (Type >= 20 and Type <= 23 ):   # Integer type
                        Condition = Condition + Node[1]
                    else:
                        raise Exception('Unknown Data Type In Expression Processing')
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
    
    def AddConstraints(self, Condition, TableName):
        #Primary Key Constraint
        Rows = self.getNumberOfRows(TableName)
        for i in range(Rows):
            for j in range(i+1,Rows):
                for k in self.getPKColumnsForTestCase(TableName):
                    Condition = Condition + "self.State.getZ3ObjectForTableElement('"+TableName+"', "+k.__str__()+", "+i.__str__()+")" + " != " + "self.State.getZ3ObjectForTableElement('"+TableName+"', "+k.__str__()+", "+j.__str__()+")" + ", "
        
        return Condition
    
    def getNumberOfRows(self, TableName):
        return self.Current_Tables[TableName].getNumberOfRows()

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
    
    def ProcessTargetList(self, ColList, Rows = None, Inner = None, Outer = None):
        TableRows = []
        if Rows == None:
            TableRows.append([])
        else:
            for i in range(len(Rows)):
                TableRows.append([])
                
        T = Table('Result' + self.Current_State_id.__str__(), False, False);
        
        for row in range(len(TableRows)):
            for Col in range(len(ColList)):
                Parts = ColList[Col].split(' ')
                JoinParts = Parts[1].split('.')
                
                if Parts[0] == 'Col':
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
                        ColIndex = Inner.getColumnIndexFromName(Parts[1])
                        InnerRow = Rows[row]
                        TableRows[row].append(Inner.getZ3ObjectForTableElement(ColIndex, InnerRow))
                        
                elif Parts[0] == 'Param':
                    if self.Current_Variables.__contains__(Parts[1]):
                        TableRows[row].append(self.Current_Variables[Parts[1]])
                
                else:
                    Type = int(Parts[0])
                    Value = Parts[1]
                    
                    if (Type >= 20 and Type <= 23 ):   # Integer type
                        TableRows[row].append(int(Value))
                    else:
                        raise Exception('Unknown Constant Type')
                    
        T.setRows(TableRows)
        return T;
    
    def getTable(self, TableName):
        if self.Current_Tables.__contains__(TableName):
            return self.Current_Tables[TableName]
        else:
            return self.AddNewTable(TableName)
        
    def AddNewTable(self, TableName):
        T = Table(TableName)
        for state in range(self.Current_State_id + 1):
            T1 = T.Copy()
            self.State[state]['Tables'][TableName] = T1
        return self.Current_Tables[TableName]
    
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
            Condition, i = self.MakeCondition(Parts,1,'')
            print(Condition)
            Condition = self.SubstituteVars(Condition)
               
            self.Current_Choices.AddChoice(Condition, None)
            self.Current_Choices.AddChoice('Not('+Condition+')', None)
            return True
            
        ######################################################################################################################
        ###########################################  T_SeqScan & T_IndexScan  ################################################
        ######################################################################################################################        
        elif Parts[0] == 'T_SeqScan' or Parts[0] == 'T_IndexScan':
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

                print(Condition)
                
                #No Data Found
                CompleteCondition = ''
                for j in range(self.getTable(TableName).getNumberOfRows()):
                    CompleteCondition = CompleteCondition + self.SubstituteTableRow(NoDataCond, TableName, j) + ', '
                
                CompleteCondition = CompleteCondition[:-2]
                print(CompleteCondition)
                
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
                    print(CompleteCondition)
                    InternalTable = self.ProcessTargetList(ColList = ColumnList, Rows = [j], Inner = self.Current_Tables[TableName])
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
                        print(CompleteCondition)
                        InternalTable = self.ProcessTargetList(ColList = ColumnList, Rows = [j,k], Inner = self.Current_Tables[TableName]) 
                        self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                        CompleteCondition = ''
                
                
            else:
                #all rows selected
                RowCount = self.getTable(TableName).getNumberOfRows()
                if (RowCount > 0):
                    InternalTable = self.ProcessTargetList(ColList = ColumnList, Rows = range(RowCount), Inner = self.Current_Tables[TableName])
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
                    TargetParts = Target.split(' ')
                    Type = int(TargetParts[0])
                    Name = TargetParts[1]
                    self.AddNewZ3ObjectForVariable(Name, Type)
                    ParsedTargets.append(self.SubstituteVars(' '+Name+' '))
                
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
            ReturnType = int(Parts[2])

            Expr, i = self.MakeCondition(Parts, 3, '')
            Expr = self.SubstituteOldVars(' ' + Expr + ' ')
            
            self.AddNewZ3ObjectForVariable(Target, ReturnType)
            Target = self.SubstituteVars(' '+Target+' ')
            Condition = Target + ' == ' + Expr
            print(Condition)
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
                    print('Inner ' + InnerRows.__str__())
                    print('Outer ' + OuterRows.__str__())
                    Comb = CombinationGenerator(InnerRows, OuterRows)
                    
                    #No Data Found
                    print('No data condition')
                    CompleteCondition = ''
                    for RowPair in Comb.getAllSinglePairs():
                        C1 = self.SubstituteInnerResultRow(NoDataCond, InnerPlanTop, RowPair[0])
                        C2 = self.SubstituteOuterResultRow(C1, OuterPlanTop, RowPair[1])
                        CompleteCondition = CompleteCondition + C2 + ', '
                    CompleteCondition = CompleteCondition[:-2]
                    print(CompleteCondition)
                    self.Current_Choices.AddChoice(CompleteCondition, None)
                    
                    #One Row Found
                    print('One Row Conditions')
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
                        print(CompleteCondition)
                        InternalTable = self.ProcessTargetList(ColList = ColumnList, Rows = [RowPair], Inner = InnerResult, Outer = OuterResult)
                        self.Current_Choices.AddChoice(CompleteCondition, InternalTable)
                    
                    #Two Rows Found
                    print('Two Row Conditions')
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
                        print(CompleteCondition)
                        InternalTable = self.ProcessTargetList(ColList = ColumnList, Rows = RowComb, Inner = InnerResult, Outer = OuterResult)
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
            ColumnList = []
            if Parts[1] == 'TargetList':
                i = 2
                while (i < len(Parts) and Parts[i] != 'Conditions' and Parts[i] != '') :
                    if Parts[i] == 'FunctionCall':
                        if self.Current_State_id == 1:
                            self.Current_Choices.AddChoice('True', None)
                            return True
                        else:
                            raise Exception('Sub Procedure Call')
                    else: 
                        ColumnList.append(Parts[i])
                        i = i+1
                                   
            T = self.ProcessTargetList(ColList = ColumnList)
            
            self.Current_Choices.AddChoice('True', T)
            return True
        
        ######################################################################################################################
        ###############################################  T_ModifyTable   #####################################################
        ######################################################################################################################
        elif (Parts[0] == 'T_ModifyTable'):
            PrevResult = self.getPreviousResult()
            TableName = Parts[2]
            
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
        
        ######################################################################################################################
        ########################################  Invalid OR Unimplemented Node   ############################################
        ######################################################################################################################
        else:
            raise Exception('Unkown Node ' + Parts[1])