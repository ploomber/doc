# Debugging Docker build errors

## Installing PyTorch

If you're deploying Docker apps using a free account, your build might fail if it takes too many resources. To fix it, you can install the CPU-only version of PyTorch. Add the following to your `Dockerfile` *before* any packages that have PyTorch as a dependency

```Dockerfile
# install the cpu-only torch (or any other torch-related packages)
# you might modify it to install another version
RUN pip install torch==2.1.1 torchvision==0.16.1 --index-url https://download.pytorch.org/whl/cpu

# any packages that depend on pytorch must be installed after the previous RUN command
```

## Installing OpenCV

If you're using OpenCV and your application gets stuck during deployment, ensure you check the `Webservice logs`, if you're using a base image that doesn't have all dependencies required by OpenCV, you might run into issues like this one:

> libGL.so.1: cannot open shared object file

If that's the case, run the following before installing OpenCV, note that this requires your base image to use `apt` as its package manager. We recommend you using the `python:3.11` base image.

```Dockerfile
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
```