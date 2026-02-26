from fastapi import APIRouter, HTTPException, Query, Response, status
from typing import List, Optional
from schema import Task, TaskCreate, TaskUpdate, TaskStats
from utils import save, load, next_id
#imports fastapi, typing and pydantic classes from schema

router = APIRouter()
task_file = "tasks.txt"
memory = load(task_file)
#creates the router and defines task_file for easier access
#creates memory which loads from tasks.txt

#post method, responds with a Task
@router.post("/", response_model=Task)
#create task function, takes a Task based on TaskCreate input
def create_task(task: TaskCreate):
    #creates task by modeldumping and attaching the id & completion status
    new_task = {"id": next_id(memory), **task.model_dump(), "completed":False}
    #appends new task to memory
    memory.append(new_task)
    #try/except anything goes wrong with saving memory to disk
    try:
        #attempt to save memory to disk
        save(task_file, memory)
    #if saving fails: remove last entry and raise exception
    except Exception as e:
        memory.pop()
        raise HTTPException(status_code=500, detail=f"Failed to save task to disk ERROR: {e}")
    return new_task

#searches tasks by Name, returns all if no name is given
@router.get("/", response_model=List[Task])
def get_tasks(
    #defines input, applies query
    title: str | None = Query(None, description="Search by title"),
    completed: bool | None = Query(None, description="Filter by completion status")
    ):
    #defines results initial state
    results = memory
    #if statements to filter results based on title match & completion status
    if title:
        results = [t for t in results if title.lower() in t["title"].lower()]
    if completed is not None:
        results = [t for t in results if t["completed"] == completed]
    return results

@router.get("/completed", response_model=list[Task])
def get_completed_tasks():
    #filter memory for only items where completed is True
    return [t for t in memory if t["completed"] is True]

#defines statistics function
@router.get("/stats", response_model=TaskStats)
def get_task_stats():
    #length of memory will always be the amount of tasks
    total = len(memory)
    #iterate and return only completed task into a list, then calc length of list
    completed_count = len([t for t in memory if t.get("completed") is True])
    #total - number of completed = how many are open
    open_count = total - completed_count
    #divides completed by 100 and multiplies by number of tasks 
    #(as long as no /0, in which case percent = 0)
    percent = (completed_count / 100 * total) if total > 0 else 0.0
    #return calculated stats as dict
    return {
        "total": total,
        "completed": completed_count,
        "open_tasks": open_count,
        "percent_completed": round(percent, 2) # Round to 2 decimal places
    }

@router.get("/{tID}", response_model=Task)
def get_task_by_id(tID: int):
    #searches the memory, stopping at the first match
    task = next((u for u in memory if u["id"] == tID), None)
    #if no task is found:
    if not task:
        #HTTP exception 404
        raise HTTPException(status_code=404, detail="Task not found")
    return task

#patch call
@router.patch("/{tID}", response_model=Task)
#defines update function
def update_task(tID: int, updata: TaskUpdate):
    #finds the first matching ID, stores it as task_idx
    task_idx = next((i for i, u in enumerate(memory) if u["id"] == tID), None)
    #exception for when no matching id is found
    if task_idx is None:
        raise HTTPException(status_code=404, detail="Task not found")
    #defines 3 new dicts, which:
    #stored_task_data: store the found task
    #update_data: store the changes, excluding unmodified data
    #updated_task: store the full, updated task
    stored_task_data = memory[task_idx]
    update_data = updata.model_dump(exclude_unset=True)
    updated_task = {**stored_task_data, **update_data}
    #overwrites old task in memory to new task
    memory[task_idx] = updated_task
    try:
        #attempt to save memory to disk
        save(task_file, memory)
    #if saving fails: remove last entry and raise exception
    except Exception as e:
        memory.pop()
        raise HTTPException(status_code=500, detail=f"Failed to save task to disk ERROR: {e}")
    return updated_task

#defines global delete function
@router.delete("/")
def global_delete():
    #accesses the memory from outside function instead of assuming new variable
    global memory
    #saves memory into "backup"
    old_memory_backup = list(memory)
    #try/except for recovery
    try:
        #overrides task_file with empty list
        save(task_file, [])
        #wipes memory
        memory = []
    #if any exception happened:
    except Exception as e:
        #restore memory to backup
        memory = old_memory_backup
        #raises error
        raise HTTPException(status_code=500,detail=f"System failed to wipe disk. Operation aborted. Error: {e}")
    return {"message": "All tasks have been purged"}

#defines delete by ID function
@router.delete("/{tID}")
def delete_task(tID: int):
    #globalizes memory, so memory isnt assumed as new
    global memory
    #catalogues length of memory before deletion
    original_length = len(memory)
    #filters out tasks where ID = tID
    memory = [u for u in memory if u["id"] != tID]
    #if length = saved length, nothing was deleted
    if len(memory) == original_length:
        #raise exception for no task found
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        #attempt to save memory to disk
        save(task_file, memory)
    #if saving fails: remove last entry and raise exception
    except Exception as e:
        memory.pop()
        raise HTTPException(status_code=500, detail=f"Failed to save task to disk ERROR: {e}")
    return {"message": "Task deleted"}