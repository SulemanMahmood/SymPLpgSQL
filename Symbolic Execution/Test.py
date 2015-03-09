from CombinationGenerater import CombinationGenerator

C = CombinationGenerator(1,1)

A = C.getAllSinglePairs()
print(len(A))
print(A)

B = C.getAllTwoPairCombinations()
print(len(B))
print(B)

print(B[0][1] == A[1])

