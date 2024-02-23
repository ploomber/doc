from openai import OpenAI
from pathlib import Path
import json
from IPython import display
from datetime import datetime
import tiktoken
from articles import ArxivClient
from scipy.spatial import KDTree
import numpy as np
from datetime import datetime

TOKEN_LIMIT = 3750 # allow some buffer so responses aren't cut off

def current_time():
    return datetime.now().strftime("%H:%M:%S")

def print_msg(msg):
    print(f"[{current_time()}]: {msg}")

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()
        self.store = EmbeddingsStore()
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.messages = [None, ]
        self.articles = [None for _ in range(6)]
        self.article_chunks = []
        self.article_focus_id = None
        self.load_tools()
        self.load_categories()


    def load_categories(self):
        path = Path("./json/categories.json")
        with open(path, "r") as categories_json:
            self.categories = json.load(categories_json)


    def load_tools(self):
        path = Path("./json/tools.json")
        self.tools = json.loads(path.read_text())["tools"]
    

    def get_articles(self):
        path = Path("./json/articles.json")
        articles = None
        with open(path, "r") as articles_json:
            articles = json.load(articles_json)
            for i in range(5):
                self.articles[i] = articles[i]
        return articles


    def count_tokens(self, msgs):
        token_count = 0
        for m in msgs:
            tc = len(self.encoding.encode(str(m)))
            token_count += tc
        return token_count


    def trim_messages(self, token_count):
        while token_count > TOKEN_LIMIT:
            first_msg = self.messages.pop(1)
            token_count -= len(self.encoding.encode(str(first_msg)))
            print_msg(f"Trimmed messages to: {token_count} tokens.")
        return token_count


    def fetch_articles_from_query(self, query, criterion="relevance", order="descending"):
        ac = ArxivClient()
        articles_raw = None
            
        topic = self.topic_classify_terms(query)
        if len(topic.split()) > 10:
            return False, topic
        else:
            articles_raw = ac.get_articles_by_terms(topic, criterion, order)
    
        articles = ac.results_to_array(articles_raw)
        embeddings = self.store.get_bunch(articles)

        try:
            kdtree = KDTree(np.array(embeddings))
        except:
            help_msg = "There was a problem processing that message. Can you please try again? \n\n I can help you with a wide range of topics, including but not limited to: mathematics, computer science, astrophysics, statistics, and quantitative biology!"
            return False, help_msg

        _, indexes = kdtree.query(self.store.get_one(query), k=5)
        relevant_articles = [articles_raw[i] for i in indexes]

        ac.results_to_json(relevant_articles)
        self.load_prompt()
        
        return True, None

    
    def load_prompt(self, verbose=False):
        prompt = f"""
You are a helpful assistant that can answer questions about scientific articles.
Here are the articles info in dictionary format: 

Use these to generate your answer,
and disregard articles that are not relevant to answer the question:

{str(self.get_articles())}

Additional instructions:
1. Obey the rules set in each tool's description.
2. You will have a knowledge base of 5 articles and 1 article to focus on at a time. The article to focus on, or 'current article context', may or may not be in the main set of 5.
3. Assume the user is asking about the current article in focus. This is usually the paper that the user most recently asked about.
"""
        if verbose:
            print(prompt)

        self.messages[0] = {"role": "system", "content": prompt} # tentatively works, needs testing
    

    def display_response(self, response):
        for i, choice in enumerate(response.choices, start=1):
            content = ''.join(f"\n> {line}" for line in choice.message.content.splitlines())
            
            display.display(display.Markdown(f"""
### Response {i}

{content}"""))
        return response
    
    def call_fetch_articles_tool_for_query_params(self, query):
        prompt = f"""
Given the query, call the fetch_articles function.
Do not return any text, just call the tool. Here is the query:

{query}
"""     
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            tools=[self.tools[-1]],
            seed=42,
            n=1,
        )

        msg = dict(response.choices[0].message)

        if not msg.get("tool_calls"):
            return "relevance", "descending"
        
        try:
            args = msg["tool_calls"]
            args = dict(eval(args[0].function.arguments))
        except:
            return "relevance", "descending"

        return args["sort_criterion"], args["sort_order"]


    def topic_classify_categories(self, user_query):
        system_prompt = f"""
You're a system that determines the topic of a question about academic articles in the field of Math and Science.

Given a user prompt, you should categorize it into an article category. 
Categories will be provided in a JSON dictionary format. Please return the category code,

which would be the key in the key, value pair. 

Only return a code if the category is explicitly mentioned in the query. If you aren't sure, don't return a code.

{self.categories}
"""

        messages_to_send = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Articles about kinematics"},
            {"role": "system", "content": "physics.class-ph"},
            {"role": "user", "content": "I want to know articles about react.js"},
            {"role": "system", "content": "cs.SE"},
            {"role": "user", "content": "Give me some articles on how the brain works"},
            {"role": "system", "content": "q-bio.NC"},
            {"role": "user", "content": user_query},
        ]

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_to_send,
            seed=42,
            n=1,
        )
        return response.choices[0].message.content


    def topic_classify_terms(self, user_query):
        system_prompt = f"""
You're a system that determines the topic of a question about academic articles in the field of Math and Science.

Given a user prompt, you should simplify it into a set of article search terms.
Your response should be less than 5 words. When in doubt, just return the query without filler words. Here is a list of examples:


{self.categories.values()}
"""

        messages_to_send = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Articles about kinematics"},
            {"role": "system", "content": "kinematics"},
            {"role": "user", "content": "I want to know articles about react.js and node libraries"},
            {"role": "system", "content": "react node libraries"},
            {"role": "user", "content": "Give me some articles on LLMs"},
            {"role": "system", "content": "large language models"},
            {"role": "user", "content": "Any new news on cryptography? or information security?"},
            {"role": "system", "content": "cryptography information security"},
            {"role": "user", "content": user_query},
        ]

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_to_send,
            seed=42,
            n=1,
        )

        return response.choices[0].message.content


    def get_article_by_title(self, title):
        for a in self.articles:
            if a["title"] == title:
                return a
        return None


    def get_description(self, arguments):
        try:
            article = self.get_article_by_title(arguments["title"])
            return f"Here's the description for **{arguments['title']}**: \n\n" + article["description"]
        except:
            return "There was a problem answering this question, try rephrasing."


    def get_authors(self, arguments):
        try:
            article = self.get_article_by_title(arguments["title"])
            return ", ".join(list(article["authors"]))
        except:
            return "There was a problem answering this question, try rephrasing."


    def get_links(self, arguments):
        try:
            article = self.get_article_by_title(arguments["title"])
            return article["links"]

        except:
            return "There was a problem answering this question, try rephrasing."


    def get_published_date(self, arguments):
        try:
            article = self.get_article_by_title(arguments["title"])
            date = datetime.strptime(article["published"], "%Y-%m-%d %H:%M:%S%z")
            return date.strftime("%m/%d/%Y")
        except:
            return "There was a problem answering this question, try rephrasing."


    def get_categories(self, arguments):
        try:
            article = self.get_article_by_title(arguments["title"])
            category_codes = article["categories"]
            category_names = []
            for code in category_codes:
                if code in self.categories:
                    category_names.append(self.categories[code])
                else:
                    print(f"Code: {code} not found in categories.")
            return " ".join(category_names)
        except:
            return "There was a problem answering this question, try rephrasing."


    def fetch_articles(self, arguments):
        try: # bring this back after testing
            query = arguments["query"]

            sort_criterion = arguments["sort_criterion"]
            sort_order = arguments["sort_order"]
            success, content = self.fetch_articles_from_query(query, sort_criterion, sort_order)
        
            if not success:
                return content
        except:
            return f"There was a problem answering your question: {content}"
        
        return "FETCHED-NEED-SUMMARIZE"
    
    
    def answer_question(self, arguments):
        try:
            id, query = arguments["id"], arguments["query"]
            chunk = self._get_article_chunk(id, query)
            prompt = f"""
    Use this chunk of the article to answer the user's question.
    {chunk}

    Here is the user's question:
    {query}
    """
            self.messages.append({
                "role": "system",
                "content": prompt,
            })

            print_msg("Getting response from Open AI.")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                seed=42,
                n=1,
            )

            answer = response.choices[0].message.content
            print_msg(answer)
            self.messages.append({"role": "assistant", "content": answer})
            return answer
        except:
            return f"There was a problem answering your question, try rephrasing."
    
    def download_article_from_url(self, arguments):
        url = arguments["url"]
        id = url.split("/")[-1]
        self._load_article_chunks(id)
        message = f"Summarize the paper that was just provided in a few sentences based on this description: {self.articles[-1]['description']}"
        content = ""
        for response in self.article_chat(message):
            content = response
        print_msg(f"Response from Open AI: {content}")
        content = f"Got your article. Here's a summary: \n\n {content} \n\n Now I can answer your questions, so ask away!"
        self.messages.append({
            "role": "assistant",
            "content": content
        })
        return content


    def call_tool(self, call):
        print_msg(f"Function call: {call}")
        try:
            func_name, args = call["name"], dict(eval(call["arguments"]))
            # print_msg(f"Called function: {func_name}, Args: {args}")
        except:
            return "There was a problem answering this question, try rephrasing."
        
        content = getattr(self, func_name)(args)

        self.messages.append( # adding assistant response to messages
            {
                "role": "assistant",
                "function_call": {
                    "name": func_name,
                    "arguments": str(args),
                },
                "content": "" # str(content)
            }
        )

        self.messages.append( # adding function response to messages
            {
                "role": "function",
                "name": func_name,
                "content": str(content),
            }
        )
        return content


    def article_chat(self, user_query):
        self.messages.append({"role": "user", "content": user_query})

        count = self.count_tokens(self.messages)
        count = self.trim_messages(count)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto",
            seed=42,
            stream=True
        )

        function_call = {
            "name": None,
            "arguments": "",
        }
        answer = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            finish_reason = chunk.choices[0].finish_reason
            if dict(delta).get("tool_calls"):
                function = dict(delta.tool_calls[0].function)
                if function.get("name"):
                    function_call["name"] = function["name"]
                if function.get("arguments"):
                    function_call["arguments"] += function["arguments"]

            if finish_reason == "tool_calls":
                answer = self.call_tool(function_call)
            else:
                content = delta.content
                if content:
                    answer += content
            yield answer
        
        self.messages.append({"role": "assistant", "content": answer})
    

    def _load_article_chunks(self, id=None):
        if self.article_focus_id == id:
            print_msg("Already downloaded this article.")
            return

        print(f"Downloading articles, id: {id}")
        info, chunks = ArxivClient().download_article(id)
        self.article_focus_id = id
        self.article_chunks = chunks
        self.articles[-1] = info
        self.messages.append({
            "role": "system",
            "content": f"The current paper context is this title: {info['title']}. Unless the user mentions a different article, assume the user is asking about this article. You may call any of the tools."
        })


    def _get_article_chunk(self, id=None, query=None):
        self._load_article_chunks(id)
        chunk_embeddings = self.store.get_bunch(self.article_chunks)

        query_embedding = self.store.get_one(query)
        kdtree = KDTree(np.array(chunk_embeddings))

        _, index = kdtree.query(query_embedding, k=1)
        relevant_chunk = self.article_chunks[index]

        return relevant_chunk



class EmbeddingsStore:
    def __init__(self):
        self._path = Path("./json/embeddings.json")

        if not self._path.exists() or not self._path.read_text():
            self._data = {}
        else:
            self._data = json.loads(self._path.read_text())

    def get_one(self, text):
        if text in self._data:
            return self._data[text]
        
        response = OpenAIClient().client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )

        embedding = response.data[0].embedding

        self._data[text] = embedding
        self._path.write_text(json.dumps(self._data))

        return embedding

    
    def get_bunch(self, content):
        print_msg("Getting many embeddings.")
        try:
            response = OpenAIClient().client.embeddings.create(
                input=content,
                model="text-embedding-3-small"
            )
        except:
            return self.get_many(content)
        print_msg("Received response.")
        embeddings = [item.embedding for item in response.data]
        for i, text in enumerate(content):
            self._data[text] = embeddings[i]
    
        self._path.write_text(json.dumps(self._data))
        print_msg(f"Returned {len(embeddings)} embeddings.")
        return embeddings


    def get_many(self, content):
        return [self.get_one(text) for text in content]

    def __len__(self):
        return len(self._data)