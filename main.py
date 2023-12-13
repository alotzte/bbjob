from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import Users, SessionLocal

app = FastAPI()

# Функция зависимости для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрут для получения всех пользователей
@app.get("/")
async def root(db: Session = Depends(get_db)):
    users = db.query(Users).get(0)
    return users