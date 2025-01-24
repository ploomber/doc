from fastapi import FastAPI, Request, Response
import httpx
from urllib.parse import urljoin
import json
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from contextlib import asynccontextmanager
import gzip
import zlib


analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await http_client.aclose()


app = FastAPI(lifespan=lifespan)

# Configuration
TARGET_URL = "https://api.openai.com"  # OpenAI API base URL
INTERCEPT_PATHS = [
    "/v1/chat/completions",  # Full path including v1 prefix
]  # Add paths you want to intercept

# Create a single httpx client to be reused with timeout settings
http_client = httpx.AsyncClient(timeout=30.0)


@app.middleware("http")
async def reverse_proxy(request: Request, call_next):
    """
    Reverse proxy middleware that intercepts and processes specific endpoints.

    Parameters
    ----------
    request : Request
        The incoming FastAPI request
    call_next : callable
        The next middleware in the chain

    Returns
    -------
    Response
        The response from either the intercepted endpoint or passed through
    """
    path = request.url.path

    # For root path, return a simple status message
    if path == "/":
        return Response(content="Proxy server is running", media_type="text/plain")

    try:
        # Normalize path by removing trailing slash if present
        path = path.rstrip("/")

        # If path doesn't need interception, pass through to target server
        if path not in INTERCEPT_PATHS:
            url = urljoin(TARGET_URL, path)  # Path already includes v1 prefix
            headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
            response = await http_client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

        # Handle intercepted paths
        if path in INTERCEPT_PATHS:
            # Preprocess the request here
            modified_body = await preprocess_request(request)

            # Update headers with new content length
            headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
            headers["content-length"] = str(len(modified_body))

            # Forward to target server
            url = urljoin(TARGET_URL, path)
            response = await http_client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=modified_body,
            )

            # Process the response if needed
            processed_response = await process_response(response)
            return processed_response

    except httpx.ReadTimeout:
        return Response(
            content="Request timed out while connecting to upstream server",
            status_code=504,
            media_type="text/plain",
        )
    except httpx.HTTPError as e:
        return Response(
            content=f"Error connecting to upstream server: {str(e)}",
            status_code=502,
            media_type="text/plain",
        )


def anonymize_text(text: str) -> str:
    """
    Anonymize sensitive information in text using Presidio.

    Parameters
    ----------
    text : str
        The input text to anonymize

    Returns
    -------
    str
        The anonymized text with sensitive information redacted
    """
    # Analyze text to find entities
    results = analyzer.analyze(text=text, entities=None, language="en")

    # Anonymize the identified entities
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)

    return anonymized.text


async def preprocess_request(request: Request):
    """
    Preprocess the intercepted request before forwarding.

    Parameters
    ----------
    request : Request
        The incoming request to process

    Returns
    -------
    bytes
        The processed request body
    """
    body = await request.body()

    try:
        body_json = json.loads(body)

        # Log original request
        print(f"Original request body: {json.dumps(body_json, indent=2)}")

        # Anonymize message contents if present
        if "messages" in body_json:
            for message in body_json["messages"]:
                if "content" in message:
                    original_content = message["content"]
                    message["content"] = anonymize_text(original_content)

        # Log anonymized request
        print(f"Anonymized request body: {json.dumps(body_json, indent=2)}")

        # Convert back to bytes
        return json.dumps(body_json).encode()

    except json.JSONDecodeError:
        # If not JSON, log raw body and return unchanged
        print(f"Intercepted request body: {body.decode()}")
        return body


async def process_response(response: httpx.Response):
    """
    Process the response from the target server, handling compression if present.

    Parameters
    ----------
    response : httpx.Response
        The response from the target server

    Returns
    -------
    Response
        The processed response
    """
    # Get the raw content and content encoding
    content = response.content
    content_encoding = response.headers.get("content-encoding", "").lower()

    # Decompress content if needed
    try:
        if content_encoding == "gzip":
            content = gzip.decompress(content)
        elif content_encoding == "deflate":
            content = zlib.decompress(content)

        # Try to parse and log the response
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            # Parse JSON from decompressed content
            response_json = json.loads(content.decode("utf-8"))
            print(f"Response body: {json.dumps(response_json, indent=2)}")
            content = json.dumps(response_json).encode("utf-8")
        else:
            # For non-JSON responses, try to log if it's text
            if any(
                text_type in content_type
                for text_type in ["text/", "application/javascript", "application/xml"]
            ):
                try:
                    print(f"Response body: {content.decode('utf-8')}")
                except UnicodeDecodeError:
                    print("Response body: [Could not decode text content]")
            else:
                print("Response body: [Binary content]")

    except Exception as e:
        print(f"Could not process response: {str(e)}")
        # If decompression or processing fails, return the original content
        content = response.content

    # Create response headers, preserving the original content-encoding
    headers = dict(response.headers)

    return Response(
        content=content,
        status_code=response.status_code,
        headers=headers,
        media_type=response.headers.get("content-type"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
