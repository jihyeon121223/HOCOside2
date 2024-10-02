import os
#Python 기반의 웹 프레임워크, RESTful API를 구축할 수 있도록 설계, 비동기 처리, Gunicorn웹서버와 함께 사용
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from random import randint
from pydantic import BaseModel #유효성 검사, 타입의 제약조건 보장 라이브러리
from typing import Optional, List
from sqlalchemy import Column, Integer, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


app = FastAPI()

# BASE_DIR 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")
print("BASE_DIR:", BASE_DIR)
print("Templates Directory:", templates_dir)

# 인스턴스 생성
templates = Jinja2Templates(directory=templates_dir)


# ==============랜덤 함수
# @app.get("/")
# async def read_root(request: Request):
#     random_number = randint(1, 45)
#     return templates.TemplateResponse("index.html", {"request": request, "number": random_number})


# ==============openAPI
# 데이터 모델 정의(각 변수의 데이터 유형 결정, 자동으로 형식을 맞춰 변환)
# class Item(BaseModel):
#     name: str
#     description: Optional[str] = None
#     price: float
#     tax: Optional[float] = None

# # 생성
# @app.post("/items/", response_model=Item)
# async def create_item(item: Item):
#     return item

# # 조회
# @app.get("/items/{item_id}", response_model=Item)
# async def read_item(item_id: int, q: Optional[str] = None):
#     return {"name": f"Item {item_id}", "description": q, "price": 100.0, "tax": 12.5}


# ==============ORM사용 CRUD
DATABASE_URL = "sqlite:///./random_numbers.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 모델 정의
class RandomNumber(Base):
    __tablename__ = "random_numbers"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    # created_at = Column(DateTime, default=datetime.now(timezone.utc)) 

class RandomNumberResponse(BaseModel):
    id: int
    number: int

    class Config:
        orm_mode = True  # ORM 모드 활성화
        from_attributes = True  # ORM 객체에서 속성을 가져오기 위해 설정

# 디비 생성
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 페이지 (SSR)
@app.get("/", response_class=templates.TemplateResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    recent_random_number = db.query(RandomNumber).order_by(RandomNumber.id.desc()).first()  # id 기준으로 내림차순 정렬
    return templates.TemplateResponse("index.html", {"request": request, "recent_random_number": recent_random_number})

# 랜덤 숫자 생성 (C)
@app.post("/random-number/", response_model=RandomNumberResponse)
async def create_random_number(db: Session = Depends(get_db)):
    random_number = randint(1, 100)  # 1부터 100까지의 랜덤 숫자 생성
    db_random_number = RandomNumber(number=random_number)
    db.add(db_random_number)
    db.commit()
    db.refresh(db_random_number)
    return RandomNumberResponse.from_orm(db_random_number)

# 랜덤 숫자 수정 (U)
@app.put("/random-number/{number_id}", response_model=RandomNumberResponse)
async def update_random_number(number_id: int, db: Session = Depends(get_db)):
    db_random_number = db.query(RandomNumber).filter(RandomNumber.id == number_id).first()
    if db_random_number is None:
        raise HTTPException(status_code=404, detail="찾을 수 없습니다.")
    
    db_random_number.number = randint(1, 100)
    db.commit()
    db.refresh(db_random_number)
    return RandomNumberResponse.from_orm(db_random_number)

# 랜덤 숫자 삭제 (D)
@app.delete("/random-number/{number_id}")
async def delete_random_number(number_id: int, db: Session = Depends(get_db)):
    db_random_number = db.query(RandomNumber).filter(RandomNumber.id == number_id).first()
    if db_random_number is None:
        raise HTTPException(status_code=404, detail="찾을 수 없습니다.")
    db.delete(db_random_number)
    db.commit()
    return {"message": "삭제완료"}


# ==============디비 설계
