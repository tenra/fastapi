from fastapi import FastAPI
from typing import List  # ネストされたBodyを定義するために必要
from starlette.middleware.cors import CORSMiddleware  # CORSを回避するために必要
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from db import session  # DBと接続するためのセッション
from model import UserTable, User  # 今回使うモデルをインポート

app = FastAPI(
    title='FastAPIvvvでつくるtoDoアプリ',
    description='FastAPIチュートリアル：FastAPI(とstarlette)でシンプルなtoDoアプリを作りましょう．',
    version='0.9 beta'
)

# CORSを回避するために設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------APIの実装------------
templates = Jinja2Templates(directory="templates")
jinja_env = templates.env

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get("/admin")
async def admin(request: Request):
    return templates.TemplateResponse('admin.html',
                                      {'request': request,
                                       'username': 'admin'})

# テーブルにいる全ユーザ情報を取得 GET
@app.get("/users")
async def read_users(request: Request):
    users = session.query(UserTable).all()
    return templates.TemplateResponse('users.html',
                                     {'request': request,
                                      'users': users})

# idにマッチするユーザ情報を取得 GET
@app.get("/users/{user_id}")
async def read_user(request: Request, user_id: int):
    user = session.query(UserTable).filter(UserTable.id == user_id).first()
    return templates.TemplateResponse('user.html',
                                     {'request': request,
                                      'user': user})

# ユーザ情報を登録 POST
@app.post("/user")
# クエリでnameとstrを受け取る
# /user?name="三郎"&age=10
async def create_user(name: str, age: int, email: str, password: str):
    user = UserTable()
    user.name = name
    user.email = email
    user.password = password
    user.age = age
    session.add(user)
    session.commit()

# 複数のユーザ情報を更新 PUT
@app.put("/users")
# modelで定義したUserモデルのリクエストbodyをリストに入れた形で受け取る
# users=[{"id": 1, "name": "一郎", "age": 16},{"id": 2, "name": "二郎", "age": 20}]
async def update_users(users: List[User]):
    for new_user in users:
        user = session.query(UserTable).\
            filter(UserTable.id == new_user.id).first()
        user.name = new_user.name
        user.age = new_user.age
        user.email = new_user.email
        user.password = new_user.password
        session.commit()
