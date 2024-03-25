import solara as sl
from dataclasses import dataclass
import time
import threading
import time
from llm import get_repo_id
import schedule
from services import status_color, repos, status, ask, scrape, reset


chatbox_css = """
a: {
    text-decoration: none;
    color: black;
}

.message {
    max-width: 450px;
    width: 100%;
}

.system-message, .system-message > * {
    background-color: #ffffff !important;
}

.user-message, .user-message > * {
    background-color: #f0f0f0 !important;
}

.assistant-message, .assistant-message > * {
    background-color: #9ab2e9 !important;
}
"""


@dataclass
class Message:
    role: str
    content: str

@dataclass
class Repository:
    id: str
    status: str


all_repos = repos()
print(f"Initializing: {all_repos}")


@sl.component
def Chat():
    sl.Style("""
        .chat-input {
            max-width: 600px;
        }
        .avatar {
            display: block;
            margin: auto;
            width: 50%;
        }   
        .chat-area: {
            margin-bottom: 50px;
        }
        .sidebar-title: {
            padding-top: 50px;
            padding-bottom: 50px;
        }
    """)

    messages, set_messages = sl.use_state([
        Message(
            role="assistant",
            content="""Hi! I can help you chat with a GitHub repository. Start by entering an owner, repo name, and branch."""
        ),
    ])
    

    owner, set_owner = sl.use_state("ploomber")
    repo, set_repo = sl.use_state("jupysql")
    branch, set_branch = sl.use_state("master")
    error_msg, set_error_msg = sl.use_state("")
    chat_error, set_chat_error = sl.use_state(False)
    # scheduled, set_scheduled = sl.use_state(False)
    # loaded_repos, set_loaded_repos = sl.use_state_or_update([])
    loaded_repos = sl.use_reactive([Repository(rp['id'], rp['status']) for rp in all_repos])
    num_finished, set_num_finished = sl.use_state(len([rp for rp in loaded_repos.value if rp.status == "finished"]))
    disabled, set_disabled = sl.use_state(num_finished < 1)

    def update_statuses():
        print("Updating statuses...")
        # _loaded_repos = list(loaded_repos.value)
        # for i, lr in enumerate(loaded_repos.value):
        #     if lr.status != "pending":
        #         continue
        #     new_status = status(lr.id)
        #     _loaded_repos[i].status = new_status
        #     print(f"Updated {lr.id}: {new_status}")
        # _loaded_repos.append(Repository("wee", "woo"))
        
        # set_loaded_repos([rp for rp in _loaded_repos])
        # loaded_repos.set([Repository("", "") for _ in _loaded_repos])
        # loaded_repos.set(_loaded_repos)

        current_repos = repos()
        loaded_repos.set([Repository(rp.id, "") for rp in loaded_repos.value])
        loaded_repos.set([Repository(rp['id'], rp['status']) for rp in current_repos])
        set_num_finished(len([rp for rp in loaded_repos.value if rp.status == "finished"]))
        set_disabled(num_finished < 1)
        print(loaded_repos)

    
    # def schedule_updates():
    #     if scheduled:
    #         return
        
    #     set_scheduled(True)
    #     print(f"Scheduling, {scheduled}")
    #     schedule.every(10).seconds.do(update_statuses)
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(1)

    # sl.use_thread(schedule_updates, dependencies=[scheduled])

    # def render():
    #     """Infinite loop regularly mutating counter state"""
    #     while True:
    #         time.sleep(10)
    #         print("Looping...")
    #         for lr in loaded_repos:
    #             lr.status = "finished"
    #             # print(lr.id, lr.status)
    #         print(loaded_repos.value)

    # result: sl.Result[bool] = sl.use_thread(render)
    # if result.error:
    #     raise result.error

    def ask_chatgpt(input):
        set_disabled(True)
        _messages = messages + [Message(role="user", content=input)]
        set_messages(_messages)

        prompt = f"""
You are an assistant designed to decide which repository the user is asking a question about.

Here is the question: {input}

Here are the available repository IDs: {[rp.id for rp in loaded_repos.value]}

Here are the previous messages: {messages}

Only respond with the repository ID and nothing else. If there is only one repository provided,
return that ID. If it is unclear which repository the user is asking about, respond with the most recent one.
"""

        repo_id = get_repo_id(prompt)
        print(repo_id)
        # content = index()
        content, err = ask(repo_id, input)
        set_chat_error(err)
        set_messages(_messages + [Message(role="assistant", content=content)])

        set_disabled(False)

    # def check_status():
    #     try:
    #         id = f"{owner}-{repo}-{branch}"
    #         stat = status(id)
    #         print(f"{id} status: {stat}")
    #     except:
    #         print(f"{id} status: Not found")
    
    def load_repo():
        current_repos = repos()
        loaded_repos.set([Repository("", "") for _ in loaded_repos.value])
        loaded_repos.set([Repository(rp['id'], rp['status']) for rp in current_repos])

        # this_id = f"{owner}-{repo}-{branch}"
        # for rp in loaded_repos.value:
        #     if this_id == rp.id:
        #         return


        set_error_msg("")
        id = None
        try:
            id = scrape(owner, repo, branch)
        except ValueError as e:
            set_error_msg(e)
            print(error_msg)

        time.sleep(2)

        try:
            stat = status(id)
            print(f"{id} status: {stat}")
            if stat == "failed":
                set_error_msg("Repo not found. Ensure branch is correct.")
            else:
                # set_loaded_repos(loaded_repos + [Repository(id, "pending")])
                loaded_repos.value = loaded_repos.value + [Repository(id, "pending")]
                # print(f"LR: {loaded_repos.value}")
                clear()
        except Exception as e:
            print(e)
            pass
        
    

    def clear():
        set_error_msg("")
        set_owner("")
        set_repo("")
        set_branch("")

    def handle_reset():
        reset()
        update_statuses()


    with sl.Column():
        sl.Title("Chat with Github")
        with sl.Sidebar():
            sl.HTML(tag="h1", unsafe_innerHTML="Load a Repository", style={"padding-top": "10px", "padding-bottom": "10px", "padding-left": "10px"})
            
            with sl.Card():
                sl.InputText("Owner", value=owner, on_value=set_owner)
                sl.InputText("Repo", value=repo, on_value=set_repo)
                sl.InputText("Branch", value=branch, on_value=set_branch)

                if error_msg:
                    sl.Error(label=f"{error_msg}", icon=True)

                sl.Button("Load", on_click=load_repo, color="primary", style={"width": "100%", "height": "7vh", "margin-bottom": "1vh"})
                sl.Button("Clear", on_click=clear, style={"width": "100%", "margin-bottom": "1vh"})
                sl.Button("Reset DB", on_click=handle_reset, style={"width": "100%"})

            with sl.HBox(align_items="center"):
                sl.HTML(tag="h1", unsafe_innerHTML="Repositories", style={"padding-top": "10px", "padding-bottom": "10px", "padding-left": "10px"})
            
                sl.Button("Update", on_click=update_statuses, style={"margin-left": "10px", "padding-right": "20px", "right": "20px", "position": "absolute"})
            for this_repo in loaded_repos.value:
                with sl.Card():
                    with sl.Columns([7.5, 2.5]):
                        sl.Markdown(this_repo.id)
                        with sl.HBox():
                            sl.Markdown(f"__{this_repo.status}__", style={"color": status_color(this_repo.status)})
            

        with sl.VBox(classes=["chat-area"]):
            with sl.lab.ChatBox(style={"height": "70vh", "padding-bottom": "20px"}):
                for message in messages:
                    with sl.lab.ChatMessage(
                        user=message.role=="user",
                        avatar=sl.Image(f"client/static/{message.role}-logo.png", classes=["avatar"]),
                        avatar_background_color="#ffffff",
                        name=message.role.capitalize(),
                        color="#7baded" if message.role == "user" else "rgba(0,0,0, 0.06)",
                        notch=True,
                    ):
                        sl.Markdown(message.content)

            if num_finished < 1:
                sl.Warning("Load a repository to start chatting.")
            if chat_error:
                sl.Error("Error answering your question. Please refresh.")
            
            sl.lab.ChatInput(send_callback=ask_chatgpt, disabled=disabled)




