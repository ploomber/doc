import solara 
from functools import partial

## agent definition
from haystack.nodes import WebSearch
from haystack.nodes import AnswerParser, PromptNode, PromptTemplate
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, PromptTemplate, AnswerParser, PromptNode
import os
from haystack.pipelines import Pipeline
from haystack.schema import Document
from typing import List 
from dotenv import load_dotenv
import os

css = """
    .main {
        width: 100%;
        height: 100%;
        max-width: 1200px;
        margin: auto;
        padding: 1em;
    }
    
    #app > div > div:nth-child(2) > div:nth-child(2) {
    display: none;
}
"""

# Load the API key from the .env file
load_dotenv(".env")
serperdev_api_key = os.getenv("SERPERDEV_API_KEY")
openai_key = os.getenv("OPENAI_KEY")


def document_store_and_pipeline(documents):
# Initialize Haystack's QA system
    document_store = InMemoryDocumentStore(use_bm25=True)
    document_store.write_documents(documents)


    rag_prompt = PromptTemplate(
        prompt="""Synthesize a brief answer from the following text for the given question.
                                Provide a clear and concise response that summarizes the key points and information presented in the text.
                                
                                \n\n Related text: {join(documents)} \n\n Question: {query} \n\n Answer:""",
        output_parser=AnswerParser(),
    )

    # Set up nodes
    retriever = BM25Retriever(document_store=document_store, top_k=5)
    pn = PromptNode("gpt-3.5-turbo", 
                    api_key=openai_key, 
                    model_kwargs={"stream":False},
                    default_prompt_template=rag_prompt)

    # Set up pipeline
    pipe = Pipeline()
    pipe.add_node(component=retriever, name="retriever", inputs=["Query"])
    pipe.add_node(component=pn, name="prompt_node", inputs=["retriever"])

    return pipe




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
        solara.Markdown("### Your Personalized Diet Plan"),
        solara.Markdown(diet_plan),
        solara.Markdown("### Your Personalized Workout Plan"),
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

    def on_clear():
        State.reset()


    def on_submit():
        process_data(weight, height, gender, body_type, activity_level, goal)

    return solara.Column(style="margin-top: 40px; width: 80%;", 
        children=[
        solara.InputFloat(label="Weight (kg)", value=weight, on_value=set_weight),
        solara.InputFloat(label="Height (cm)", value=height, on_value=set_height),
        solara.Select(label="Gender", values=["Male", "Female", "Other"], value=gender, on_value=set_gender),
        solara.Select(label="Body Type", values=["Ectomorph", "Mesomorph", "Endomorph"], value=body_type, on_value=set_body_type),
        solara.Select(label="Activity Level", values=["Sedentary", "Lightly active", "Moderately active", "Very active"], value=activity_level, on_value=set_activity_level),
        solara.Select(label="Goal", values=["Weight loss", "Muscle gain", "Fitness maintenance"], value=goal, on_value=set_goal),
        solara.Button("Submit", on_click=on_submit),
        solara.Button("Clear Results", on_click=on_clear)
    ])


def process_data(weight, height, gender, body_type, activity_level, goal):
    # Example logic for processing data and generating suggestions
    diet_plan = generate_diet_plan(weight, height, gender, activity_level, goal, body_type)
    workout_plan = generate_workout_plan(weight, height, gender, body_type, activity_level, goal)

    # Store the plans in a state to display them
    State.diet_plan.value = diet_plan
    State.workout_plan.value = workout_plan

def generate_workout_plan(weight, height, gender, body_type, activity_level, goal):
    search = WebSearch(api_key=serperdev_api_key)
    query = f"What is a good workout plan for someone who is {gender}, weighs {weight} kg, and is {height} cm tall, with {body_type} body type, whose activity level is {activity_level}, whose goal is to {goal}? Please include frequency and duration in your response."
    search_results = search.run(query=query, top_k=10)

    # Transform search results into Document objects
    documents = search_results[0]['documents']

    pipe = document_store_and_pipeline(documents)
    results = pipe.run(query=query, documents=documents)

    # Process results and return a formatted string
    answers = "\n".join([res.answer for res in results['answers']])
    title = "\n \n ".join([f"* {res.meta['title']}" for res in results['documents']])
    link =  "\n \n".join([f"* {res.meta['link']}" for res in results['documents']])
    formatted_results = f"Answer: {answers} \n\n Retrieved from: \n\n Titles: \n\n {title} \n\n Links: \n\n {link} \n\n "
    return formatted_results


def generate_diet_plan(weight, height, gender, activity_level, goal, body_type):
    search = WebSearch(api_key=serperdev_api_key)
    query = f"What is a good diet and nutrition plan for someone who is {gender}, \
        weighs {weight} kg, and is {height} cm tall, with {body_type} \
            body type, whose activity level is {activity_level}, \
                whose goal is to {goal}? Please include calorie and macro suggestion."
    search_results = search.run(query=query, top_k=10)

    # Transform search results into Document objects
    documents = search_results[0]['documents']

    pipe = document_store_and_pipeline(documents)
    results = pipe.run(query=query, documents=documents)

    # Process results and return a formatted string
    answers = "\n".join([res.answer for res in results['answers']])
    title = "\n \n ".join([f"* {res.meta['title']}" for res in results['documents']])
    link =  "\n \n".join([f"* {res.meta['link']}" for res in results['documents']])
    formatted_results = f"Answer: {answers} \n\n Retrieved from: \n\n Titles: \n\n {title} \n\n Links: \n\n {link} \n\n "
    return formatted_results

@solara.component
def Page():
    with solara.AppBarTitle():
        solara.Text("Personalized Diet and Workout Planner")


    
    return solara.Row(classes=["main"],style=css, 
                      children=[
                          
                        solara.Column([
                        solara.Markdown("# Welcome to Your Personalized Planner"),
                        solara.Markdown(
                            """
                            Welcome to your Personalized Diet and Workout Planner. 
                            Please input your details like weight, height, gender, body type, activity level, and goal 
                            to receive customized diet and workout plans.
                            """, style="margin-top: 20px; width: 80%;",
                        ),
                        solara.Markdown("Please enter your details to get started."),
                        user_input_form(),
                        solara.Markdown("App hosted in [Ploomber Cloud](https://ploomber.io/)")
                        
                    ]),
        solara.Row(classes=["main"],style=css, children=[
            solara.Column(
                style="margin-top: 40px; width: 150%;",
                children=[
                    solara.Markdown("# Your results"),
                    display_results()
                        ])
                ])
        ])

    

@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)