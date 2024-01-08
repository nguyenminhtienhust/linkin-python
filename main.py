
from fastapi import FastAPI
from database import connect
from fastapi import HTTPException
from database import create_user,initialize_db


app = FastAPI()

@app.post("/users/")
async def add_user(name: str, age: int):
    user_id = create_user(name, age)
    if user_id:
        return {"id": user_id, "name": name, "age": age}
    else:
        raise HTTPException(status_code=400, detail="User not created")




@app.on_event("startup")
async def startup_event():
    initialize_db()


