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
import asyncio
from dotenv import dotenv_values, load_dotenv
import uvicorn
import socket
load_dotenv()

STABLE_DIFFUSION_API_KEY=os.getenv("STABLE_DIFFUSION_API_KEY")
STABLE_DIFFUSION_API_IMG2IMG_ENDPOINT=os.getenv("STABLE_DIFFUSION_API_IMG2IMG_ENDPOINT")

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
app.mount("/frames", StaticFiles(directory="frames"), name="frames")

# Get the host IP
host_ip = socket.gethostbyname(socket.gethostname())

# Path to the file
file_path = "/path/to/file.txt"

# Create the string
result = f"http://{host_ip}/frames/ar1wmmvlyua8d6j53afnpr/frame2.jpg"
print(result)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

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

    # # Create a Semaphore with a limit of 5 requests per second
    # semaphore = asyncio.Semaphore(5)

    # async def limit_requests():
    #     async with semaphore:
    #         # Perform your API request here
    #         # ...

    #         # Simulate some processing time
    #         await asyncio.sleep(0.1)  # Adjust the sleep duration as per your needs

    # # Call the limit_requests function whenever you want to make a request
    # asyncio.run(limit_requests())

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

