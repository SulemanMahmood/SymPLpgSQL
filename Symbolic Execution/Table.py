from z3 import *
from Config import *
import psycopg2

class Table:
    TableRows = 2
    
    def __init__(self, oid, DataHandler, IsADBTable = True, IsNotCopy = True):
        self.oid = oid            # Any change here should go to copy functions as well
        self.DataHandler = DataHandler
        self.ColumnsByName = {}
        self.ColumsByIndex = {}
        self.NamebyAttnum = {}
        self.DisabledConstraints = []      
        self.Rows = []
        self.UniqueConstraint = []
        self.CheckConstraint = []
        self.FKConstraint = []
        self.IsADBTable = IsADBTable
        self.Name = oid     # Will be overridden for copy and new db table
        
        if IsNotCopy:
            if self.IsADBTable:
                DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
                DB = DBConn.cursor()
                
                NameQuery = "select relname from pg_class where oid = " + self.oid
                DB.execute(NameQuery)
                NameList = DB.fetchall()
                self.Name = NameList[0][0]
                
                if self.Name[0:3] == 'pg_':
                    raise Exception('Catalog table ' + self.Name + ' being modeled')
                
                ColQuery = ("Select cols.attname, cols.atttypid, cols.attnum, cols.attnotnull " +
                "from pg_attribute cols, pg_class tab " +
                "where tab.oid = cols.attrelid " +
                "and tab.oid = " + self.oid + " " +
                "and attnum > 0 " +
                "and cols.atttypid <> 0" 
                "order by attnum asc")
                
                DB.execute(ColQuery)
                
                index = 0;
                for col in DB.fetchall():
                    Name = col[0]
                    Type = col[1]
                    AttNum = col[2]
                    NotNull = col[3]
                    
                    if not (self.ColumnsByName.__contains__(Name)):
                        self.ColumnsByName[Name] = [Type, index]
                    if not (self.ColumsByIndex.__contains__(index)):
                        self.ColumsByIndex[index] = [Type, Name]
                    if not (self.NamebyAttnum.__contains__(AttNum)):
                        self.NamebyAttnum[AttNum] = [index, Name]
                        
                    if NotNull:
                        if not self.DataHandler.SkipConstraint(Type, 'NotNULL'):
                            self.CheckConstraint.append('T_NullTest\tIS_NOT_NULL\tCol '+ Type.__str__() + ' ' + Name+'\t')
                    
                    index = index + 1
                
                UkQuery = ("Select cons.conkey from pg_constraint cons, pg_class tab " +
                           "where tab.oid = " + self.oid +" " + 
                           "and cons.conrelid = tab.oid and contype = 'u'")
                DB.execute(UkQuery)

                for cons in DB.fetchall():
                    constraint = []
                    for AttNum in cons[0]:
                        constraint.append(self.NamebyAttnum[AttNum][0])
                    self.UniqueConstraint.append(constraint)        
                
                PKQuery = ("Select cons.conkey from pg_constraint cons, pg_class tab " +
                           "where tab.oid = " + self.oid +" " + 
                           "and cons.conrelid = tab.oid and contype = 'p'")
                DB.execute(PKQuery)
                
                for cols in DB.fetchall():
                    constraint = []
                    for AttNum in cols[0]:
                        Index = self.NamebyAttnum[AttNum][0]
                        Type = self.getColumnTypeFromIndex(Index)
                        constraint.append(Index)
                        if not self.DataHandler.SkipConstraint(Type, 'NotNULL'):
                            self.CheckConstraint.append('T_NullTest\tIS_NOT_NULL\tCol ' + Type.__str__() + ' ' + self.NamebyAttnum[AttNum][1]+'\t')
                    self.UniqueConstraint.append(constraint)
                    
                UkQuery2 = ("Select indkey from pg_index where indrelid = "  + self.oid + 
                            " and indisunique = 't' ")
                DB.execute(UkQuery2)

                for cons in DB.fetchall():
                    constraint = []
                    for AttNum in cons[0].split():
                        constraint.append(self.NamebyAttnum[int(AttNum)][0])
                    
                    AddCon = True
                    for UKcons in self.UniqueConstraint:
                        if UKcons == constraint:
                            AddCon = AddCon and False
                        else:
                            AddCon = AddCon and True
                    
                    if AddCon == True:
                        self.UniqueConstraint.append(constraint)
                
                CkCQuery = ("Select cons.conbin, cons.conname from pg_constraint cons, pg_class tab " +
                           "where tab.oid = " + self.oid +" " + 
                           "and cons.conrelid = tab.oid and contype = 'c'")
                
                DB.execute(CkCQuery)
                
                for cols in DB.fetchall():
                    resstring = self.ConstraintStruct(cols[0], cols[1])
                    if resstring != None:
                        self.CheckConstraint.append(resstring)
                        
                for _, v in self.ColumsByIndex.items():
                    C = self.DataHandler.AddTableConstraint(v[0], v[1])
                    if C != None:
                        self.CheckConstraint.append(C)
                        
                FKQuery = ("Select cons.conkey, tab2.oid, cons.confkey, cons.conname " +
                           "from pg_constraint cons, pg_class tab, pg_class tab2 " + 
                           "where cons.conrelid = tab.oid and contype = 'f' " + 
                           "and tab.oid = " + self.oid +" and cons.confrelid = tab2.oid" )
                
                DB.execute(FKQuery)
                
                for cons in DB.fetchall():
                    Fk = {} 
                    Fk['Column'] = cons[0][0]
                    Fk['ForeignTable'] = cons[1].__str__()
                    Fk['ForeignColumn'] = cons[2][0]
                    Fk['Name'] = cons[3]
                    self.FKConstraint.append(Fk)
                
                OTQuery = ("Select contype from pg_constraint cons, pg_class tab " +
                           "where tab.oid = " + self.oid +" " + 
                           "and cons.conrelid = tab.oid and contype not in ('p','c','u','f')")
                 
                DB.execute(OTQuery)
                 
                for cols in DB.fetchall():
                    raise Exception('Unmodeled Constraint on table '+cols[0])
                 
                for _ in range(self.TableRows):
                    self.addRow()
                    
                DB.close
                DBConn.close
                
            else:
                pass
            
        else:
            # It is a copy. We will set the details in copy function
            pass 
                
    def getRows(self):
        return self.Rows
    
    def getDisabledConstraints(self):
        return self.DisabledConstraints
    
    def getName(self):
        return self.Name
        
    def getColumnIndexFromName(self, Name):
        return (self.ColumnsByName[Name])[1]

    def getColumnIndexFromAttnum(self, FK):
        return self.NamebyAttnum[FK['Column']][0]   # 0: Index    1: Name
    
    def getForeignColumnIndexFromAttnum(self,FK):
        return self.NamebyAttnum[FK['ForeignColumn']][0]   # 0: Index    1: Name
    
    def getZ3ObjectForTableElement(self,ColIndex, RowNum):
        return self.Rows[RowNum][ColIndex]
    
    def getColumnNameList(self):
        List = []
        for index in self.ColumsByIndex:
            List.append(self.ColumsByIndex[index][1])
        return List
             
    def getColumnTypeList(self):
        List = []
        for index in self.ColumsByIndex:
            List.append(self.ColumsByIndex[index][0])
        return List
              
    def getColumnTypeFromIndex(self, Index):
        return (self.ColumsByIndex[Index])[0]
    
    def getColumnNameFromIndex(self, Index):
        return (self.ColumsByIndex[Index])[1]
        
    def getNumberOfRows(self):
        return len(self.Rows)
    
    def getNumberOfCols(self):
        return len(self.Rows[0])
    
    def getUniqueConstaints(self):
        return self.UniqueConstraint
    
    def getCheckCons(self):
        return self.CheckConstraint
    
    def getFKeyCons(self):
        return self.FKConstraint
    
    def getForeignTables(self):
        TableList = []
        for FK in self.FKConstraint:
            TableList.append(FK['ForeignTable'])
        return TableList
    
    def DisableFKConstraint(self, ForeignTableOID):
        FKs = []
        for FK in self.FKConstraint:
            FKs.append(FK)
        
        for FK in FKs:
            if FK['ForeignTable'] == ForeignTableOID :
                self.FKConstraint.remove(FK)
                self.DisabledConstraints.append(FK['Name'])       # Has irreverible effect on Data Set
    
    def getForeignTableName(self, FK):
        return FK['ForeignTable']
    
    def addRow(self):
        RowIndex = self.getNumberOfRows()+1
        row = []
        for ColIndex in range(self.ColumsByIndex.__len__()):
            V = self.ColumsByIndex[ColIndex]
            Type = V[0]
            Name = self.oid + "_" + V[1] + RowIndex.__str__() + ColIndex.__str__()
            row.append(self.DataHandler.getZ3Object(Type, Name))
        
        self.Rows.append(row)
        
    def addPreparedRow(self,row):
        self.Rows.append(row)
        
    def AddRowsFromTable(self, Result):
        for row in Result.getRows():
            self.addPreparedRow(row)
                
    def Copy(self):
        # Makes a Partly Shallow Partly Deep Copy of the Table
        T = Table(self.oid, self.DataHandler, self.IsADBTable, IsNotCopy = False)
        T.ColumnsByName = self.ColumnsByName
        T.ColumsByIndex = self.ColumsByIndex
        T.NamebyAttnum = self.NamebyAttnum
        T.UniqueConstraint = self.UniqueConstraint
        T.CheckConstraint = self.CheckConstraint
        T.FKConstraint = self.FKConstraint
        T.DisabledConstraints = self.DisabledConstraints
        T.Name = self.Name
        
        for eachrow in self.Rows:
            row = []
            for eachElement in eachrow:
                row.append(eachElement)
            T.Rows.append(row)
        
        return T
            
    def setRows(self, TableRows):
        self.Rows = TableRows
        
    def setColumnName(self,Index, Name):
        if not (self.ColumnsByName.__contains__(Name)):
            self.ColumnsByName[Name] = [0, Index]
        if not (self.ColumsByIndex.__contains__(Index)):
            self.ColumsByIndex[Index] = [0, Name]
        
    def UpdateRowsFromTable(self, Prev_Result):
        #ctid is always last column in update
        for eachrow in Prev_Result.getRows():
            ctid = eachrow[-1]
            row = eachrow[:-1]
            self.Rows[ctid] = row
    
    def DeleteRowsInTable(self,Prev_Result):
        #ctid should be the only column
        for eachrow in Prev_Result.getRows():
            ctid = eachrow[-1]
            self.Rows[ctid] = None
            
        Rows = []
        for eachrow in self.Rows:
            if eachrow != None:
                Rows.append(eachrow)
        
        self.Rows = Rows 
        
    def ConstraintStruct(self, S, ConName):
        a = S.find('{')
        if a == -1:
            return ''
        
        S = S[(a+1):]
        b = S.find(' ')
        
        token = S[:b]
        res = ''
        
        if token == 'BOOLEXPR':
            a = S.find(':boolop')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            op = S[:a]
        
        elif token == 'OPEXPR':
            a = S.find(':opfuncid')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            op = S[:a]
        
        elif token == 'VAR':
            a = S.find(':varattno')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            varattno = int(S[:a])
            a = S.find(':vartype')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            vartype = S[:a]
            op = 'Col ' + vartype + ' ' + self.NamebyAttnum[varattno][1]
            
        elif token == 'CONST':
            a = S.find(':consttype')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            Type = int(S[:a])
            
            a = S.find(':constisnull')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            isNULL = S[:a]
            
            if isNULL == 'true':
                op = Type.__str__() + ' ' + 'NULL'
            else:
                a = S.find(':constvalue')
                S = S[a:]
                op = Type.__str__() + ' ' + self.DataHandler.ProcessConstraintString(Type, S)
            
        elif token == 'SCALARARRAYOPEXPR':
            a = S.find(':opfuncid')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            operation = S[:a]
            
            a = S.find(':useOr')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            UseOr = S[:a]
            
            a = S.find(':varattno')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            varattno = int(S[:a])
            a = S.find(':vartype')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            vartype = S[:a]
            var = 'Col ' + vartype + ' ' + self.NamebyAttnum[varattno][1]
        
            a = S.find(':array_typeid')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            # find array end
            index = 0
            count = 1
            while count != 0:
                if (S[index] == '{'):
                    count = count + 1
                elif (S[index] == '}'):
                    count = count - 1
                index = index + 1
            
            elements = S[:index]
            elements = self.ConstraintStruct(elements, ConName)
            
            if elements == None:
                return None
            
            elements = elements.split('\t')[:-1]
            
            op = self.MakeOrCondition(UseOr, operation, var, elements)
            
            S = S[index:]
            
        elif token == 'NULLTEST':
            a = S.find(':varattno')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            varattno = int(S[:a])
            a = S.find(':vartype')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            vartype = S[:a]
            var = 'Col ' + vartype + ' ' + self.NamebyAttnum[varattno][1]
            
            a = S.find(':nulltesttype')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            TestType = int(S[:a])
            
            if not self.DataHandler.SkipConstraint(vartype, 'NotNULL'):
                if TestType == 1:
                    op = 'T_NullTest' + '\t' + 'IS_NOT_NULL' + '\t' + var
                else:
                    op = 'T_NullTest' + '\t' + 'IS_NULL' + '\t' + var
            else:
                op = 'True'     # to cover the Nulltest result when used in an expression                    
            
            
        elif token == 'FUNCEXPR':
            PrintLog('Disabling constraint because of FunctionCall ' + ConName)
            self.DisabledConstraints.append(ConName)
            return None
        
        elif token == 'COALESCE':
            a = S.find(':coalescetype')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            Type = S[:a]
            
            index = 0
            count = 1
            while count != 0:
                if (S[index] == '{'):
                    count = count + 1
                elif (S[index] == '}'):
                    count = count - 1
                index = index + 1
            
            elements = S[:index]
            elements = self.ConstraintStruct(elements, ConName)
            
            if elements == None:
                return None
            
            elements = elements.split('\t')[:-1]
            op = 'T_CoalesceExpr' + '\t' + Type + '\t'
            for ele in elements:
                op = op + 'ARGUMENT_START' + '\t' + ele + '\t' + 'ARGUMENT_END' + '\t'
            op = op + 'T_CoalesceExpr_End'
            
            S = S[index:]
            
        else:
            raise Exception ('Node not handled in check constrains ' + token)
        
        res = self.ConstraintStruct(S, ConName)
        if res == None:
            return None
        res = op + '\t' + res
        return res
    
    def MakeOrCondition(self,UseOr, operation, var, elements):
        if (len(elements) == 1):
            return operation + '\t' + var + '\t' + elements[0]
        else:
            if UseOr == 'true':
                return 'or' + '\t' + operation + '\t' + var + '\t' + elements[0] + '\t' + self.MakeOrCondition(UseOr, operation, var, elements[1:])
            else:
                return 'And' + '\t' + operation + '\t' + var + '\t' + elements[0] + '\t' + self.MakeOrCondition(UseOr, operation, var, elements[1:])