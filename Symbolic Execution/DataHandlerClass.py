from z3 import *
from random import randint

class DataHandlerClass:
    
    def __init__(self):
        self.StringsByIndex  = {}
        self.StringsByValue  = {}
        self.StringIndex = 0
    
    def getZ3Object(self, Type, Name):
        if (Type >= 20 and Type <= 23 ) or (Type == 1700):   # Integer type or Numeric type
            return Int(Name)
        
        elif Type == 16 :                  # Boolean type
            return Bool(Name)
        
        elif Type == 25 :                  # Text type
            return Int(Name)
        
        else:
            raise Exception('Unknown Data Type ' + Type.__str__())
        
    def ProcessConstant(self, Type, Value):   # Type as int, Value as String
        if (Type >= 20 and Type <= 23 ):   # Integer type
            return int(Value)

        elif Type == 16:                    # Boolean type
            if Value == 'True':
                return True
            elif Value == 'False':
                return False
            else:
                raise Exception('Invalid Value for Boolean type')

        elif Type == 25:                    # text type
            self.AddString(Value)
            return self.StringsByValue[Value]

        else:
            raise Exception('Unknown Data Type In Constant Processing ' + Value)
        
    def getValue(self, Model, Type, Variable):
        if (Type >= 20 and Type <= 23 ) or (Type == 1700):   # Integer type or Numeric type
            try:
                value = Model.evaluate(Variable)
                int(value.__str__())
            except:
                value = randint(0,10)
            finally:
                return value.__str__()
        
        elif Type == 16:                     # Boolean
            value = Model.evaluate(Variable)
            if value.__str__() == 'True':
                return 'True'
            elif value.__str__() == 'False':
                return 'False'
            else:
                value = randint(0,1)
                if value.__str__() == 1:
                    return 'True'
                else:
                    return 'False'
            
        elif Type == 25:                    # String / text
            try:
                value = Model.evaluate(Variable)
                value = int(value.__str__())
            except:
                value = randint(0,10)
            finally:
                if self.StringsByIndex.__contains__(value):
                    return "'" + self.StringsByIndex[value] + "'"
                else:
                    value = value.__str__()
                    self.AddString(value)
                    return "'" + value + "'"
                
            
        else:
            raise Exception('Unknwon Data Type for Model ' + Type.__str__())
    
    def AddString(self,Value):
        if not self.StringsByValue.__contains__(Value):
            self.StringIndex = self.StringIndex + 1
            self.StringsByIndex[self.StringIndex] = Value
            self.StringsByValue[Value] = self.StringIndex        