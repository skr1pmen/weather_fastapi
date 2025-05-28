from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import httpx
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecret")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

Base = declarative_base()
engine = create_engine("sqlite:///weather.db")
SessionLocal = sessionmaker(bind=engine)


class SearchHistory(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    city = Column(String)
    count = Column(Integer, default=1)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    last_city = request.session.get("last_city")
    weather_html = ""

    if last_city:
        async with httpx.AsyncClient() as client:
            geo = await client.get(f"https://geocoding-api.open-meteo.com/v1/search?name={last_city}&count=1")
            geo_data = geo.json()
            if geo_data.get("results"):
                lat = geo_data["results"][0]["latitude"]
                lon = geo_data["results"][0]["longitude"]
                weather = await client.get(
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                )
                weather_data = weather.json().get("current_weather", {})
                weather_html = f"""
                <div class="result">
                    <h2>{last_city}</h2>
                    <p><strong>Температура:</strong> {weather_data.get("temperature")}°C</p>
                    <p><strong>Скорость ветра:</strong> {weather_data.get("windspeed")} км/ч</p>
                </div>
                """

    return templates.TemplateResponse("index.html", {
        "request": request,
        "last_city": last_city or "",
        "weather_html": weather_html
    })


@app.post("/search", response_class=HTMLResponse)
async def search_weather(request: Request, city: str = Form(...), db: Session = Depends(get_db)):
    request.session["last_city"] = city

    history = db.query(SearchHistory).filter_by(city=city).first()
    if history:
        history.count += 1
    else:
        history = SearchHistory(city=city, count=1)
        db.add(history)
    db.commit()

    async with httpx.AsyncClient() as client:
        geo = await client.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1")
        geo_data = geo.json()
        if not geo_data.get("results"):
            return HTMLResponse('<div class="error">Город не найден</div>')

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        weather = await client.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather_data = weather.json().get("current_weather", {})

    return HTMLResponse(f"""
    <div class="result">
      <h2>{city}</h2>
      <p><strong>Температура:</strong> {weather_data.get("temperature")}°C</p>
      <p><strong>Скорость ветра:</strong> {weather_data.get("windspeed")} км/ч</p>
    </div>
    """)


@app.get("/autocomplete", response_class=JSONResponse)
async def autocomplete(q: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=5&language=ru")
        data = resp.json()
        suggestions = [r.get("name") or r.get("name_ascii") for r in data.get("results", [])]
        return JSONResponse(suggestions)


@app.get("/stats")
async def stats(db: Session = Depends(get_db)):
    history = db.query(SearchHistory).all()
    return {"search_stats": [{"city": h.city, "count": h.count} for h in history]}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
