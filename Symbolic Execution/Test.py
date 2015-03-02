from z3 import *

x = Int('x')
y = Int('y')
z = Int('z')
x1 = Int('x1')

S = Solver()

S.push()
S.add(x1 == x + y)
print(S)
S.push()
S.add(y > 3)
S.add(x > 5)
S.check()
print(S.model())