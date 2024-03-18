# Describe Image backend

A backend API that generates description of an image.

## Testing locally

Run the below command to start the app:

```bash
uvicorn app:app
```

The below cURL request can be sent to generate the description. The image path is the local path of the image:

```bash
curl -X POST \
  -F "file=@image.jpg" 'http://127.0.0.1:8000/describe?question=what%27s%20in%20the%20image'
```