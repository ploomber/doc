# Document processing

```{important}
The serverless functions is free while in beta. Community users get 10 calls per day,
PRO users get 100 calls per day.
```

You can use Ploomber Cloud's API to process PDFs and have them ready for LLM
processing. First, install the client:

```sh
pip install ploomber-cloud --upgrade
```

```{important}
Ensure you're running the latest version of `ploomber-cloud` since the API will change
over the beta period.
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