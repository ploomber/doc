# WASM Apps

```{note}
To develop WASM apps, use our [AI editor.](https://editor.ploomber.io/editor/new)
```

WASM applications run entirely in the browser and do not count towards your app or
compute quota. You can deploy as many as you want.

## What is WASM?

WASM is a new technology that allows running Python and other programming languages
directly in web browsers. Traditional browsers can only execute JavaScript code,
but WASM removes this limitation.

## How is it different than a regular app?

Regular applications use a client-server architecture where the browser (client) sends
requests to a server when users interact with the app, like clicking buttons. The
server then processes these requests and sends back responses. WASM apps work
differently - instead of sending requests to a server, the application code runs
directly in the user's browser.

## Limitations

WASM apps have some important limitations. The source code is visible to users, making
them unsuitable for applications that use sensitive information like API keys. Not all
Python libraries are compatible with WASM. The apps take longer to start up
initially (since all libraries must be installed), and their performance depends on
the user's computer specifications.