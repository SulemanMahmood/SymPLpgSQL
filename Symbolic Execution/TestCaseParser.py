from random import randint

class TestCaseParser:

    IndexByOrder = {}       # value = [Type, Name]
    IndexByName = {}        # value = Order
    TestCasePath = './TestCases/'
    
    def __init__(self,proc_name, DetailsFile):
        Details = open(DetailsFile,'r');
        Args = int(Details.readline())
        self.CaseNo = 0
        self.proc_name = proc_name
        
        for i in range(Args):
            Line = Details.readline()
            In = Line.split()
            self.IndexByOrder[i] = [In[0], In[1]]
            self.IndexByName[In[1]] = i
            
        #further stuff will be added later
        Details.close
        
        
    def get_first_test_case(self):
        self.CaseNo = self.CaseNo+1
        T = self.TestCasePath + 'Case' + self.CaseNo.__str__() + '.sql'
        case = 'Select ' + self.proc_name + '('
        
        for i in range(self.IndexByOrder.__len__()):
            In = self.IndexByOrder[i]
            
            if In[0] == 'Int':
                value = randint(0,10)
                case = case + value.__str__() + ','
            
            elif In[0] == 'something else':
                print('something else')
            else:
                print('Error: Undefined Data Type')
                
        case = case[:-1] + ');'
        
        Test = open(T,'w')
        Test.write(case)
        Test.flush()
        Test.close
        return T
    
    
    def ParseModel(self, M, Input):
        self.CaseNo = self.CaseNo+1
        T = self.TestCasePath + 'Case' + self.CaseNo.__str__() + '.sql'
        case = 'Select ' + self.proc_name + '('
        
        for i in range(self.IndexByOrder.__len__()):
            In = self.IndexByOrder[i]
            
            if In[0] == 'Int':
                var = Input[In[1]]
                var = var[-1]
                value = M.evaluate(var)
                
                try:
                    int(value.__str__())
                    case = case + value.__str__() + ','
                except:
                    value = randint(0,10)
                    case = case + value.__str__() + ','
                    
            
            elif In[0] == 'something else':
                print('something else')
            else:
                print('Error: Undefined Data Type')
                
        case = case[:-1] + ');'
        print(case)
        Test = open(T,'w')
        Test.write(case)
        Test.close
        
        return T