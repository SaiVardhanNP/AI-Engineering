from pydantic import BaseModel, ValidationError


class Student(BaseModel):
    name: str
    age: int
    cgpa: float
    placed: bool


first_student = Student(name="vardhan", age=20, cgpa=9.8, placed=True)

second_student = Student(name="jane", age="22", cgpa="9.8", placed="true")

print(first_student.name)
print(first_student.model_dump())


print(type(second_student.age))

try:
    Student(
        name=123,
        age="abc",
        cgpa="high",
        placed="yes"
    )
except ValidationError as e:
    print(e)