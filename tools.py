from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
import datetime, arxiv

def search_arxiv(query: str, max_results: int = 5):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    results = []
    for result in search.results():
        results.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "summary": result.summary,
            "published": result.published.strftime("%Y-%m-%d"),
            "url": result.entry_id
        })

    if not results:
        return "No academic papers found for this query."

    output = []
    for r in results:
        authors = ", ".join(r["authors"])
        snippet = r["summary"][:200] + "..."
        output.append(f"{r['title']} ({r['published']})\nAuthors: {authors}\n{snippet}")

    return "\n\n".join(output)

def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    
    return f"Data successfully saved to {filename}"

def load_from_txt(filename: str = "research_output.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "No research output found."

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

date_tool = Tool(
    name="current_date",
    func=get_current_date,
    description="Returns the current date and time in YYYY-MM-DD HH:MM:SS format"
)

save_tool = Tool(
    name="save",
    func=save_to_txt,
    description="Saves structured response to text file"
)

load_tool = Tool(
    name="load",
    func=load_from_txt,
    description="Loads previously saved structured response from text file"
)

arxiv_tool = Tool(
    name="arxiv",
    func=search_arxiv,
    description="Search arXiv for academic papers"
)

search = DuckDuckGoSearchRun()
search_tool =  Tool(
  name = "search",
  func = search.run,
  description = "Search the web for information",
)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max = 100)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
