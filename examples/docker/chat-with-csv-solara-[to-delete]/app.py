import uuid
import requests
from functools import partial

import openai
import solara
import solara.lab
from solara.components.file_drop import FileDrop

from sql import inspect
from sql.run import run
from sqlalchemy import create_engine
from sql.connection import SQLAlchemyConnection
from sql.magic import SqlMagic, load_ipython_extension
from IPython.core.interactiveshell import InteractiveShell
from sql.plot import boxplot, histogram
from sqlalchemy.exc import ProgrammingError

from chat import *

from matplotlib import pyplot as plt

plt.switch_backend("agg")

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

openai.api_key = "YOUR_API_KEY"

prompt_template = """
This is the schema for the my_data table:

{}

I'll start prompting you and I want you to return SQL code.

If you're asked to plot a histogram, you can return: %sqlplot histogram NAME
If you're asked to plot a boxplot, you can return: %sqlplot boxplot NAME

If you're asked to plot a histogram for rows where column=value, you can 
return %sql --save snippet SELECT rows where column=value; %sqlplot histogram --table snippet --column NAME

If you're asked to plot a boxplot for rows where column=value, you can 
return %sql --save snippet SELECT rows where column=value; %sqlplot boxplot --table snippet --column NAME

And replace NAME with the column name, do not include the table  name
"""


def gen_name():
    return str(uuid.uuid4())[:8] + ".csv"


def load_data(name):
    run.run_statements(conn, "drop table if exists my_data", sqlmagic)
    run.run_statements(
        conn, f"create table my_data as (select * from '{name}')", sqlmagic
    )
    cols = inspect.get_columns("my_data")
    return cols


def delete_data():
    run.run_statements(conn, "drop table if exists my_data", sqlmagic)


ip = InteractiveShell()

sqlmagic = SqlMagic(shell=ip)
sqlmagic.feedback = 1
sqlmagic.autopandas = True
load_ipython_extension(ip)

conn = SQLAlchemyConnection(create_engine("duckdb://"), config=sqlmagic)


class State:
    initial_prompt = solara.reactive("")
    sample_data_loaded = solara.reactive(False)
    upload_data = solara.reactive(False)
    upload_data_error = solara.reactive("")
    results = solara.reactive(20)
    input = solara.reactive("")
    loading_data = solara.reactive(False)

    @staticmethod
    def load_sample():
        State.reset()
        name = gen_name()
        State.loading_data.value = True
        url = (
            "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
        )
        response = requests.get(url)
        if response.status_code == 200:
            with open(name, "wb") as f:
                f.write(response.content)
            cols = load_data(name)
            State.sample_data_loaded.value = True
            State.loading_data.value = False
            State.initial_prompt.value = prompt_template.format(cols)
        else:
            solara.Warning("Failed to fetch the data. Check the URL and try again.")

    @staticmethod
    def load_from_file(file):
        if not file["name"].endswith(".csv"):
            State.upload_data_error.value = "Only csv files are supported"
            return
        State.reset()
        name = gen_name()
        State.loading_data.value = True
        try:
            df = pd.read_csv(file["file_obj"])
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.replace(" ", "_")
            df.to_csv(name, index=False)
            cols = load_data(name)
            State.upload_data.value = True
            State.loading_data.value = False
            State.initial_prompt.value = prompt_template.format(cols)
        except Exception as e:
            State.upload_data_error.value = str(e)
            return
        State.upload_data_error.value = ""

    @staticmethod
    def reset():
        State.sample_data_loaded.value = False
        State.upload_data.value = False
        delete_data()
        State.initial_prompt.value = ""
        State.upload_data_error.value = ""

    @staticmethod
    def chat_with_gpt3(prompts):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": State.initial_prompt.value},
                {"role": "user", "content": "Show me the first 5 rows"},
                {"role": "assistant", "content": "SELECT * FROM my_data LIMIT 5"},
            ]
            + [{"role": prompt.role, "content": prompt.content} for prompt in prompts],
            temperature=0.1,
            stream=True,
        )

        total = ""
        for chunk in response:
            part = chunk["choices"][0]["delta"].get("content", "")
            total += part
            yield total


