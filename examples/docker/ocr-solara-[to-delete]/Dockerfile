FROM python:3.11

COPY app.py app.py
COPY label.png label.png
RUN pip install torch==2.1.1 torchvision==0.16.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install solara easyocr



ENTRYPOINT ["solara", "run", "app.py", "--host=0.0.0.0", "--port=80"]