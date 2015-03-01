from random import randint
from reportlab.lib.validators import isString

class TestCaseParser:

    TestCasePath = './TestCases/'
    
    def __init__(self,proc_name):
        self.CaseNo = 0
        self.proc_name = proc_name
                
    def getCase(self, Model, State):
        self.CaseNo = self.CaseNo+1
        T = self.TestCasePath + 'Case' + self.CaseNo.__str__() + '.sql'
        
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
                    Value = self.getValue(Model, Types[i] , eachrow[i])
                    if isString(Value):
                        line = line + Value + ', '
                    else:
                        line = line + 'NULL' + ', '
                
                line = line[:-2] + ');\n'                        
                Test.write(line);
        
        line = 'commit;\n'
        Test.write(line)
        
        # Setup procedure Executeion
        line = 'Select ' + self.proc_name + '('
        
        for i in range (State.getNoOfInputs()):
            Name = '$'+(i+1).__str__()
            Variable = State.getZ3ObjectFromNameForTestCase(Name)
            Type = State.getTypeFromNameForTestCase(Name)

            Value = self.getValue(Model, Type, Variable)
            
            if isString(Value):
                line = line + Value + ', '
            else:
                line = line + 'NULL' + ', '

        line = line[:-2] + ');\n'                        
        Test.write(line);
        
        Test.flush()
        Test.close
        return T
    
    def getValue(self, Model, Type, Variable):
        if (Type == 'Int'):
            try:
                value = Model.evaluate(Variable)
                int(value.__str__())
                return value.__str__()
            except:
                value = randint(0,10)
                return value.__str__()
            
        elif (Type == 'String'):
            pass
        
        elif (Type == 'Date'):
            pass
         