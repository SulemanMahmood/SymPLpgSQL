from z3 import *
from random import randint

class DataHandlerClass:
    
    def __init__(self):
        self.StringsByIndex  = {}
        self.StringsByValue  = {}
        self.StringIndex = 0
        self.NullValue = -101
        
        self.BaseDate = '20150401'
        
    
    def getZ3Object(self, Type, Name):
        if (Type >= 20 and Type <= 23 ):   # Integer type or Numeric type
            return Int(Name)
        
        elif Type == 16 :                  # Boolean type
            return Bool(Name)
        
        elif Type == 25 :                  # Text type
            return Int(Name)
        
        elif Type == 1042 :                # Char type
            return Int(Name)
        
        elif Type == 1700 :                # Numeric
            return Real(Name)
        
        elif Type == 1082 :                # Date
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
        
        elif Type == 1042:                  # char type
            return ord(Value)

        else:
            raise Exception('Unknown Data Type In Constant Processing ' + Type.__str__())
        
    def getValue(self, Model, Type, Variable):
        if (Type >= 20 and Type <= 23 ):   # Integer type
            try:
                value = Model.evaluate(Variable)
                value = int(value.__str__())
            except:
                value = randint(0,10)
            finally:
                if value == self.NullValue:
                    return 'NULL'
                else: 
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
                if value == self.NullValue:
                    return 'NULL'
                elif self.StringsByIndex.__contains__(value):
                    return "'" + self.StringsByIndex[value] + "'"
                else:
                    value = value.__str__()
                    self.AddString(value)
                    return "'" + value + "'"
        
        elif Type == 1042:                    # char
            try:
                value = Model.evaluate(Variable)
                value = int(value.__str__())
            except:
                value = randint(65,90)
            finally:
                if value == self.NullValue:
                    return 'NULL'
                else:
                    return "'" + chr(value) + "'"
        
        elif Type == 1700:      #Numeric
            value = Model.evaluate(Variable)
            if isinstance(value, RatNumRef):
                ValParts = value.__str__().split('/')
                if (ValParts.__len__() == 1):
                    if value == self.NullValue:
                        return 'NULL'
                    else:
                        return ValParts[0];
                else:
                    numerator = ValParts[0] + '.0'
                    denominator = ValParts[1]
                    exec('float = '+ numerator + ' / ' + denominator)
                    return float.__str__()
            
            elif isinstance(value, ArithRef):
                return randint(0,10).__str__()
            else:
                raise Exception('Exception in processig numeric')
        
        elif Type == 1082:      #Date
            try:
                value = Model.evaluate(Variable)
                value = int(value.__str__())
            except:
                value = randint(0,10)
            finally:
                if value == self.NullValue:
                    return 'NULL'
                else:
                    year = int(self.BaseDate[:4])
                    month = int(self.BaseDate[4:][:2])
                    day = int(self.BaseDate[-2:])
                    
                    year, month, day = self.AddDate(year, month, day, value)
                    
                    year = year.__str__()
                    month = month.__str__()
                    day = day.__str__()
                    
                    if len(day) < 2:
                        day = '0' + day
                        
                    if len(month) < 2:
                        month = '0' + month 
                    
                    value = year.__str__() + month.__str__() + day.__str__()
                    return "'" + value + "'"
            
        else:
            raise Exception('Unknwon Data Type for Model ' + Type.__str__())
        
    def ProcessConstraintString(self,Type, S):
        if Type == 1042:
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            length = int(S[:a])
            a = S.find('[')
            b = S.find(']')
            value = S[(a+1):b]
            value = value.split()
            r = ''
            for i in range(4,length):
                r = r + chr(int(value[i]))
            
            return r
        
        elif Type == 23:
            a = S.find(' ')
            S = S[(a+1):]
            a = S.find(' ')
            length = int(S[:a])
            a = S.find('[')
            b = S.find(']')
            value = S[(a+1):b]
            value = value.split()
            x = 0
            for i in range(length):
                x = x << 8
                x = x | int(value[i]);
            return x.__str__()
        
        else:
            raise Exception('Type not handled in check constrains ' + Type.__str__())

    def AddTableConstraint(self, Type, Name):
        if Type == 1042:
            return ("or\t" +
                        "or\t" + 
                            "and\t" +
                                "150\tCol " + Name + "\t1042 A\t" + 
                                "149\tCol " + Name + "\t1042 Z\t" +
                            "and\t" + 
                                "150\tCol " + Name + "\t1042 a\t" + 
                                "149\tCol " + Name + "\t1042 z\t" +
                        "and\t" + 
                            "150\tCol " + Name + "\t1042 0\t" + 
                            "149\tCol " + Name + "\t1042 9\t")
        else:
            return None
    
    def getVariableTypeConstraint(self, Type, Name):
        if Type == 1042:
            return ("or\t" +
                        "or\t" + 
                            "and\t" + 
                                "150\tParam " + Name + "\t1042 A\t" + 
                                "149\tParam " + Name + "\t1042 Z\t" +
                            "and\t" + 
                                "150\tParam " + Name + "\t1042 a\t" + 
                                "149\tParam " + Name + "\t1042 z\t" +
                        "and\t" + 
                            "150\tParam " + Name + "\t1042 0\t" + 
                            "149\tParam " + Name + "\t1042 1\t")
    
        else:
            return None
        
    def AddString(self,Value):
        if not self.StringsByValue.__contains__(Value):
            self.StringIndex = self.StringIndex + 1
            self.StringsByIndex[self.StringIndex] = Value
            self.StringsByValue[Value] = self.StringIndex
            
    def AddDate(self,year, month, day, value):
        daysInMonth = self.daysInaMonth(year, month)        
        if value >= 0:
            remainingDays = daysInMonth - day
            if remainingDays >= value:
                return year, month, day + value
            else:
                month = month + 1
                if month > 12:
                    return self.AddDate(year + 1, 1, 1, value - remainingDays - 1)
                else:
                    return self.AddDate(year, month, 1, value - remainingDays - 1)
        else:
            if day > abs(value):
                return year, month, day + value
            else:
                month = month - 1
                if month < 1:
                    return self.AddDate(year - 1, 12, 31, value + day)
                else:
                    daysInMonth = self.daysInaMonth(year, month)
                    return self.AddDate(year, month, daysInMonth, value + day)
                
    def daysInaMonth(self, year, month):
        if month in [1,3,5,7,8,10,12]:
            daysInMonth = 31
        elif month in [4,6,9,11]:
            daysInMonth = 30
        elif month in [2]:
            if year % 4 == 0:
                if year % 100 == 0:
                    daysInMonth = 28
                else:
                    daysInMonth = 29
            else:
                daysInMonth = 28
        return daysInMonth