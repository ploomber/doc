FROM python:3.11

RUN pip install jupyter_kernel_gateway --no-cache-dir

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir


ENTRYPOINT ["jupyter", "kernelgateway", "--KernelGatewayApp.ip=0.0.0.0", "--KernelGatewayApp.port=80"]

