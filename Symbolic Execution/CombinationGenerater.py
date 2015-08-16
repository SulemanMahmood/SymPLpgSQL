class CombinationGenerator:
    
    def __init__(self, InnerRows, OuterRows = None):
        self.List = []
        if OuterRows == None:
            for i in range(InnerRows):
                pair = i
                self.List.append(pair)
        
        else:                
            for i in range(InnerRows):
                for j in range(OuterRows):
                    pair = [i, j]
                    self.List.append(pair)
    
    def copyList(self, List):
        result = []
        for i in range(List.__len__()):
            result.append(List[i])
        return result            
                                     
    def getCombinationIndexes(self, SetSize):
        Indexes = []
        StartingValue = range(SetSize)
        
        ListCopy = self.copyList(StartingValue)            
        Indexes.append(ListCopy)
        
        while True:
            
            ChangeValueIndex = SetSize - 1
            for n in range(SetSize):
                if StartingValue[n] == ( self.List.__len__() - 1 ):
                    ChangeValueIndex = n - 1
                    break
            
            if ChangeValueIndex ==  -1:
                return Indexes
            
            if ChangeValueIndex == (SetSize - 1):
                if StartingValue[ChangeValueIndex] ==  ( self.List.__len__() - 1 ):
                    return Indexes

            StartingValue[ChangeValueIndex] = StartingValue[ChangeValueIndex] + 1
            
            StartingIndex = StartingValue[ChangeValueIndex] + 1                 
            a = ChangeValueIndex + 1
            
            broken = False
            while a < SetSize:
                StartingValue[a] = StartingIndex
                
                if StartingValue[a] >=  self.List.__len__():
                    broken = True
                    break
                
                StartingIndex = StartingIndex + 1
                a = a + 1
            
            if not broken:
                ListCopy = self.copyList(StartingValue)            
                Indexes.append(ListCopy)
                
    def getCombinations(self, SetSize):
        CombinationIndexes = self.getCombinationIndexes(SetSize)
        Result = []
        
        for Indexes in CombinationIndexes:
            Row = []
            for index in Indexes:
                Row.append(self.List[index])
                
            Result.append(Row)
        return Result
        