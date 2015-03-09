class CombinationGenerator:
    
    def __init__(self, InnerRows, OuterRows):
        self.List = []
        for i in range(InnerRows):
            for j in range(OuterRows):
                pair = [i, j]
                self.List.append(pair)
                                 
    def getAllSinglePairs(self):
        return self.List
    
    def getAllTwoPairCombinations(self):
        Combinations = []
        for i in range(len(self.List)):
            for j in range(i+1,len(self.List)):
                Combinations.append([self.List[i], self.List[j]])
        return Combinations
        