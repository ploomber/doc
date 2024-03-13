FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

RUN pip install jupyter_kernel_gateway ipykernel --no-cache-dir

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir


ENTRYPOINT ["jupyter", "kernelgateway", "--KernelGatewayApp.ip=0.0.0.0", "--KernelGatewayApp.port=80"]

