# AI Research Agent

A LangChain-based agent that researches a topic using DuckDuckGo and Wikipedia, then returns a structured summary with sources.

## Tools
- **search** — DuckDuckGo web search
- **wiki** — Wikipedia lookup
- **save** — saves research output to a text file
- **load** — reads previously saved research
- **current_date** — returns today's date and time

## Features
- Structured output via Pydantic (topic, summary, sources, tools used)
- Exponential backoff with jitter on agent calls for resilience against API failures

## Setup
1. Add your API key to a `.env` file, for example: `OPENAI_API_KEY=your-key`
2. `pip install -r requirements.txt`
3. `python main.py`

Initial code from https://www.youtube.com/watch?v=bTMPwUgLZf0