@solara.component
def Chat() -> None:
    solara.Style(
        """
        .chat-input {
            max-width: 800px;
        })
    """
    )

    messages, set_messages = solara.use_state(
        [
            Message(
                role="assistant",
                content=f"Welcome. Please post your queries!",
                df=None,
                fig=None,
            )
        ]
    )
    input, set_input = solara.use_state("")

    def ask_chatgpt():
        input = State.input.value
        _messages = messages + [Message(role="user", content=input, df=None, fig=None)]
        user_input = input
        set_input("")
        State.input.value = ""
        set_messages(_messages)
        if State.initial_prompt.value:
            final = None
            for command in State.chat_with_gpt3(
                [Message(role="user", content=user_input, df=None, fig=None)]
            ):
                final = command

            if ";" in final:
                queries = final.split(";")
            else:
                queries = [final]

            print(queries)

            for query in queries:
                query = query.strip()
                set_messages(
                    _messages
                    + [Message(role="assistant", content=query, df=None, fig=None)]
                )
                if "--save" in query:
                    error = "Sorry, we couldn't create a data subset"
                    try:
                        snippet_index = query.find("--save snippet")
                        sql_query = query[
                            snippet_index + len("--save snippet ") :
                        ].strip()
                        print(
                            f"Running temp table creation : CREATE TABLE snippet as ({sql_query})"
                        )
                        query_result = run.run_statements(
                            conn,
                            f"DROP TABLE IF EXISTS snippet; CREATE TABLE snippet as "
                            f"({sql_query})",
                            sqlmagic,
                        )
                        set_messages(
                            _messages
                            + [
                                Message(
                                    role="assistant",
                                    content=sql_query,
                                    df=query_result,
                                    fig=None,
                                )
                            ]
                        )
                    except ProgrammingError as e:
                        set_messages(
                            _messages
                            + [
                                Message(
                                    role="assistant",
                                    content=f"{query} {error} {str(e)}",
                                    df=None,
                                    fig=None,
                                )
                            ]
                        )
                    except Exception as e:
                        set_messages(
                            _messages
                            + [
                                Message(
                                    role="assistant",
                                    content=f"{query} {error} {str(e)}",
                                    df=None,
                                    fig=None,
                                )
                            ]
                        )

                elif query.startswith("%sqlplot"):
                    try:
                        args = query.split(" ")
                        if len(args) == 3:
                            name = args[1]
                            table = "my_data"
                            column = args[2]
                        else:
                            name = args[1]
                            table = args[3]
                            column = args[5]

                    except Exception as e:
                        error_message = (
                            "Sorry, we couldn't run your query on the data. "
                            "Please ensure you specify a relevant column."
                        )
                        set_messages(
                            _messages
                            + [
                                Message(
                                    role="assistant",
                                    content=f"{error_message}",
                                    df=None,
                                    fig=None,
                                )
                            ]
                        )
                        return

                    fig = Figure()
                    ax = fig.subplots()

                    fn_map = {
                        "histogram": partial(histogram, bins=50),
                        "boxplot": boxplot,
                    }

                    fn = fn_map[name]
                    try:
                        ax = fn(table, column=column, ax=ax)
                        set_messages(
                            _messages
                            + [Message(role="assistant", content="", df=None, fig=fig)]
                        )
                    except Exception as e:
                        print(e)
                        set_messages(
                            _messages
                            + [
                                Message(
                                    role="assistant",
                                    content=f"Please pass relevant columns.",
                                    df=None,
                                    fig=None,
                                )
                            ]
                        )
                else:
                    error = "Sorry, we couldn't run your query on the data"
                    try:
                        query_result = run.run_statements(conn, query, sqlmagic)
                        set_messages(
                            _messages
                            + [
                                Message(
                                    role="assistant",
                                    content="",
                                    df=query_result,
                                    fig=None,
                                )
                            ]
                        )
                    except ProgrammingError as e:
                        set_messages(
                            _messages
                            + [
                                Message(
                                    role="assistant", content=error, df=None, fig=None
                                )
                            ]
                        )
                    except Exception as e:
                        set_messages(
                            _messages
                            + [
                                Message(
                                    role="assistant", content=error, df=None, fig=None
                                )
                            ]
                        )

        else:
            set_messages(
                _messages
                + [
                    Message(
                        role="assistant",
                        content="Please load some data first!",
                        df=None,
                        fig=None,
                    )
                ]
            )

    with solara.VBox():
        for message in messages:
            ChatBox(message)

    with solara.Row(justify="center"):
        with solara.HBox(align_items="center", classes=["chat-input"]):
            solara.InputText(label="Query", value=State.input, continuous_update=False)

    if State.input.value:
        ask_chatgpt()


@solara.component
def Page():
    initial_prompt = State.initial_prompt.value
    sample_data_loaded = State.sample_data_loaded.value
    upload_data = State.upload_data.value
    upload_data_error = State.upload_data_error.value
    results = State.results.value

    with solara.AppBarTitle():
        solara.Text("Data Querying and Visualisation App")

    with solara.Card(title="About", elevation=6, style="background-color: #f5f5f5;"):
        solara.Markdown(
            """
        Interact with your data using natural language.

        Examples: <br>
        - Simple query: show me the unique values of column {column name} <br>
        - Plot columns: create a histogram (or boxplot) of {column name} <br>
        - Plot transformations: crate a histogram of column {colum name} where {another column} is {some value} """
        )

    with solara.Sidebar():
        with solara.Card("Controls", margin=0, elevation=0):
            with solara.Column():
                with solara.Row():
                    solara.Button(
                        "Sample dataset",
                        color="primary",
                        text=True,
                        outlined=True,
                        on_click=State.load_sample,
                    )
                    solara.Button(
                        "Clear dataset",
                        color="primary",
                        text=True,
                        outlined=True,
                        on_click=State.reset,
                    )
                FileDrop(
                    on_file=State.load_from_file,
                    on_total_progress=lambda *args: None,
                    label="Drag a .csv file here",
                )
                if State.loading_data.value:
                    with solara.Div():
                        solara.Text("Loading csv...")
                        solara.ProgressLinear(True)
                if initial_prompt:
                    solara.InputInt(
                        "Number of preview rows",
                        value=State.results,
                        continuous_update=True,
                    )

                solara.Markdown("Hosted in [Ploomber Cloud](https://ploomber.io/)")

    if sample_data_loaded:
        solara.Info("Sample data is loaded")
        sql_output = run.run_statements(
            conn, f"select * from my_data limit {results}", sqlmagic
        )
        solara.DataFrame(sql_output, items_per_page=10)

    if upload_data:
        solara.Info("Data is successfully uploaded")
        sql_output = run.run_statements(
            conn, f"select * from my_data limit {results}", sqlmagic
        )
        solara.DataFrame(sql_output, items_per_page=10)

    if upload_data_error:
        solara.Error(f"Error uploading data: {upload_data_error}")

    if initial_prompt == "":
        solara.Info("No data loaded")

    solara.Style(css)
    with solara.VBox(classes=["main"]):
        solara.HTML(
            tag="h3", style="margin: auto;", unsafe_innerHTML="Chat with your data"
        )

        Chat()


@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)
