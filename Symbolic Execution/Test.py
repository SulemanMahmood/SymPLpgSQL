from z3 import *

x = Int('x')
y = Int('y')
z = Int('z')
x1 = Int('x1')

S = Solver()

S.push()
S.add(x == y)
print(S)
S.push()
S.add(y == z)
print(S)
S.check()
print(S.model())