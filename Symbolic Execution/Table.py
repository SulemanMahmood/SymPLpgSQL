from z3 import *
from Config import *
import psycopg2

class Table:
    TableRows = 3
    
    def __init__(self, Name, DataHandler, IsADBTable = True, IsNotCopy = True):
        self.Name = Name            # Any change here should go to copy functions as well
        self.DataHandler = DataHandler
        self.ColumnsByName = {}
        self.ColumsByIndex = {}
        self.NamebyAttnum = {}      
        self.Rows = []
        self.PK = []
        self.CheckConstraint = []
        self.IsADBTable = IsADBTable
        
        if IsNotCopy:
            if self.IsADBTable:
                ColQuery = ("Select cols.attname, cols.atttypid, cols.attnum " +
                "from pg_attribute cols, pg_class tab " +
                "where tab.oid = cols.attrelid " +
                "and tab.relname = '" + self.Name + "' " +
                "and attnum > 0 " + 
                "order by attnum asc")
                
                DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
                DB = DBConn.cursor()
                DB.execute(ColQuery)
                
                index = 0;
                for col in DB.fetchall():
                    Name = col[0]
                    Type = col[1]
                    AttNum = col[2]
                    
                    if not (self.ColumnsByName.__contains__(Name)):
                        self.ColumnsByName[Name] = [Type, index]
                    if not (self.ColumsByIndex.__contains__(index)):
                        self.ColumsByIndex[index] = [Type, Name]
                    if not (self.NamebyAttnum.__contains__(AttNum)):
                        self.NamebyAttnum[AttNum] = [index, Name]
                    
                    index = index + 1
                
                PKQuery = ("Select cons.conkey from pg_constraint cons, pg_class tab " +
                           "where tab.relname = '" + self.Name +"' " + 
                           "and cons.conrelid = tab.oid and contype = 'p'")
                DB.execute(PKQuery)
                
                for cols in DB.fetchall():
                    for AttNum in cols[0]:
                        self.PK.append(self.NamebyAttnum[AttNum][0])
                
                CkCQuery = ("Select cons.conbin from pg_constraint cons, pg_class tab " +
                           "where tab.relname = '" + self.Name +"' " + 
                           "and cons.conrelid = tab.oid and contype = 'c'")
                
                DB.execute(CkCQuery)
                
                for cols in DB.fetchall():
                    self.CheckConstraint.append(self.ConstraintStruct(cols[0]))
                    
                for k, v in self.ColumsByIndex.items():
                    C = self.DataHandler.AddTableConstraint(v[0], v[1])
                    if C != None:
                        self.CheckConstraint.append(C)
                
                OTQuery = ("Select contype from pg_constraint cons, pg_class tab " +
                           "where tab.relname = '" + self.Name +"' " + 
                           "and cons.conrelid = tab.oid and contype not in ('p','c')")
                 
                DB.execute(OTQuery)
                 
                for cols in DB.fetchall():
                    raise Exception('Unmodeled Constraint on table '+cols[0])
                 
                for i in range(self.TableRows):
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
        
    def getColumnIndexFromName(self, Name):
        return (self.ColumnsByName[Name])[1]
    
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
        return (self.ColumsByIndex[Index])[0]
        
    def getNumberOfRows(self):
        return len(self.Rows)
    
    def getNumberOfCols(self):
        return len(self.Rows[0])
    
    def getPKColumns(self):
        return self.PK
    
    def getCheckCons(self):
        return self.CheckConstraint
    
    def addRow(self):
        RowIndex = self.getNumberOfRows()+1
        row = []
        for ColIndex in range(self.ColumsByIndex.__len__()):
            V = self.ColumsByIndex[ColIndex]
            Type = V[0]
            Name = self.Name + "_" + V[1] + RowIndex.__str__() + ColIndex.__str__()
            row.append(self.DataHandler.getZ3Object(Type, Name))
        
        self.Rows.append(row)
        
    def addPreparedRow(self,row):
        self.Rows.append(row)
        
    def AddRowsFromTable(self, Result):
        for row in Result.getRows():
            self.addPreparedRow(row)
                
    def Copy(self):
        # Makes a Partly Shallow Partly Deep Copy of the Table
        T = Table(self.Name, self.DataHandler, self.IsADBTable, False)
        T.ColumnsByName = self.ColumnsByName
        T.ColumsByIndex = self.ColumsByIndex
        T.NamebyAttnum = self.NamebyAttnum
        T.PK = self.PK
        
        for eachrow in self.Rows:
            row = []
            for eachElement in eachrow:
                row.append(eachElement)
            T.Rows.append(row)
        
        return T
            
    def setRows(self, TableRows):
        self.Rows = TableRows
        
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
        
    def ConstraintStruct(self, S):
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
            op = 'Col ' + self.NamebyAttnum[int(S[:a])][1]
            
        elif token == 'CONST':
            a = S.find(':consttype')
            S = S[a:]
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            Type = int(S[:a])
            a = S.find(':constvalue')
            S = S[a:]
            op = Type.__str__() + ' ' + self.DataHandler.ProcessConstraintString(Type, S)
            
        elif token == 'FUNCEXPR':
            raise Exception ('Proceudure call in check constraint: Not Supported for now')
        
        else:
            raise Exception ('Node not handled in check constrains ' + token)
        
        res = self.ConstraintStruct(S)
        res = op + '\t' + res
        return res