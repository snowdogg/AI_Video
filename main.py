from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from dotenv import load_dotenv
import json
import subprocess
import random
import string
import boto3
from botocore.exceptions import ClientError
from mangum import Mangum  # Import Mangum
from urllib.parse import urlparse
import time
from PIL import Image
import io
app = FastAPI()

# Load environment variables
load_dotenv()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://38.34.105.41:*"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Initialize S3 client
s3 = boto3.client("s3")

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/api/frame_response/{id}")
async def frame_response(request: Request, file: UploadFile = File(...)):
    with open("return_image", "wb") as buffer:
        buffer.write(await file.read())

@app.post("/api/upload")
async def upload_video(
    
    id: str = Form(...),
  
    file: UploadFile = File(...)
):
    timestamp_start = int(time.time())
    print(f"ID: {id}")

    temp_folder = f"temp/" 
    os.makedirs(temp_folder, exist_ok=True)

    # Create the name of the temporary video with a random string
    video_name = os.path.join(temp_folder, f"{random_string(10)}.mp4")  # Specify the directory path for the temporary video file
    print(f"Video name: {video_name}")

    # Save the uploaded video file to a temporary location
    with open(video_name, "wb") as buffer:
        buffer.write(await file.read())

    # Use FFmpeg to extract frames from the video
    frame_name = os.path.join(temp_folder, f"{random_string(10)}_frame%04d.jpg")
    subprocess.run(["ffmpeg", "-i", video_name, "-vf", "select='mod(n,2)'", "-q:v", "2", frame_name])

    # Upload each frame to Amazon S3
    frame_files = sorted(os.listdir(temp_folder))
    frame_urls = []
    bucket_name = os.getenv("s3bucketname")  # Replace with your S3 bucket name

    for frame_file in frame_files:
        # Skip the file if it's not a .jpg
        if not frame_file.endswith(".jpg"):
            continue

        frame_path = os.path.join(temp_folder, frame_file)
        frame_key = f"{frame_file}"
        print(frame_key)

        try:
            s3.upload_file(frame_path, bucket_name, frame_key)
            frame_url = f"https://{bucket_name}.s3.amazonaws.com/{frame_key}"
            frame_urls.append(frame_url)
        except ClientError as e:
            print(f"Error uploading {frame_file} to S3: {e}")


    # Clean up the temporary video file and extracted frames
    os.remove(video_name)
    for frame_file in frame_files:
        try:
            os.remove(os.path.join(temp_folder, frame_file))
        except Exception as e:
            print(f"Error deleting {frame_file} {str(e)}")
    

    i = 0
    stableDiffusionURL = "https://stablediffusionapi.com/api/v4/dreambooth/img2img"
    stableDiffusionKey = os.getenv("STABLE_DIFFUSION_API_KEY")
    # Return a response with frame URLs
    for frame_url in frame_urls:
        i += 1
        timestamp_now = int(time.time())
        print(f"Time elapsed: {timestamp_now - timestamp_start} seconds")
        body = {
            "key": stableDiffusionKey,
            "model_id": "synthwave-diffusion",
            "prompt": "animation, cowboy bebop, cel-shaded, anime, jrpg, cool, sunglasses, casino, las vegas",
            "negative_prompt": "text, disfigured face, disfigured limbs, disfigured fingers, too many limbs, too many, fingers, old, blurry, distorted, hair texture, extra fingers, random, fingers and digits, cracked face, wrinkles on forehead, distorted face, text, watermark, (deformed hands], extra hands,hand in tars shad-hands-5» watermark nolu, (child:1.5), ((((underage)))), ((((child)))), (((kid))), (((preteen))), (teen:1.5) ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face, blurry, draft, grainy",
            "guidance": 3.5,
            "init_image": frame_url,
            "safety_checker": None, 
            "width": "600",
            "height": "1080",
            "samples": 1,
            "steps": 20,
            "seed": 0,
            "strength": 0.2,
            "webhook": None,
            "track_id": None,
            "scheduler": "UniPCMultistepScheduler"
        }
        r = requests.post(stableDiffusionURL, json=body)
        print(r.status_code)
        
        print(r.json())
        
        json_response = r.json()
        while (json_response['status'] == 'error'):
            print('sleeping for a second')
            time.sleep(.5)
            r = requests.post(stableDiffusionURL, json=body)
            print(r.status_code)
            print(r.json())
            json_response = r.json()

        # Check if 'output' key exists and it's not an empty list
        if 'output' in json_response and json_response['output']:
            newFrameURL = json_response['output'][0]
        # If 'output' key doesn't exist or it's an empty list, check for 'fetch_result' key
        elif 'fetch_result' in json_response:
            newFrameURL = json_response['fetch_result']
        # If neither condition is met, raise an exception
        else:
            raise KeyError("'output' or 'fetch_result' key not found in JSON response")

        print(newFrameURL)
        save_new_image(newFrameURL, frame_url)
        print(f"{frame_url}")



    output_video_name = "output.mp4"  # Specify the name of the output video file
    
    command = [
        'ffmpeg',
        '-pattern_type', 'glob',
        '-i', '*.png',
        '-vf', 'setpts=2.0*PTS',
        '-r', '24',
        '-c:v', 'prores_ks',
        f"{random_string(10)}.mov"
    ]
    subprocess.run(command, capture_output=True, text=True)
    timestamp_end = int(time.time())
    print(f"Time taken: {timestamp_end - timestamp_start} seconds")
    delete_all_files_in_bucket(bucket_name)
    return {"frame_urls": frame_urls}

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))

#function to delete all files in the s3 bucket
def delete_all_files_in_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()

    return

#function to delete all

def save_new_image(newFrameURL, og_frame_url):
    try:
        # Send a GET request to the image's URL
        response = requests.get(newFrameURL)

        # Check if the request was successful
        while response.status_code != 200:
            print(f"Failed to download image at {newFrameURL} HTTP status code: {response.status_code}")
            print('sleeping for a second and trying again')
            time.sleep(1)
            response = requests.get(newFrameURL)
            

        parsed = urlparse(og_frame_url)
        file_key = parsed.path.lstrip('/')  # Remove the leading '/'

        # Path where the image will be saved
        save_path = os.path.join("temp", file_key)

        # Create a BytesIO object from the response content
        image_data = io.BytesIO(response.content)

        # Open the image data with PIL and convert to PNG
        img = Image.open(image_data)
        png_save_path = save_path.rsplit('.', 1)[0] + '.png'
        img.save(png_save_path, 'PNG')

    except Exception as e:
        print(f"Error occurred while saving image: {e}")
    return



# Mangum handler to run FastAPI on AWS Lambda
handler = Mangum(app)