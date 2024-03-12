# Book Recommender

A chat assistant for recommending books to the user based on inputs.

![](screenshot.webp)

## Set key

To run this example you need to set the `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY=<your_api_key> 
```

## Dataset

Download the [dataset](https://www.kaggle.com/datasets/cristaliss/ultimate-book-collection-top-100-books-up-to-2023) to the `book-recommender/` folder, and rename it as `goodreads.csv`. 


## Generate lookup files

Generate lookup files by running the following script:

```bash
python generate_assets.py --embeddings --verbose
```

Running this command should generate `author_to_title.json`, `title_to_description.json` and `embeddings.json` files in the `assets/` folder.

If you want to generate embedding for the first N rows only run the below command (here N=100):

```bash
python generate_assets.py -n 100 --embeddings --verbose
```

## Weights and biases tracking

This application comes with weights and biases tracking. It is disabled by default. To enable it, go to `app.py` and set `WEIGHTS_AND_BIASES_TRACKING` = True.

You will also need to create an account in Weights and Biases. You can do this by visiting the [Weights and Biases website sign up page - it's free](https://wandb.ai/site/). You will need to generate an API key, which you can obtain after you log in by visiting [https://wandb.ai/authorize](https://wandb.ai/authorize). 

Once you log in, you can create a new project by visiting your user profile, selecting the project tab, and clicking on the "New Project" button. 

![](./images/new_project.png)

The app assumes the following environment variable names. Please store them somewhere safe, as you will need them later. You can set them as environment variables, or create a `.env` file with these values.

```bash
WANDB_API_KEY=your_api_key
WANDB_PROJECT=your_project_name
WANDB_ENTITY=your_user_name
```

Now, just run your app and then navigate to the project page. You should see logs tracking the responses of your app.

## Deployment

Create a zip of `app.py`, `util.py`, `_wandb.py`, `requirements.txt` and `assets/` folder, and follow the instructions for deploying a [Panel](https://docs.cloud.ploomber.io/en/latest/apps/panel.html) application.
You also need to set `OPENAI_API_KEY` as an [environment variable](https://docs.cloud.ploomber.io/en/latest/user-guide/env-vars.html) while deploying the application. If you have Weights and Biases tracking enabled, make sure you set those environment values as well.
