from fastapi import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import requests
from dotenv import load_dotenv
import json
import subprocess
from typing import Annotated
from fastapi.staticfiles import StaticFiles
import random
import string
import requests
from pathlib import Path

os.makedirs('frames', exist_ok=True)
os.makedirs('temp', exist_ok=True)

app = FastAPI( 
    # Increase the payload size limit to 500 megabytes
    upload_max_size=500 * 1024 * 1024  # 500 MB
)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

static_folder = "frames"
app.mount("/frames", StaticFiles(directory=static_folder, html=True), name="frames")

@app.post("/api/frame_response/{id}")
async def frame_response(request: Request, file: UploadFile = File(...)):
    with open("return_image", "wb") as buffer:
        buffer.write(await file.read())
    

@app.post("/api/upload")
async def upload_video( id: str = Form(...), email: str = Form(...), file: UploadFile = File(...)):
    
    print(f"ID: {id}")

    folder_name = "frames/"+id

    #Create the name of the temporary video with a random string
    video_name = f"temp/{random_string(10)}.mp4"  # Specify the directory path for the temporary video file
    print(f"Video name: {video_name}")

    # Save the uploaded video file to a temporary location
    with open(video_name, "wb") as buffer:
        buffer.write(await file.read())


    os.makedirs(folder_name, exist_ok=True)

    # Use FFmpeg to extract frames from the video
    subprocess.run(["ffmpeg", "-i", video_name, f"{folder_name}/frame%d.jpg"])

    # Process the frames or perform any other required operations

    # Clean up the temporary video file and extracted frames
    # os.remove(video_name)
    # frame_files = os.listdir(folder_name)
    # for frame_file in frame_files:
    #     os.remove(os.path.join(folder_name, frame_file))
    # os.rmdir(folder_name)


    
    # Return a response
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        # "description": description,
        # "size": len(video_bytes)
    }

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))