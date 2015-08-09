from Config import *
import psycopg2

class Sequence:
    
    SequenceDataType = 23
    
    def __init__(self, oid, DataHandler, IsNotCopy = True):
        self.oid = oid            # Any change here should go to copy functions as well
        self.Name = oid     # Will be overridden for copy and new db table
        self.DataHandler = DataHandler
        self.Value = 0
        self.StartingValueForState = 0
#         self.Startvalue
#         self.IncrementValue         # Defined Later
#         self.MinValue
#         self.MaxValue
        
        if IsNotCopy:
            self.Startvalue = self.DataHandler.getZ3Object(self.SequenceDataType, oid + '_Start_Value')
            
            DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
            DB = DBConn.cursor()
            
            NameQuery = "select relname from pg_class where oid = " + self.oid
            DB.execute(NameQuery)
            NameList = DB.fetchall()
            self.Name = NameList[0][0]
            
            ColQuery = ("Select increment_by, min_value, max_value " +
            "from  " + self.Name)
                
            DB.execute(ColQuery)
            
            for col in DB.fetchall():
                self.IncrementValue = col[0]
                self.MinValue = col[1]
                self.MaxValue = col[2]
            
            DB.close
            DBConn.close
                
    def getName(self):
        return self.Name

    def getStartValue(self):
        return self.Startvalue
    
    def getIncrementValue(self):
        return self.IncrementValue

    def getMinValue(self):
        return self.MinValue
    
    def getMaxValue(self):
        return self.MaxValue
    
    def getValue(self):
        return self.Value
    
    def setValue(self, Value):
        self.Value = Value
            
    def nextval(self):
        retval = self.Startvalue + self.Value
        self.Value = self.Value + self.IncrementValue
        return retval
    
    def Advance(self):
        S = Sequence(self.oid, self.DataHandler, IsNotCopy = False)
        S.Name = self.getName()
        S.Value = self.Value
        S.StartingValueForState = self.Value
        S.Startvalue = self.getStartValue()
        S.IncrementValue = self.IncrementValue
        S.MinValue = self.MinValue
        S.MaxValue = self.MaxValue
        
        return S
    
    def ResetSequence(self):
        self.Value = self.StartingValueForState