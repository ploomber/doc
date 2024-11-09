# WASM Apps

WASM applications run entirely in the browser and do not count towards your app or
compute quota. You can deploy as many as you want.

## What is WASM?

- wasm is a new technology that allows running Python (among other languages) in the browser
- without WASM, browsers are constrained and can only execute Javascript

## How is it different than a regular app?

- a regular application has a server and a client (the browser)
- the client sends requests triggered by user interactions (e.g. user clicked a button)
- the server processes the request and returns an answer (e.g the result of an operation)
- in WASM apps, the source code is passed to the client (the browser) and executed locally

## Limitations

- source code is visible to the client (hence, not recommended when using API keys or any other secrets)
- not all python libraries work
- slower startup times
- performance depends on the client's computer