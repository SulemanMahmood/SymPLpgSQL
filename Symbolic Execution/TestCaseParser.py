from random import randint
from reportlab.lib.validators import isString

class TestCaseParser:

    IndexByOrder = {}       # value = [Type, Name]
    IndexByName = {}        # value = Order
    TestCasePath = './TestCases/'
    
    def __init__(self,proc_name):
        self.CaseNo = 0
        self.proc_name = proc_name
        
        
        
        
    def getCase(self, Model, Variables, Types, Alaises, Tables):
        self.CaseNo = self.CaseNo+1
        T = self.TestCasePath + 'Case' + self.CaseNo.__str__() + '.sql'
        
        Test = open(T,'w')
        
        # Truncate Tables first
        for k,v in Tables.items():
            line = 'Truncate Table '+ k + ';\n'
            Test.write(line);
        
        # Setup data for tables
        for k,v in Tables.items():
            for eachrow in v.Rows:
                line = 'insert into '+ k + '('
                
                for Index in range(v.ColumsByIndex.__len__()):
                    line = line + v.getColumnNameFromIndex(Index) + ', '
                line = line[:-2] + ') values ('
                
                for i in range(v.NumberOfColumns):
                    Value = self.getValue(Model, v.getColumnTypeFromIndex , (eachrow[i])[0])
                    if isString(Value):
                        line = line + Value + ', '
                    else:
                        line = line + 'NULL' + ', '
                
                line = line[:-2] + ');\n'                        
                Test.write(line);
        
        # Setup procedure Executeion
        line = 'Select ' + self.proc_name + '('
        
        for i in range (Alaises.__len__()):
            Name = Alaises['$'+(i+1).__str__()]
            Variable = Variables[Name]
            Type = Types[Name]

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

            
        