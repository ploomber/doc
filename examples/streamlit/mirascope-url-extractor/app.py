"""A Streamlit App for Extracting structured information using Mirascope."""
from typing import Dict, List, Literal, Optional, Type, Union
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from mirascope.anthropic import AnthropicExtractor, AnthropicCallParams
from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING
from pydantic import BaseModel, Field, computed_field, create_model
import streamlit as st

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the application"""

    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# =============================================== #
# ~~~~~~~~~~~ MIRASCOPE CODE SECTION ~~~~~~~~~~~~ #
# =============================================== #


class FieldDefinition(BaseModel):
    """Define the fields to extract from the webpage."""

    name: str = Field(..., description="The desired name for this field.")
    type: Literal["str", "int", "float", "bool"]


class SchemaGenerator(AnthropicExtractor[list[FieldDefinition]]):
    """Generate a schema based on a user query."""

    api_key = settings.anthropic_api_key

    extract_schema: Type[list] = list[FieldDefinition]

    prompt_template = """
    Call your tool with field definitions based on this query:
    {query}
    """

    query: str


class WebpageURLExtractor(AnthropicExtractor[BaseModel]):
    """Extract JSON from a webpage using natural language"""

    api_key = settings.anthropic_api_key

    extract_schema: Type[BaseModel] = BaseModel

    prompt_template = """
    YOU MUST USE THE PROVIDED TOOL FUNCTION.
    Call the function with parameters extracted from the following content:
    {webpage_content}
    """

    url: str
    query: str

    call_params = AnthropicCallParams(max_tokens=4000)

    @computed_field
    @property
    def webpage_content(self) -> str:
        """Returns the text content of the webpage found at `url`."""
        request = Request(url=self.url, headers={"User-Agent": "Mozilla/6.0"})
        html_doc = urlopen(request).read().decode("utf-8")
        soup = BeautifulSoup(html_doc, "html.parser")
        text = soup.get_text()
        for link in soup.find_all("a"):
            text += f"\n{link.get('href')}"
        return text

    def generate_schema(self) -> None:
        """Sets `extract_schema` to a schema generated based on `query`."""
        field_definitions = SchemaGenerator(query=self.query).extract()
        model = create_model(
            "ExtractedFields",
            __doc__=DEFAULT_TOOL_DOCSTRING,
            **{
                field.name.replace(" ", "_"): (field.type, ...)
                for field in field_definitions
            },
        )
        self.extract_schema = list[model]


# =============================================== #
# ~~~~~~~~~~ STREAMLIT UI CODE SECTION ~~~~~~~~~~ #
# =============================================== #

st.title("Mirascope URL Extractor")
st.subheader("Extract a list of flat structures from a URL with natural language")

url = st.text_input(
    "URL",
    value="https://www.fridakahlo.org/frida-kahlo-paintings.jsp",
    label_visibility="visible",
)

query = st.text_input(
    "Query",
    value="painting titles and associated full links",
    label_visibility="visible",
)


extracted_items: List[Dict[str, Union[str, int, float, bool]]] = []
if "extracted_items" not in st.session_state:
    st.session_state.extracted_items = []


begin = st.container()


def extract():
    """Extracts a list of objects defined by the `query` from the `url`."""
    begin.empty()
    extractor = WebpageURLExtractor(url=url, query=query)
    with begin.status("Extracting information...") as status:
        try:
            st.write("Generating schema based on user query...")
            extractor.generate_schema()
            st.write(f"Extracting data from {url}...")
            st.session_state.extracted_items = extractor.extract(retries=3)
        except Exception as e:
            status.error(f"Error: {e}")
            status.update(state="error")
            return
    with begin.container():
        for item in st.session_state.extracted_items:
            st.write("-" * 20)
            for key, value in item.model_dump().items():
                st.write(f"{key}: {value}")


begin.button("Extract", on_click=extract)
