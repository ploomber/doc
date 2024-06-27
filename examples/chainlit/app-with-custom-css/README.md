# App with custom CSS

A basic Chainlit application for demonstrating custom CSS.

To customize the design of a Chainlit application, you need to use a custom CSS stylesheet and modify the configuration settings in the `.chainlit/config.toml` file.

**1. Create a custom stylesheet:**

* Create a file named `stylesheet.css` in a `public/` folder inside the application's root directory. 
* For example, to hide the footer in the Chainlit app add the below custom CSS as we have done in this example:

```css
a[href*='https://github.com/Chainlit/chainlit'] {
    visibility: hidden;
}
```

**2. Generate the Configuration File:** Run the command `chainlit init` or `chainlit run app.py` to generate the `.chainlit/config.toml` file.

**3. Modify the Configuration File:**

Once the file is generated, add the following setting:

```toml
[UI]
# ...
# This can either be a css file in your `public` dir or a URL
custom_css = '/public/stylesheet.css'
```

Here's how the UI section in our example `config.toml` looks like:

```toml
[UI]
# Name of the assistant.
name = "Assistant"

# Description of the assistant. This is used for HTML tags.
# description = ""

# Large size content are by default collapsed for a cleaner ui
default_collapse_content = true

# Hide the chain of thought details from the user in the UI.
hide_cot = false

# Link to your github repo. This will add a github button in the UI's header.
# github = ""

# Specify a CSS file that can be used to customize the user interface.
# The CSS file can be served from the public directory or via an external link.
custom_css = "/public/stylesheet.css"
...
...
```

## Deployment

To deploy the application to Ploomber Cloud, zip all the necessary files including the `public/` folder and the `.chainlit` folder. Here's an example zip command for Mac:

```bash
zip -r app.zip .
```

Follow the deployment [guide](https://docs.cloud.ploomber.io/en/latest/apps/chainlit.html) for deploying your app.

