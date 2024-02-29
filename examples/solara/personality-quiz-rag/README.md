# Personality Quiz

A RAG application to deduce user's Myers-Briggs personality type from answers to quiz questions.

## How to run this application locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure you have an OpenAI API key and save it into a `.env` file


### 3. Run the application

```bash
solara run app.py
```

### Navigate to the application

A web browser window should automatically open to the application. If it does not, navigate to http://localhost:8765 in your web browser.

## Deploying this application on Ploomber Cloud

Ensure you have an account and an API key. Refer to the [documentation on creating an account](https://docs.cloud.ploomber.io/en/latest/quickstart/signup.html) and [documentation on generating an API key](https://docs.cloud.ploomber.io/en/latest/quickstart/apikey.html) for more details.

### 1. Install Ploomber Cloud's CLI

```bash
pip install ploomber-cloud
```

### 2. Connect your API key

```bash
ploomber-cloud key YOURKEY
```

### 3. Initialize your app

```bash
ploomber-cloud init
```

### 4. Deploy your app

```bash
ploomber-cloud deploy
```