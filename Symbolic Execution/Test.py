from z3 import *

x = Int('x')
y = Int('y')
z = Int('z')
x1 = Int('x1')

S = Solver()

S.push()
S.add( )
print(S)
S.push()
S.add(y == z)
S.add(True)
print(S)
S.pop()
print(S)
S.pop()
print(S)