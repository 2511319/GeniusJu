# app.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse
from flask import Flask, make_response, request as flask_request

from config import ENV, db
from dash_app import create_dash_app

# 1) Основное FastAPI-приложение (ASGI)
app = FastAPI()  # ASGI для неблокирующей обработки множества запросов :contentReference[oaicite:4]{index=4}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}  # быстрый health-check без блокировок :contentReference[oaicite:5]{index=5}

@app.get("/")
async def root():
    return RedirectResponse(url="/dash/")  # редирект на Dash UI :contentReference[oaicite:6]{index=6}

# 2) Создаём Flask-сервер, на котором инициализируем Dash
flask_app = Flask(__name__)
dash_app = create_dash_app(flask_app)      # Mount Dash на Flask :contentReference[oaicite:7]{index=7}

# 3) Дополнительный маршрут для токена (идентификация пользователя)
@flask_app.route("/")
def dash_index():
    token = flask_request.args.get("token")
    if token and db:
        doc = db.collection('links').document(token).get()
        if doc.exists and not doc.to_dict().get("used", False):
            db.collection('links').document(token).update({"used": True})
            resp = make_response(dash_app.index())
            resp.set_cookie("user_token", token, httponly=True,
                            secure=True, max_age=7*24*3600, samesite="lax")
            return resp
    return dash_app.index()

# 4) # Монтируем на корень, чтобы Dash получал «чистый» путь
app.mount("/", WSGIMiddleware(flask_app))  # WSGI-middleware FastAPI :contentReference[oaicite:8]{index=8}

# 5) Запуск ASGI-сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=ENV in ("development", "local"),  # авто-перезагрузка в dev :contentReference[oaicite:9]{index=9}
        workers=4,                               # 4 воркера ASGI для продакшена :contentReference[oaicite:10]{index=10}
        log_level="info"
    )
