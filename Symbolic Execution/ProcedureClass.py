class ProcedureClass:
    def __init__(self, Name, ArgTypes, ReturnType):
        self.Name = Name
        
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