from fastapi import FastAPI
from routes import crud
#imports from fastapi and the crud operations

#creates the FastAPI app, with title,l desc and version
app = FastAPI(
    title = "Task Management API",
    description = "FastAPI Backend for managing tasks",
    version = "1.0.0"
)
#attach tasks.py to website
app.include_router(crud.router, prefix="/tasks", tags=["Tasks"])

#health check, as message is only returned when the API is functioning
@app.get("/")
def root_health_check():
    return {"status":"healthy", "message":"API is running"}