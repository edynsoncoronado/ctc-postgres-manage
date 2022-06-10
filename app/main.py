from fastapi import FastAPI
from worker import db_manage_backup, db_manage_restore1, db_manage_restore2, db_manage_restore3


app = FastAPI()


@app.get("/")
def root():
    return {'message': 'Hello World'}

@app.post("/backup")
async def process_backup():
    db_manage_backup.delay()
    return True

@app.post("/restore1")
async def process_backup():
    db_manage_restore1.delay()
    return True

@app.post("/restore2")
async def process_backup():
    db_manage_restore2.delay()
    return True

@app.post("/restore3")
async def process_backup():
    db_manage_restore3.delay()
    return True
