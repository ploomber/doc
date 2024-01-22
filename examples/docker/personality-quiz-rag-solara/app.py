import solara
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter

from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack import Document

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_KEY')

questions = [
    {"text": "Do you feel more energized when surrounded by people?", "trait": "E"},
    {"text": "Do you often find solitude more refreshing than social gatherings?", "trait": "I"},
    {"text": "When faced with a problem, do you prefer discussing it with others?", "trait": "E"},
    {"text": "Do you tend to process your thoughts internally before you speak?", "trait": "I"},
    {"text": "At parties, do you initiate conversations with new people?", "trait": "E"},
    {"text": "Do you prefer spending weekends quietly at home rather than going out?", "trait": "I"},
    {"text": "Do you focus more on the details and facts of your immediate surroundings?", "trait": "S"},
    {"text": "Are you more interested in exploring abstract theories and future possibilities?", "trait": "N"},
    {"text": "In learning something new, do you prefer hands-on experience over theory?", "trait": "S"},
    {"text": "Do you often think about how actions today will affect the future?", "trait": "N"},
    {"text": "When planning a vacation, do you prefer having a detailed itinerary?", "trait": "S"},
    {"text": "Do you enjoy discussing symbolic or metaphorical interpretations of a story?", "trait": "N"},
    {"text": "When making decisions, do you prioritize logic over personal considerations?", "trait": "T"},
    {"text": "Are your decisions often influenced by how they will affect others emotionally?", "trait": "F"},
    {"text": "In arguments, do you focus more on being rational than on people's feelings?", "trait": "T"},
    {"text": "Do you strive to maintain harmony in group settings, even if it means compromising?", "trait": "F"},
    {"text": "Do you often rely on objective criteria to assess situations?", "trait": "T"},
    {"text": "When a friend is upset, is your first instinct to offer emotional support rather than solutions?", "trait": "F"},
    {"text": "Do you prefer to have a clear plan and dislike unexpected changes?", "trait": "J"},
    {"text": "Are you comfortable adapting to new situations as they happen?", "trait": "P"},
    {"text": "Do you set and stick to deadlines easily?", "trait": "J"},
    {"text": "Do you enjoy being spontaneous and keeping your options open?", "trait": "P"},
    {"text": "Do you find satisfaction in completing tasks and finalizing decisions?", "trait": "J"},
    {"text": "Do you prefer exploring various options before making a decision?", "trait": "P"},
]

def llm_pipeline(api_key):
    """
    This function creates an LLM-powered pipeline to determine someone's MBTI type.

    Parameters
    ----------
    api_key : str
        OpenAI API key

    Returns
    -------
    pipeline : Pipeline (Haystack)
        A pipeline that can be used to determine someone's MBTI type.
    """
    prompt_template = """
    Determine the personality of someone using the Myers-Briggs Type Indicator (MBTI) test. In this test,
    a user answers a series of questions using "Yes" and "No" responses. The questions are
    labelled according to the trait, where the traits are:
    E = Extraversion
    I = Introversion
    S = Sensing
    N = Intuition
    T = Thinking
    F = Feeling
    J = Judging
    P = Perceiving
    Please provide a concise explanation for your response and also provide insights into the personality type of the user. 
    In your description mention the defining characteristics of the personality type.
    If the documents do not contain the answer to the question, say that ‘Answer is unknown.’
    Context:
    {% for doc in documents %}
        Question: {{ doc.content }} Response: {{ doc.meta['answer'] }} Personality trait: {{doc.meta['trait']}} \n
    {% endfor %};
    Question: {{query}}
    \n
    """
    splitter = DocumentSplitter(split_length=100, split_overlap=5)
    prompt_builder = PromptBuilder(prompt_template)
    llm = OpenAIGenerator(api_key=api_key, 
                          model='gpt-4',
                          generation_kwargs={"temperature":0.1})

    pipeline = Pipeline()
    pipeline.add_component("splitter", splitter)
    pipeline.add_component(name="prompt_builder", instance=prompt_builder)
    pipeline.add_component(name="llm", instance=llm)
    pipeline.connect("splitter.documents", "prompt_builder.documents")
    pipeline.connect("prompt_builder", "llm")

    return pipeline

def generate_documents_from_responses(responses):
    """
    This function takes responses and generates Haystack Documents.

    Parameters
    ----------
    responses : list
        A list of responses to the MBTI questions. Each response is of type dict
        and has the following keys: 'text' (str), 'trait' (str), 'answer' (str).

    Returns
    -------
    documents : list
        A list of Haystack Documents.
    """
    for i, question in enumerate(questions):
        question['meta'] = {
            'trait': question['trait'],
            'answer': responses[i]
        }

    documents = [Document(content=question["text"], meta=question["meta"]) for question in questions]

    return documents

