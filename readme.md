# AI Video Filter Backend

The idea of this app is to create a backend api that takes a short video file uploaded to it, extracts every other frame, stores each frame in an S3 bucket, runs each frame through Stable Diffusion Img2Img using [Stable Diffusion API](www.stablediffusionapi.com) and my predefined settings for a cool animation style, and then returns a link to the video.

![Before](/og.gif)
![After](/transformed.gif)

More information on this video style can be found [here](https://www.linkedin.com/pulse/how-i-used-ai-make-animated-music-video-under-500-andreas-cary)

This repository is a work in progress.

# To Deploy On Lambda
First run these commands: 
```console
pip3 install -t dep -r requirements.txt
(cd dep; zip ../lambda_artifact.zip -r .)
zip lambda_artifact.zip -u main.py
```