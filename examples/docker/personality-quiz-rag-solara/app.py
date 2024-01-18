import solara

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

def calculate_mbti_scores(responses):
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

# A component to display a question
@solara.component
def QuestionComponent(question, on_answer):
    text, set_text = solara.use_state("")

    def on_yes():
        on_answer(question, "Yes")

    def on_no():
        on_answer(question, "No")

    return solara.Column([
        solara.Text(question["text"]),
        solara.Button("Yes", on_click=on_yes),
        solara.Button("No", on_click=on_no)
    ])

# Main Quiz component
@solara.component
def PersonalityQuiz():
    current_index, set_current_index = solara.use_state(0)
    responses, set_responses = solara.use_state([])
    mbti_result, set_mbti_result = solara.use_state("")

    def handle_answer(question, answer):
        new_responses = responses[:]
        if current_index >= len(new_responses):
            new_responses.append(answer)
        else:
            new_responses[current_index] = answer
        set_responses(new_responses)
        if current_index < len(questions) - 1:
            set_current_index(current_index + 1)

    def on_back():
        if current_index > 0:
            set_current_index(current_index - 1)

    def on_submit():
        try:
            scores = calculate_mbti_scores(responses)
            # Process the scores to determine MBTI type
            mbti_type = ''
            for trait_pair in ['EI', 'SN', 'TF', 'JP']:
                trait1, trait2 = trait_pair
                if scores[trait1] >= scores[trait2]:
                    mbti_type += trait1
                else:
                    mbti_type += trait2
            set_mbti_result(f"Your MBTI type is: {mbti_type}")
        except ValueError as e:
            set_mbti_result(str(e))


    # Display the result or the next question
    if mbti_result is not None:
        return solara.Column([
            solara.Markdown(f"### Question {current_index + 1}"),
            QuestionComponent(questions[current_index], handle_answer),
            solara.Row([
                solara.Button("Back", on_click=on_back, disabled=current_index == 0),
                solara.Button("Next", on_click=lambda: set_current_index(current_index + 1), disabled=current_index == len(questions) - 1),
            ], justify="space-between", style="margin-top: 1em;"),
            solara.Button("Submit", on_click=on_submit, disabled=current_index != len(questions) - 1, style="margin-top: 1em;"),
            ResultsComponent(mbti_result)  # Add this line to display results
        ], style="flex: 1;")
    else:
        return solara.Column([
            solara.Markdown(f"### Question {current_index + 1}"),
            QuestionComponent(questions[current_index], handle_answer),
            solara.Row([
                solara.Button("Back", on_click=on_back, disabled=current_index == 0),
                solara.Button("Next", on_click=lambda: set_current_index(current_index + 1), disabled=current_index == len(questions) - 1),
            ], justify="space-between", style="margin-top: 1em;"),
            solara.Button("Submit", on_click=on_submit, disabled=current_index != len(questions) - 1, style="margin-top: 1em;")
        ], style="flex: 1;")


@solara.component
def ResultsComponent(mbti_result):
    return solara.Markdown(f"### Your results:\n\n{mbti_result}")


@solara.component
def Sidebar():
    return solara.Column([
        solara.Markdown("# About MBPT"),
        solara.Markdown("brief text on this personality test"),
        solara.Markdown("# How is this application built"),
        # Here you can add more information or links to how the application is built
    ], style="background-color: #333; color: white; padding: 1em; width: 250px; height: 100vh;")


# App layout
@solara.component
def Page():
    return solara.Row([
        Sidebar(),
        PersonalityQuiz(),
    ])

@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)