def calculate_mbti_scores(responses):
    """
    This function takes responses and calculates the MBTI scores.
    
    Parameters
    ----------
    responses : list
        A list of responses to the MBTI questions. Each response is of type dict
        and has the following keys: 'text' (str), 'trait' (str), 'answer' (str).
        
    Returns
    -------
    scores : dict
        A dictionary containing the MBTI scores for each trait.
    
    """
    if len(responses) != 24:
        raise ValueError("There must be exactly 24 responses.")

    # Mapping each response to its corresponding dichotomy
    # 'Yes' for the first trait in the dichotomy and 'No' for the second.
    dichotomy_map = {
        'E/I': [1, 0, 1, 0, 1, 0],
        'S/N': [1, 0, 1, 0, 1, 0],
        'T/F': [1, 0, 1, 0, 1, 0],
        'J/P': [1, 0, 1, 0, 1, 0]
    }

    # Initial scores
    scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}

    # Iterate through the responses and update scores
    for i, response in enumerate(responses):
        if i < 6:  # E/I questions
            trait = 'E' if response == 'Yes' else 'I'
            scores[trait] += dichotomy_map['E/I'][i % 6]
        elif i < 12:  # S/N questions
            trait = 'S' if response == 'Yes' else 'N'
            scores[trait] += dichotomy_map['S/N'][i % 6]
        elif i < 18:  # T/F questions
            trait = 'T' if response == 'Yes' else 'F'
            scores[trait] += dichotomy_map['T/F'][i % 6]
        else:  # J/P questions
            trait = 'J' if response == 'Yes' else 'P'
            scores[trait] += dichotomy_map['J/P'][i % 6]

    return scores

def classic_mbti(responses):
    """
    This function takes responses and determines the MBTI type using a classic decision-tree approach.
    
    Parameters
    ----------
    responses : list
        A list of responses to the MBTI questions. Each response is of type dict
        and has the following keys: 'text' (str), 'trait' (str), 'answer' (str).

    Returns
    -------
    mbti_type : str
        The MBTI type.

    """
    scores = calculate_mbti_scores(responses)
    # Process the scores to determine MBTI type
    mbti_type = ''
    for trait_pair in ['EI', 'SN', 'TF', 'JP']:
        trait1, trait2 = trait_pair
        if scores[trait1] >= scores[trait2]:
            mbti_type += trait1
        else:
            mbti_type += trait2
    return mbti_type

@solara.component
def QuestionComponent(question, on_answer, key, reset_flag):
    answer, set_answer = solara.use_state(None, key=key)

    solara.use_effect(lambda: set_answer(None), [reset_flag])

    def on_click(response):
        set_answer(response)
        on_answer(question, response)

    yes_style = {"background-color": "#030637", "color": "white"} if answer == "Yes" else {}
    no_style = {"background-color": "#030637", "color": "white"} if answer == "No" else {}

    return solara.Column([
        solara.Text(question["text"]),
        solara.Button("Yes", on_click=lambda: on_click("Yes"), style=yes_style),
        solara.Button("No", on_click=lambda: on_click("No"), style=no_style),
    ])



# Main Quiz component
@solara.component
def PersonalityQuiz():
    current_index, set_current_index = solara.use_state(0)
    responses, set_responses = solara.use_state([])
    mbti_result, set_mbti_result = solara.use_state("")
    is_processing, set_is_processing = solara.use_state(False)
    reset_flag, set_reset_flag = solara.use_state(False)  # Add a flag for reset status

    def reset_quiz():
        if not is_processing:  # Disable during processing
            set_current_index(0)
            set_responses([])
            set_mbti_result("")
            set_is_processing(False)
            set_reset_flag(True) 
       

    def handle_answer(question, answer):
        if not is_processing:  
            new_responses = responses[:]
            if current_index >= len(new_responses):
                new_responses.append(answer)
            else:
                new_responses[current_index] = answer
            set_responses(new_responses)
            if current_index < len(questions) - 1:
                set_current_index(current_index + 1)


    def on_back():
        if current_index > 0 and not is_processing:
            set_current_index(current_index - 1)

    def on_submit():
        set_is_processing(True)
        try:
            mbti_type_classic = classic_mbti(responses)
            pipeline = llm_pipeline(api_key)
            documents = generate_documents_from_responses(responses)
            query = "Based on the responses, what is this user's Myers-Briggs personality type?"
            answer = pipeline.run(data={'splitter': {'documents': documents}, "prompt_builder": {"query": query}})
            mbti_type_llm = answer['llm']['replies'][0]
            set_mbti_result(f"Your MBTI type:\n\n According to a deterministic approach: {mbti_type_classic}. \n\n According to an LLM-generated approach: {mbti_type_llm}")
        except ValueError as e:
            set_mbti_result(str(e))
        finally:
            set_is_processing(False)

    # Conditional elements based on state
    quiz_elements = []

    if mbti_result:
        # Show results and additional buttons if results are ready
        quiz_elements.append(ResultsComponent(mbti_result))
        quiz_elements.append(solara.Button("Reset quiz", on_click=reset_quiz, disabled=is_processing, style="margin-top: 1em;"))
        quiz_elements.append(solara.Button("Re-generate results (the LLM may take a few seconds)", on_click=on_submit, disabled=is_processing,style="margin-top: 1em;"))
    elif current_index < len(questions) or is_processing:
        # Show questions and navigation buttons
        quiz_elements.append(solara.Markdown(f"### Question {current_index + 1} out of 24"))
        quiz_elements.append(QuestionComponent(questions[current_index], handle_answer, key=current_index, reset_flag=reset_flag))
        # Disable submit button if not all questions are answered
        submit_disabled = len(responses) != len(questions) or is_processing

        quiz_elements.append(solara.Row([
            solara.Button("Back", on_click=on_back, disabled=current_index == 0 or is_processing),
            solara.Button("Submit", on_click=on_submit, disabled=submit_disabled),
            solara.Button("Reset Quiz", on_click=reset_quiz, disabled=is_processing)
        ], justify="space-between", style="margin-top: 1em;"))

        if is_processing:
            # Show processing message while results are being computed
            quiz_elements.append(solara.Markdown("Calculating your MBTI type through a deterministic and an LLM-based approach. Generation may take the LLM a few seconds... Please wait."))

    return solara.Column(quiz_elements, style="flex: 1; padding: 20px; margin: auto;")



