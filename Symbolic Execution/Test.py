from z3 import Int, Solver
V = {}

x = Int('x')
y = Int('y')
z = Int('z')

print(V)

s = Solver()

s.add(x > y, x > z)

print(s)
# base constraint for course table
print(s.check())