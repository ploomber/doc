# Document processing

```{important}
The document processing API is in beta and only available for PRO users. The API will
remain **free** during the beta period with a rate limit of 50 requests per day. If you
need a higher rate for your account, email us
[contact@ploomber.io](mailto:contact@ploomber.io)
```

You can use Ploomber Cloud's API to process PDFs and have them ready for LLM
processing. First, install the client:

```sh
pip install ploomber-cloud --upgrade
```

Ensure you set your [API key](../quickstart/apikey.md), and then you'll be able to use
the API:

```python
from ploomber_cloud import functions

# pass the path to the pdf file
result = functions.pdf_to_text("document.pdf")
```

`result` will be a list (one per page in the PDF) with the text.

By default, `functions.pdf_to_text` will wait until processing is done, you can pass
`block=False` to return immediately:

```python
jobid = functions.pdf_to_text("document.pdf", block=False)
```

Then, you can get the result:

```python
result = functions.get_result(jobid)
```