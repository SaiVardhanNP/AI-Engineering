import numpy as np

arr = np.array([1, 2, 3, 4, 5])

print(arr)

print(arr[0])

print(arr[-1])

print(arr[1:])

matrix = np.array([[1, 2, 3], [4, 5, 6]])
print(matrix.shape)
print(matrix.size)
print(matrix.dtype)
print(matrix.ndim)

zeros = np.zeros(4)

ones = np.ones(4)

sequence = np.arange(10).reshape(2, 5)

print(zeros)

print(ones)

print(sequence)

second_arr = np.array([10, 20, 30, 40, 50])

print(second_arr + 20)

print(second_arr * 2)

print(second_arr / 10)

a = np.array([1, 2, 3])
b = np.array([10, 20, 30])

print(a + b)
print(b - a)
print(a * b)

marks = np.array([65, 70, 80, 90])

marks = marks + 5

print(marks.mean())

print(marks.min())

print(marks.max())

print(marks.sum())


print(matrix.sum(axis=0))

A = np.array([
    [1,2],
    [3,4]
])

B = np.array([
    [2,0],
    [1,2]
])

print(A*B)

print(A@B)

print(matrix)
print(matrix.T)