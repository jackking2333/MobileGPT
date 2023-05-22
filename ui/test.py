from __future__ import annotations
import openai
import json
import deepl
from duckduckgo_search import ddg
auth_key = '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'
translator = deepl.Translator(auth_key)


def google_search(query: str, num_results: int = 8) -> str:
    """Return the results of a Google search

    Args:
        query (str): The search query.
        num_results (int): The number of results to return.

    Returns:
        str: The results of the search.
    """
    # query_en = translator.translate_text(query, target_lang='EN-US')
    search_results = []
    if not query:
        return json.dumps(search_results)

    results = ddg(query, max_results=num_results)
    if not results:
        return json.dumps(search_results)

    for j in results:
        search_results.append(j)

    return json.dumps(search_results, ensure_ascii=False, indent=4)

# print(google_search('星链StarsLink'))

openai.api_key = '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'
OUTPUT_FILE = "model_list.txt"
modelList = openai.Model.list() 
with open(OUTPUT_FILE, "a") as f:
    for d in modelList.data:
        f.write(d.id)
        f.write("\n")