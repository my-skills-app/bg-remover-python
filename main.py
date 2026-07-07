import os
import uuid
import threading
import uvicorn
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rembg import remove, new_session
from PIL import Image
import io

app = FastAPI()
session = None

os.makedirs("static", exist_ok=True)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def load_model():
    global session
    threading.Thread(target=lambda: setattr(app, "_model_loaded", True) or new_session(), daemon=True).start()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/remove-bg")
async def remove_bg(request: Request, file: UploadFile = File(...)):
    global session
    if session is None:
        session = new_session()
    contents = await file.read()
    input_image = Image.open(io.BytesIO(contents))
    output = remove(input_image, session=session)
    filename = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join("static", filename)
    output.save(output_path)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": f"/static/{filename}",
        "original": file.filename
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
