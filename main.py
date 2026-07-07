import os
import uuid
import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rembg import remove
from PIL import Image
import io

app = FastAPI()

os.makedirs("static", exist_ok=True)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/remove-bg")
async def remove_bg(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    input_image = Image.open(io.BytesIO(contents))
    output = remove(input_image)
    filename = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join("static", filename)
    output.save(output_path)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": f"/static/{filename}",
        "original": file.filename
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
