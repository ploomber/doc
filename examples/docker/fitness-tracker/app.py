import solara 
from functools import partial

## agent definition
from haystack.nodes import WebSearch
from haystack.nodes.search_engine import WebSearch
from haystack.schema import Document
from typing import List 
from dotenv import load_dotenv
import os

# Load the API key from the .env file
load_dotenv(".env")
serperdev_api_key = os.getenv("SERPERDEV_API_KEY")

# Let's configure the web search to user SerperDev as the search engine provider
# SerperDev is the default provider, so we just need the API key
search = WebSearch(api_key=serperdev_api_key)

# This search uses the default SerperDev provider, so we just need the API key
ws = WebSearch(api_key=serperdev_api_key)
documents: List[Document] = search.run(query="What's the meaning of life?")


class State:
    diet_plan = solara.reactive("")
    workout_plan = solara.reactive("")

    @staticmethod
    def load_sample():
        # Example loading sample data logic
        # You should replace this with your actual data loading logic
        State.diet_plan.value = "Sample Diet Plan"
        State.workout_plan.value = "Sample Workout Plan"

    @staticmethod
    def reset():
        # Reset the state values
        State.diet_plan.value = ""
        State.workout_plan.value = ""

def display_results():
    diet_plan = State.diet_plan.value
    workout_plan = State.workout_plan.value

    return solara.Column([
        solara.Markdown("## Your Personalized Diet Plan"),
        solara.Markdown(diet_plan),
        solara.Markdown("## Your Personalized Workout Plan"),
        solara.Markdown(workout_plan)
    ])

@solara.component
def user_input_form():
    weight, set_weight = solara.use_state(0)
    height, set_height = solara.use_state(0)
    age, set_age = solara.use_state(0)
    gender, set_gender = solara.use_state("")
    body_type, set_body_type = solara.use_state("")
    activity_level, set_activity_level = solara.use_state("")
    goal, set_goal = solara.use_state("")

    def on_submit():
        process_data(weight, height, gender, body_type, activity_level, goal)

    return solara.Column(style="margin-top: 20px; width: 40%;", 
        children=[
        solara.InputFloat(label="Weight (kg)", value=weight, on_value=set_weight),
        solara.InputFloat(label="Height (cm)", value=height, on_value=set_height),
        solara.Select(label="Gender", values=["Male", "Female", "Other"], value=gender, on_value=set_gender),
        solara.Select(label="Body Type", values=["Ectomorph", "Mesomorph", "Endomorph"], value=body_type, on_value=set_body_type),
        solara.Select(label="Activity Level", values=["Sedentary", "Lightly active", "Moderately active", "Very active"], value=activity_level, on_value=set_activity_level),
        solara.Select(label="Goal", values=["Weight loss", "Muscle gain", "Fitness maintenance"], value=goal, on_value=set_goal),
        solara.Button("Submit", on_click=on_submit)
    ])


def process_data(weight, height, gender, body_type, activity_level, goal):
    # Example logic for processing data and generating suggestions
    diet_plan = generate_diet_plan(weight, height, gender, activity_level, goal)
    workout_plan = generate_workout_plan(weight, height, gender, body_type, activity_level, goal)

    # Store the plans in a state to display them
    State.diet_plan.value = diet_plan
    State.workout_plan.value = workout_plan

def generate_workout_plan(weight, height, gender, body_type, activity_level, goal):
    # Logic to generate a workout plan
    # ...
    # This is a placeholder for the actual logic to generate a workout plan
    return "Workout plan based on your inputs..."

def generate_diet_plan(weight, height, gender, activity_level, goal):
    # ...
    # This is a placeholder for the actual logic to generate a diet plan
    return "Diet plan based on your inputs..."

@solara.component
def Page():
    with solara.AppBarTitle():
        solara.Text("Personalized Diet and Workout Planner")

    with solara.Card(title="About", elevation=6, style="background-color: #f5f5f5;"):
        solara.Markdown(
            """
            Welcome to your Personalized Diet and Workout Planner. 
            Please input your details like weight, height, gender, body type, activity level, and goal 
            to receive customized diet and workout plans.
            """
        )

    with solara.Sidebar():
        with solara.Card("Controls", margin=0, elevation=0):
            with solara.Column():
                solara.Button(
                    "Load Example Data", 
                    color="primary", 
                    text=True, 
                    outlined=True, 
                    on_click=State.load_sample
                )
                solara.Button(
                    "Reset Data", 
                    color="primary", 
                    text=True, 
                    outlined=True, 
                    on_click=State.reset
                )
                solara.Markdown("Hosted in [Ploomber Cloud](https://ploomber.io/)")

    return solara.Column([
        solara.Markdown("# Welcome to Your Personalized Planner"),
        solara.Markdown("Please enter your details to get started."),
        user_input_form(),
        display_results()
    ])

@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)