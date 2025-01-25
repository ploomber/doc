from flask import Flask, render_template, request, jsonify
from transformers import AutoTokenizer, pipeline
from markitdown import MarkItDown

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Prompt-Guard-86M")
classifier = pipeline("text-classification", model="meta-llama/Prompt-Guard-86M")
md = MarkItDown()


app = Flask(__name__)


def call_in_batches(callable, batches, batch_size):
    """
    Call a function in batches to prevent memory issues.
    """
    results = []

    for i in range(0, len(batches), batch_size):
        batch = batches[i : i + batch_size]
        batch_results = callable(batch)
        results.extend(batch_results)

    return results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process-text", methods=["POST"])
def process_text():
    text = request.json.get("text", "")
    lines = text.splitlines()
    responses = call_in_batches(classifier, lines, 4)

    for response, line in zip(responses, lines):
        response["input"] = line

    return render_template("text-results.html", responses=responses)


def predict_from_pdf(pdf_stream):
    # change for the path to the PDF
    result = md.convert_stream(pdf_stream)

    input_text = result.text_content
    chunks = []

    # max is 512 for the model but we're limiting to 256 to avoid memory issues
    max_length = 256

    input_ids = tokenizer.encode(input_text, add_special_tokens=False)

    for i in range(0, len(input_ids), max_length):
        chunk = input_ids[i : i + max_length]
        decoded_chunk = tokenizer.decode(chunk)
        chunks.append(decoded_chunk)

    responses = call_in_batches(classifier, chunks, 4)

    for response, chunk in zip(responses, chunks):
        response["input"] = chunk

    return responses


@app.route("/api/process-file", methods=["POST"])
def process_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    responses = predict_from_pdf(file)

    return render_template("text-results.html", responses=responses)


if __name__ == "__main__":
    app.run(debug=True)
