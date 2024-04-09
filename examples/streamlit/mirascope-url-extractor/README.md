# Mirascope URL Extractor

An app for extracting structured data from websites with Mirascope, Anthropic, and Streamlit.

## How to run

1. First, you'll need an Anthropic API key. You can following the [getting started](https://docs.anthropic.com/claude/reference/getting-started-with-the-api) guide to generate your key.
2. Then, you'll need to create a `.env` file and add the `ANTHROPIC_API_KEY` variable, which will be loaded by the app `Settings`.
3. Last, you'll need to install the app's dependencies. Run the following command (in a virual environment):

    ```bash
    pip install -r requirements.txt
    ```

4. Now you can run the app locally with the following command:

```bash
streamlit run app.py
```
