from openai import OpenAI
from .config import get_config


def _get_openai_text_response(client, model, prompt, tools):
    if hasattr(client, "responses"):
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        }
                    ],
                }
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=tools,
            temperature=1,
            max_output_tokens=4096,
            top_p=1,
            store=True,
        )
        return response.output[1].content[0].text

    if not tools:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
            temperature=1,
            max_tokens=4096,
            top_p=1,
        )
        return response.choices[0].message.content

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
            tools=tools,
            tool_choice="auto",
            temperature=1,
            max_tokens=4096,
            top_p=1,
        )
        return response.choices[0].message.content
    except TypeError as exc:
        raise RuntimeError(
            "OpenAI chat.completions does not support tools; "
            "unable to perform web search fallback."
        ) from exc


def get_stock_news_openai(query, start_date, end_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])
    prompt = (
        f"Can you search Social Media for {query} from {start_date} to {end_date}? "
        "Make sure you only get the data posted during that period."
    )
    tools = [
        {
            "type": "web_search_preview",
            "user_location": {"type": "approximate"},
            "search_context_size": "low",
        }
    ]
    return _get_openai_text_response(
        client, config["quick_think_llm"], prompt, tools
    )


def get_global_news_openai(curr_date, look_back_days=7, limit=5):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])
    prompt = (
        "Can you search global or macroeconomics news from "
        f"{look_back_days} days before {curr_date} to {curr_date} that would be "
        "informative for trading purposes? Make sure you only get the data posted "
        f"during that period. Limit the results to {limit} articles."
    )
    tools = [
        {
            "type": "web_search_preview",
            "user_location": {"type": "approximate"},
            "search_context_size": "low",
        }
    ]
    return _get_openai_text_response(
        client, config["quick_think_llm"], prompt, tools
    )


def get_fundamentals_openai(ticker, curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])
    prompt = (
        f"Can you search Fundamental for discussions on {ticker} during of the "
        f"month before {curr_date} to the month of {curr_date}. Make sure you only "
        "get the data posted during that period. List as a table, with PE/PS/Cash "
        "flow/ etc"
    )
    tools = [
        {
            "type": "web_search_preview",
            "user_location": {"type": "approximate"},
            "search_context_size": "low",
        }
    ]
    return _get_openai_text_response(
        client, config["quick_think_llm"], prompt, tools
    )
