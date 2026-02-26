from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
#imports for fastapi and pydantic

#pydantic base model to be inherited from, verfies title and description data
class TaskBase(BaseModel):
    title: str
    description: str | None = None

#Task class, defines what a task is by adding id & completed bool to the Base it inherits from
class Task(TaskBase):
    id: int
    completed: bool = False

#creation class, matches & inherits from TaskBase for now
class TaskCreate(TaskBase):
    pass

#update class, inherits from Base, adds completed, but allows both inputs to be null
class TaskUpdate(TaskBase):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

#stats class, seperate data entity for the statistics call
class TaskStats(BaseModel):
    total: int
    completed: int
    open_tasks: int
    percent_completed: float