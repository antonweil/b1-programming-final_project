from fastapi import FastAPI, HTTPException
from schema import Task, TaskUpdate
import json
import os

#load data function, returns a list of dictionaries
def load(filepath:str) -> list[dict]:
    #checks if filepath is real, raises exception is not, process stops
    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail="Internal server error: File does not exist")
    #defines the list to be populated
    tasks = []
    #error handling for any IOError
    try:
        #open the file, read mode, universial encoding standard
        with open(filepath, "r", encoding="utf-8") as f:
            #iterate through lines, returning number & the line
            for line_number, line in enumerate(f, 1):
                #strips lines
                clean_line = line.strip()
                #skip lines that couldnt be stripped
                if not clean_line:
                    continue
                #turn line into dictionary and append to tasks. 
                #try/except for json errors, skip accordingly
                try:
                    tasks.append(json.loads(clean_line))
                except json.JSONDecodeError as e:
                    print(f"JSON Error on line {line_number}: {e}")
                    continue
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Could not read file: {str(e)}")
    return tasks

#save function, takes file and content and writes content into file, returns null
def save(filepath: str, content: list[dict]) -> None:
    #try/except for any IOErrors
    try:
        #open the file, write mode, universial encoding standard
        with open(filepath, "w", encoding="utf-8") as f:
            #iterates through the content, dumping lines as strings 
            #into json record which is then written into the file
            for line in content:
                json_record = json.dumps(line)
                f.write(json_record + "\n")
    except IOError as e:
        print(f"Could not write to {filepath}: {e}")

#modify function, which takes the list of tasks "memory", 
#a specific task and the changes to be made then modifies within memory
def modify(tasks: list[Task], tID: int, updates: TaskUpdate) -> Task | None:
    #iterate through tasks
    for task in tasks:
        #check if ID matches given ID
        if tID == task.id:
            #sets new data through dump, excluding non modified data
            update_data = updates.model_dump(exclude_unset=True)
            #for each task, the loop runs for the number of changed fields
            for key, value in update_data.items():
                #sets old value of task to new value by finding it with the key
                setattr(task, key, value)
            return task
    return None

def next_id(tasks: list[Task]):
    return len(tasks)+1