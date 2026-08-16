import pandas as pd

students = pd.DataFrame(
    {
        "name": ["Alice", "Bob", "Charlie", "David", "Eva"],
        "cgpa": [8.7, 9.2, 7.9, 8.4, 9.0],
        "department": ["AI", "Web", "AI", "Cloud", "Web"],
        "placed": [True, True, False, True, True],
    }
)

print(students.info())
print(students.describe())
print(students.isnull().sum())
print(students.head())

print(students[students["cgpa"] > 8.5])

print(students[students["placed"] == True])

print(students[students["department"] == "AI"])

print(students.sort_values("cgpa", ascending=False))

students["percentage"] = students["cgpa"] * 9.5

print(students)

print(students.groupby("department")['cgpa'].mean())

students.to_csv("students_output.csv",index=False)