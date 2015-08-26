from Config import PrintLog

class ChoicesClass:
    
    
    def __init__(self):
        self.ChoiceIndex = 1
        self.ChoicesProcessed = 1
        self.Conditions = {}        # Conditions that need to be setup for next Execution
        self.Result_Tables = {}     # Corresponding Results for Conditions   
    
    def AddChoice(self,Condition, Results_Table, Choices = None):
        if Choices == None:
            PrintLog(Condition)
            self.Conditions[self.ChoiceIndex] = Condition
            self.Result_Tables[self.ChoiceIndex] = Results_Table
            self.ChoiceIndex = self.ChoiceIndex + 1
        else:
            for Choice in Choices:
                C = Condition + ' , ' + Choice
                PrintLog(C)
                self.Conditions[self.ChoiceIndex] = C
                self.Result_Tables[self.ChoiceIndex] = Results_Table
                self.ChoiceIndex = self.ChoiceIndex + 1
        
    def getNextCondition(self):
        if (self.ChoiceIndex > self.ChoicesProcessed):
            Cond = self.Conditions[self.ChoicesProcessed]
            Res_tbl = self.Result_Tables[self.ChoicesProcessed]
            
            self.ChoicesProcessed = self.ChoicesProcessed + 1         
            return Cond, Res_tbl
        else:
            return '', None
        
        