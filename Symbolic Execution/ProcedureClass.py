import psycopg2
from Config import *

class ProcedureClass:
    def __init__(self, Name, ArgTypes, ReturnType):
        self.Name = Name
        
        self.ArgTypes = []
        if ArgTypes != '':
            self.ArgTypes = ArgTypes.split(' ')
            for i in range(len(self.ArgTypes)):
                self.ArgTypes[i] = int(self.ArgTypes[i])
        
        self.ReturnType = ReturnType
        
    def getArgList(self):
        ArgList = []
        for i in range(len(self.ArgTypes)):
            ArgList.append([self.ArgTypes[i],  '$'+(i+1).__str__()])
        return ArgList           
       
    def getName(self):
        return self.Name
         
    def getNoOfInputs(self):
        return len(self.ArgTypes)
    
    def getReturnType(self):
        return self.ReturnType
    

def getProcedureFromNumber(oid):
    DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
    DB = DBConn.cursor()
    DB.execute("Select proname, proargtypes, prorettype from pg_proc p where prolang = 11899 and oid = "+oid.__str__()+" ")

    proc = DB.fetchall()
    
    if proc == []:
        return None
    else:
        Procedure = ProcedureClass(proc[0][0], proc[0][1], proc[0][2])
        PrintLog(Procedure.getName());
    
    DB.close
    DBConn.close
    
    return Procedure
            
def getProcedureReturnType(oid):
    if oid in ['Not', 'NOT', 'not']:
        return 16
    elif oid in ['And', 'AND', 'and']:
        return 16
    elif oid in ['Or', 'OR', 'or']:
        return 16
    else:
        DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
        DB = DBConn.cursor()
        DB.execute("Select prorettype from pg_proc p where oid = " + oid +" ")
    
        proc = DB.fetchall()
    
        DB.close
        DBConn.close
        
        if proc == []:
            return None
        
        return proc[0][0]

def getNoOfArgsForProcedure(oid):
    DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
    DB = DBConn.cursor()
    DB.execute("Select pronargs from pg_proc p where oid = "+oid.__str__()+" ")

    proc = DB.fetchall()
    DB.close
    DBConn.close
    
    return proc[0][0]

def getReturnValueFromModel(oid, Arglist, State):
    if oid == 1574:         # Sequence nexval
        return State.getSequence(Arglist[0].__str__()).nextval()
    
    elif oid == 480:        # Int8 to Int4 converter
        return Arglist[0]
    
    elif oid == 1299:       # Now = returns current timestamp
        return 0
    
    elif oid == 871:        # Upper
        return Arglist[0]
    
    elif oid == 1079:       # String to Oid Conversion
        name =  State.DataHandler.getString(Arglist[0])
        if name[0] == '"':
            name = name[1:-1]
        
        DBConn = psycopg2.connect(dbname=dbname, database=database, user=user, password=password, host=host, port=port)
        DB = DBConn.cursor()
        NameQuery = "Select oid from pg_class where relname = '" + name + "' "
        DB.execute(NameQuery)
    
        proc = DB.fetchall()
        DB.close
        DBConn.close
        
        return proc[0][0]
    
    elif oid == 2027:         # Timestamp with timezone to timestamp without timezone conversion
        return Arglist[0]
    
    else:
        raise Exception('Unmodeled non-PLpgSQL procedure call ' + oid.__str__())