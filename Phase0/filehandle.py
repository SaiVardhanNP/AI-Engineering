import json

with open('notes.txt','a') as file:
    file.write("\nStart a company")

# task = {
#     "title": "Learn AI",
#     "priority": 100
# }

# with open('task.json','w') as file:
#     json.dump(task,file,indent=3)
    
with open('task.json','r') as file:
    task=json.load(file)

print(task['title'])