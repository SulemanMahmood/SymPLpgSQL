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
        T = self.TestCasePath + self.Procedure.getName() + '_Data' + self.CaseNo.__str__() + '.sql'
        
        Test = open(T,'w')
        
        # Truncate Tables first
        for table in State.getTableListForTestCase():
            line = 'Truncate Table '+ table + ';\n'
            Test.write(line);
        
        # Setup data for tables
        for table in State.getTableListForTestCase():
            for eachrow in State.getTableRowForTestCase(table):
                line = 'insert into '+ table + '('
                
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
        
        line = 'commit;\n'
        Test.write(line)
        Test.flush()
        Test.close
        DataFile = T;
        
        T = self.TestCasePath + self.Procedure.getName() + '_Case' + self.CaseNo.__str__() + '.sql'
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
    