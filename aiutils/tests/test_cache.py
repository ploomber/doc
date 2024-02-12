import json
import sqlite3

from pydantic import BaseModel
import pytest

import aiutils.cache as cache


def dummy_api_function():
    pass


@pytest.fixture
def sample_messages():
    return [
        {"role": "system", "content": "You're a helpful assistant"},
        {"role": "user", "content": "Say hello to me"},
    ]


@pytest.fixture
def sample_response():
    return {
        "id": "chatcmpl-8oGlRhCPtGidbnfEseI4Q5sncqZf0",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "logprobs": None,
                "message": {
                    "content": "Hello! How can I assist you today?",
                    "role": "assistant",
                    "function_call": None,
                    "tool_calls": None,
                },
            }
        ],
        "created": 1706991533,
        "model": "gpt-4-0125-preview",
        "object": "chat.completion",
        "system_fingerprint": "fp_f084bcfc79",
        "usage": {"completion_tokens": 9, "prompt_tokens": 20, "total_tokens": 29},
    }


@pytest.fixture
def sample_cache(sample_messages, sample_response):
    my_cache = cache.APICache(
        api_function=dummy_api_function, path_to_db="api_calls.db"
    )

    my_cache.insert(
        kwargs=dict(
            model="gpt-4-0125-preview",
            messages=sample_messages,
        ),
        response=sample_response,
    )

    return my_cache


def test_create_db():
    cache.APICache(api_function=dummy_api_function, path_to_db="api_calls.db")
    conn = sqlite3.connect("api_calls.db")

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    assert tables == [("api_calls",)]


def test_insert(sample_messages, sample_response):
    c = cache.APICache(api_function=dummy_api_function, path_to_db="api_calls.db")

    kwargs = dict(
        model="gpt-4-0125-preview",
        messages=sample_messages,
    )

    c.insert(
        kwargs=kwargs,
        response=sample_response,
    )

    conn = sqlite3.connect("api_calls.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_calls")
    rows = cursor.fetchall()

    assert rows == [
        (
            "test_cache.dummy_api_function",
            json.dumps(kwargs),
            json.dumps(sample_response),
        )
    ]


def test_lookup_exists(sample_cache, sample_messages, sample_response):
    response = sample_cache.lookup(
        kwargs=dict(model="gpt-4-0125-preview", messages=sample_messages)
    )

    assert response == sample_response


@pytest.mark.parametrize(
    "model, messages",
    [
        (
            "gpt-4-0125-preview",
            [
                {"role": "user", "content": "Say goodbye to me"},
            ],
        ),
        (
            "some-other-model",
            [
                {"role": "system", "content": "You're a helpful assistant"},
                {"role": "user", "content": "Say hello to me"},
            ],
        ),
    ],
)
def test_lookup_does_not_exist(sample_cache, model, messages):
    response = sample_cache.lookup(
        kwargs=dict(
            model=model,
            messages=messages,
        )
    )

    assert response is None


def test_call_uses_cache(sample_cache, sample_messages, sample_response):
    def api_function(*args, **kwargs):
        raise RuntimeError("Should not call the API")

    response = sample_cache(model="gpt-4-0125-preview", messages=sample_messages)

    assert response.to_dict() == sample_response


class SampleResponseModel(BaseModel):
    key: str


@pytest.mark.parametrize(
    "extra_kwargs",
    [
        {},
        {
            "n": 1,
        },
    ],
)
def test_call_calls_api(sample_messages, sample_response, extra_kwargs):
    def api_function(*args, **kwargs):
        return SampleResponseModel(key="this is a message from the API!")

    my_cache = cache.APICache(api_function=api_function, path_to_db="api_calls.db")

    my_cache.insert(
        kwargs=dict(
            model="gpt-4-0125-preview",
            messages=sample_messages,
        ),
        response=sample_response,
    )

    response = my_cache(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "You're a new assistant"},
            {"role": "user", "content": "Say goodbye to me"},
        ],
        **extra_kwargs,
    )

    assert response.to_dict() == {"key": "this is a message from the API!"}


def test_doesnt_use_cache_if_different_api_function():
    def first_api_function(a, b):
        return SampleResponseModel(key="first api")

    def second_api_function(a, b):
        return SampleResponseModel(key="second api")

    first_cache = cache.APICache(
        api_function=first_api_function, path_to_db="api_calls.db"
    )
    second_cache = cache.APICache(
        api_function=second_api_function, path_to_db="api_calls.db"
    )

    assert first_cache(a=1, b=2).to_dict() == {"key": "first api"}
    assert second_cache(a=1, b=2).to_dict() == {"key": "second api"}
