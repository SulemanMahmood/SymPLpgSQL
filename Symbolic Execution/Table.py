from z3 import Int

class Table:
    
    def __init__(self, Name, IsADBTable):
        self.Name = Name
        self.ColumnsByName = {}
        self.ColumsByIndex = {}
        self.Rows = []
        self.PK = []
        self.IsADBTable = IsADBTable
        
        if self.IsADBTable:
            DetailsFile = './Resources/'+Name+'Details.txt'
            Details = open(DetailsFile,'r')
            
            self.NumberOfColumns = int(Details.readline())
            for index in range(self.NumberOfColumns):
                Line = Details.readline()
                Col = Line.split()
                Type = Col[0]
                Name = Col[1]
                if not (self.ColumnsByName.__contains__(Name)):
                    self.ColumnsByName[Name] = [Type, index]
                if not (self.ColumsByIndex.__contains__(index)):
                    self.ColumsByIndex[index] = [Type, Name]
            
            Line = Details.readline()
            while (Line != ''):
                Parts = Line.split()
                if (Parts[0] == 'PK'):
                    for i in range(len(Parts) - 1):
                        self.PK.append((self.ColumnsByName[Parts[i+1]])[1])
                
                elif (Parts[0] == 'FK'):
                    pass
                
                Line = Details.readline()
                
        else:
            pass
        
    
    
    def getColumnNameFromIndex(self, Index):
        return (self.ColumsByIndex[Index])[1]
    
    
    
    def getColumnTypeFromIndex(self, Index):
        return (self.ColumsByIndex[Index])[0]
        
    
    
    def getNumberOfRows(self):
        return len(self.Rows)
    
    
    
    def addRow(self):
        RowIndex = self.getNumberOfRows()+1
        row = []
        for ColIndex in range(self.ColumsByIndex.__len__()):
            V = self.ColumsByIndex[ColIndex]
            Type = V[0]
            Name = V[1]+ RowIndex.__str__() + ColIndex.__str__()
            row.append(self.getZ3Object(Type, Name))
        
        self.Rows.append(row)
        
            
            
    def getZ3Object(self, Type,Name):
        if (Type == 'Int'):
            return Int(Name)
            
        elif (Type == 'String'):
            pass
        
        elif (Type == 'Date'):
            pass