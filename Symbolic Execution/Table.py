class Table:
    
    def __init__(self, Name, IsADBTable):
        self.Name = Name
        self.ColumnsByName = {}
        self.ColumsByIndex = {}
        self.Rows = []
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
        else:
            pass
        
    
    
    def getColumnNameFromIndex(self, Index):
        return (self.ColumsByIndex[Index])[1]
                