@solara.component
def ResultsComponent(mbti_result):
    return solara.Markdown(f"{mbti_result}")

@solara.component
def Topbar():
    # Define the top bar style and content
    return solara.Row(
        [
            solara.Markdown("### Take the test to determine your MBTI personality type\n", 
                            style="color: #FFFFFF; font-size: 20px; padding: 10px;"),
            solara.Markdown("Note - the purpose  of this test is to assess the different responses between a deterministic and an LLM-based approach. \
                            The test is also not extensive nor should it be used to evaluate someone's personality. \
                            This application is hosted on Ploomber Cloud. To learn more about Ploomber Cloud, visit <a href='https://ploomber.io/' style='color:  #FFC800;'>Ploomber.io</a>.", 
                            style="color: #FFFFFF;padding: 10px;"),
        ],
        style="background-color: #3C0753; justify-content: center; align-items: center;"
    )

@solara.component
def Sidebar():
    return solara.Column([
        solara.Markdown("### About The Myers-Briggs Type Indicator (MBTI)", style="color: white; font-size: 1.2em;"),
        solara.Markdown("The Myers-Briggs Type Indicator (MBTI) is a widely recognized psychological tool \
                            designed by Isabel Myers and Katherine Briggs, \
                            drawing from Carl Jung's theory on personality types. \
                            It aims to categorize individuals into one of 16 distinct personality types, \
                            each with unique preferences and characteristics.", style="color: white"),
        solara.Markdown("In summary, the MBTI is a reflective tool that helps individuals understand \
                            their own personality, encompassing their likes, dislikes, strengths, weaknesses, \
                            potential career paths, and social compatibility. It is not intended to \
                            measure or diagnose psychological health but rather to facilitate \
                            personal insight and self-understanding.", style="color: white"),
        solara.Markdown("The MBTI measures four key dimensions of personality:", style="color: white"),
        solara.Markdown("* Extraversion (E) – Introversion (I): This dimension assesses how people interact \
                            with their environment, with extraverts being action-oriented and sociable, \
                                while introverts are contemplative and solitary.", style="color: white"),
        solara.Markdown("* Sensing (S) – Intuition (N): This looks at how individuals gather information, \
                        with sensors focusing on concrete facts and details, and intuitives \
                            looking at patterns and possibilities.", style="color: white"),
        solara.Markdown("* Thinking (T) – Feeling (F): This scale examines decision-making processes, \
                        with thinkers prioritizing \
                            objective data and logic, and feelers considering personal \
                            implications and emotions.", style="color: white"),
        solara.Markdown("* Judging (J) – Perceiving (P): This final dimension evaluates how people\
                        approach the external world, \
                            with judgers preferring order and decisiveness,\
                                while perceivers value flexibility and openness.", style="color: white"),
        solara.Markdown("The MBTI suggests that while everyone utilizes each dimension to \
                            some extent, individuals tend to \
                            have a dominant preference in each of the four categories,\
                                culminating in a specific personality type.", style="color: white"),
    solara.Markdown("### How is this application built", style="color: white"),
    solara.Markdown("This application is built using the following libraries and frameworks:", style="color: white"),
    solara.Markdown("* Front end: <a href='https://solara.dev/docs' style='color: #FFC800;'>Solara</a>", style="color: white"),
    solara.Markdown("* Back end: <a href='https://haystack.deepset.ai/' style='color: #FFC800;'>Haystack</a>", style="color: white"),
    solara.Markdown("* Deployment: <a href='https://ploomber.io/' style='color:  #FFC800;'>Ploomber Cloud</a>", style="color: white"),
        # Here you can add more information or links to how the application is built
    ], style="background-color: #910A67; color: #F0EDCF; padding: 1em; width: 550px; height: 175vh;")


# App layout
@solara.component
def Page():
    return solara.Column(
        [
            Topbar(),  # This will place the Topbar at the top of the page
            solara.Row([
                Sidebar(),
                PersonalityQuiz(),
            ])
        ],
        style="height: 100vh;"  # Set the height to fill the screen vertically
    )

@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)