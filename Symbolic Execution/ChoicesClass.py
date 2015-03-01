class ChoicesClass:
    
    
    def __init__(self):
        self.ChoiceIndex = 1
        self.Conditions = {}         # Conditions that need to be setup for next Execution
        self.Variable_Updates = {}   # a list will store variable updates that needs to be applied on State
        self.Table_Updates = {}      # may become a more involved structure when implemented in full
        self.ChoicesProcessed = 1    
    
    def AddChoice(self,Condition, Var_Updates, Table_Updates):
        self.Conditions[self.ChoiceIndex] = Condition
        self.Variable_Updates[self.ChoiceIndex] = Var_Updates
        self.Table_Updates[self.ChoiceIndex] = Table_Updates
        
        self.ChoiceIndex = self.ChoiceIndex + 1
        
    def getNextCondition(self):
        if (self.ChoiceIndex > self.ChoicesProcessed):
            Cond = self.Conditions[self.ChoicesProcessed]
            var_upd = self.Variable_Updates[self.ChoicesProcessed]
            tbl_upd = self.Table_Updates[self.ChoicesProcessed]
            
            self.ChoicesProcessed = self.ChoicesProcessed + 1         
            return Cond, var_upd, tbl_upd
        else:
            return '', {}, {}
        