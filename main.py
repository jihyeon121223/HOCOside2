import os
#Python 기반의 웹 프레임워크, RESTful API를 구축할 수 있도록 설계, 비동기 처리, Gunicorn웹서버와 함께 사용
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from random import randint
from pydantic import BaseModel #유효성 검사, 타입의 제약조건 보장 라이브러리
from typing import Optional

app = FastAPI()

# BASE_DIR 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")
print("BASE_DIR:", BASE_DIR)
print("Templates Directory:", templates_dir)

# 인스턴스 생성
templates = Jinja2Templates(directory=templates_dir)

# ==============랜덤 함수
@app.get("/")
async def read_root(request: Request):
    random_number = randint(1, 45)
    return templates.TemplateResponse("index.html", {"request": request, "number": random_number})

# ==============openAPI
# 데이터 모델 정의(각 변수의 데이터 유형 결정, 자동으로 형식을 맞춰 변환)
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# 생성
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item

# 조회
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int, q: Optional[str] = None):
    return {"name": f"Item {item_id}", "description": q, "price": 100.0, "tax": 12.5}


# 빨리해오면 디비서버 설계 알려준대