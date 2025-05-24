# app.py

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse, Response
from flask import Flask, make_response, request as flask_request

from config import ENV, db
from dash_app import create_dash_app
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache

# 1) Основное FastAPI-приложение (ASGI)
app = FastAPI()

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type:
        response.headers["Content-Security-Policy"] = "script-src 'self' 'unsafe-eval'; object-src 'self'"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return RedirectResponse(url="/dash/")

# 2) Создаём Flask-сервер, на котором инициализируем Dash
flask_app = Flask(__name__)

# Инициализация Long Callback Manager
cache = diskcache.Cache("./cache_directory") 
long_callback_manager = DiskcacheLongCallbackManager(cache)

# Передаем long_callback_manager в create_dash_app
dash_app = create_dash_app(flask_app, long_callback_manager=long_callback_manager)

# 3) Дополнительный маршрут для токена (идентификация пользователя)
@flask_app.route("/") # Обслуживает и / и /dash/ через WSGIMiddleware
def dash_index():
    token = flask_request.args.get("token")
    if token and db:
        doc_ref = db.collection('links').document(token)
        doc = doc_ref.get()
        if doc.exists and not doc.to_dict().get("used", False):
            doc_ref.update({"used": True})
            # Используем dash_app.index() для получения отрендеренного Dash layout
            resp = make_response(dash_app.index()) 
            resp.set_cookie("user_token", token, httponly=True,
                            secure=True, max_age=7*24*3600, samesite="lax")
            return resp
    return dash_app.index() # Возвращаем стандартный Dash index

# 4) Монтируем Flask-приложение (с Dash) в FastAPI
# Убедитесь, что path="/dash" соответствует url_base_pathname в create_dash_app, если вы его используете
# Если Dash обслуживается с корня Flask, то монтируем Flask-приложение на корень FastAPI
app.mount("/dash", WSGIMiddleware(flask_app)) # Путь /dash/ должен совпадать с routes_pathname_prefix и requests_pathname_prefix

# 5) Запуск ASGI-сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=ENV in ("development", "local"),
        workers=4 if ENV == "production" else 1, # Меньше воркеров для разработки
        log_level="info"
    )
