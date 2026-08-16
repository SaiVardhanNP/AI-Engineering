import numpy as np

marks = np.array([45, 60, 55, 60, 66, 30, 70])

marks_below_fifty = marks[marks < 50]

marks_above_fifty = marks[marks >= 50]

print(marks_above_fifty)
print(marks_below_fifty)

numbers = np.arange(20)

even_numbers = numbers[numbers % 2 == 0]
odd_numbers = numbers[numbers % 2 != 0]
numbers_above_ten = numbers[numbers > 10]

print(even_numbers)
print(odd_numbers)
print(numbers_above_ten)

scores = np.array([55, 67, 82, 91, 48, 73, 88])

mask = (scores >= 60) & (scores <= 85)
required_scores = scores[mask]

print(required_scores)


np.random.seed(42)

random_integers = np.random.randint(1, 101, size=10)
random_floats = np.random.rand(5)

print(random_integers)
print(random_floats)
