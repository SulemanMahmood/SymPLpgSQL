from reportlab.lib.validators import isString

class TestCaseParser:

    TestCasePath = './TestCases/'
    
    def __init__(self,Procedure, DataHandler):
        self.CaseNo = 0
        self.Procedure = Procedure
        self.DataHandler = DataHandler
        
    def IncrementCaseNumber(self):
        self.CaseNo = self.CaseNo+1
                
    def getCase(self, Model, State):
        T = self.TestCasePath + self.Procedure.getName() + self.Procedure.getNoOfInputs().__str__() + "_Data" + self.CaseNo.__str__() + ".sql"
        
        Test = open(T,'w')
        
        # Truncate Tables first
        for table in State.getTableListForTestCase():
            TableName = State.getTableName(table)
            line = 'Truncate Table '+ TableName + ' cascade;\n'
            Test.write(line);
        
        # Disable Triggers    
        for table in State.getTableListForTestCase():
            TableName = State.getTableName(table)
            line = 'Alter Table '+ TableName + ' DISABLE TRIGGER ALL;\n'
            Test.write(line);
            
        # Disable Constraints
        for table in State.getTableListForTestCase():
            TableName = State.getTableName(table)
            for Con in State.getDisabledConstraints(table):
                line = 'Alter Table '+ TableName + ' DISABLE CONSTRAINT ' + Con + ';\n'
                Test.write(line); 
        
        # Setup data for tables
        for table in State.getTableListForTestCase():
            for eachrow in State.getTableRowForTestCase(table):
                TableName = State.getTableName(table)
                line = 'insert into '+ TableName + ' ('
                
                Columns = State.getColumnNamesListForTestCase(table)
                Types = State.getColumnTypesListForTestCase(table)
                
                for ColName in Columns:
                    line = line + ColName + ', '
                line = line[:-2] + ') values ('
                
                for i in range(len(Types)):
                    Value = self.DataHandler.getValue(Model, Types[i] , eachrow[i])
                    if isString(Value):
                        line = line + Value + ', '
                    else:
                        line = line + 'NULL' + ', '
                
                line = line[:-2] + ');\n'                        
                Test.write(line);
                
        #Enable Triggers
#         for table in State.getTableListForTestCase():
#             TableName = State.getTableName(table)
#             line = 'Alter Table '+ TableName + ' ENABLE TRIGGER ALL;\n'
#             Test.write(line);
        
        line = 'commit;\n'
        Test.write(line)
        Test.flush()
        Test.close
        DataFile = T;
        
        T = self.TestCasePath + self.Procedure.getName() + self.Procedure.getNoOfInputs().__str__() + '_Case' + self.CaseNo.__str__() + '.sql'
        Test = open(T,'w')
        
        # Setup procedure Executeion
        line = 'Select ' + self.Procedure.getName() + '('
        
        for i in range (self.Procedure.getNoOfInputs()):
            Name = '$'+(i+1).__str__()
            Variable = State.getZ3ObjectFromNameForTestCase(Name)
            Type = State.getTypeFromNameForTestCase(Name)

            Value = self.DataHandler.getValue(Model, Type, Variable)
            
            if isString(Value):
                line = line + Value + ', '
            else:
                line = line + 'NULL' + ', '
        
        if self.Procedure.getNoOfInputs() > 0:
            line = line[:-2]
        
        line = line + ');\n'   
        Test.write(line);
        Test.flush()
        Test.close
        
        TestFile = T
        return DataFile, TestFile