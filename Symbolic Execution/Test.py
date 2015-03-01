from z3 import *

x = Int('x')
y = Int('y')
z = Int('z')

S = Solver()

S.push()
S.add(x > y)

S.push()
S.add(y > z)


print(S)
S.pop()
print(S)