# def background_job():
#     print('Hello from the background thread')
#     # _loaded_repos = list(loaded_repos.value)
#     print(loaded_repos.value)
#     for lr in loaded_repos.value:
#         print(lr.status)
#         if lr.status == "pending":
#             # new_status = status(lr.id)
#             lr.status = "finished"
            # _loaded_repos[i].status = "finished"
    # loaded_repos.value = _loaded_repos






# def run_continuously(interval=1):
#     """Continuously run, while executing pending jobs at each
#     elapsed time interval.
#     @return cease_continuous_run: threading. Event which can
#     be set to cease continuous run. Please note that it is
#     *intended behavior that run_continuously() does not run
#     missed jobs*. For example, if you've registered a job that
#     should run every minute and you set a continuous run
#     interval of one hour then your job won't be run 60 times
#     at each interval but only once.
#     """
#     cease_continuous_run = threading.Event()

#     class ScheduleThread(threading.Thread):
#         @classmethod
#         def run(cls):
#             while not cease_continuous_run.is_set():
#                 schedule.run_pending()
#                 time.sleep(interval)

#     continuous_thread = ScheduleThread()
#     continuous_thread.start()
#     return cease_continuous_run



# # Start the background thread
# stop_run_continuously = run_continuously()




# # Do some other things...
# time.sleep(10)

# # Stop the background thread
# stop_run_continuously.set()