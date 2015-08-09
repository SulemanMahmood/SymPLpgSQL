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
    DB.execute("Select proargtypes from pg_proc p where oid = "+oid.__str__()+" ")

    proc = DB.fetchall()
    DB.close
    DBConn.close
    
    ArgTypes = proc[0][0]
    ArgTypes = ArgTypes.split(' ')
    
    return len(ArgTypes)

def getReturnValueFromModel(oid, Arglist, State):
    if oid == 1574:
        return State.getSequence(Arglist[0].__str__()).nextval()
    else:
        raise Exception('Unmodeled non-PLpgSQL procedure call ' + oid.__str__())