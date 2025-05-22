# agent_001.py
import os
import json
import requests
import urllib.parse
from abc import ABC, abstractmethod
from backend.utils.json_utils import parse_response_string
from backend.llms.groq_llm.inference import GroqInference

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
llm = GroqInference()

SYSTEM_PROMPT = """
You are an expert in searching through the web and providing information after analyzing the search results you get. 
You will be given a user query using which you should analyze and create appropriate search queries.

The tools which you have access to are:
1. browsertool: This is a tool to browse the web.
   parameters:
   - queries: [List of comma separated queries you need to search for example: ["query1", "query2", "query3"]]

2. thinkingtool: This tool is used to break down the user query and generate search queries.
   parameters:
   - query: Take the user input query and generate the queries to search for

3. tablecreatortool: This tool generates a structured markdown table of tourist information.
   parameters:
   {
     "tourism_places": {
       "Amber Fort": {
         "Timings": "...",
         ...
       }
     }
   }
   Instructions:
   - Create a table with the following columns:
        - Place
        - Description
        - Timings
        - Entry Fees
        - Best Time to Visit
        - Holidays
        - Google Map Link
        - Mentioned In (top three only)
   - use precise data for table either from internet or from document, don't make up the information.

4. finishtool: This tool should be called when you have found the information you need.
   parameters:
   - summary: The summary of the information you have found and add factual context in summary part from the data.

Instructions:
   -Always use the finishtool to finish the task.
   -Respond strictly in JSON like:
    ```JSON
        {
        "reasoning": "Explain why the selected tool and parameters are appropriate",
        "tool_name": "tool_name_here",
        "parameters": {
            ... tool-specific parameters ...
        }
        }
    ```
    """

class BrowserAgent:
    def __init__(self):
        self.stored_table = None 

    def run(self, query):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"User query: {query}"},
        ]

        while True:
            print("\n=== Generating LLM Response ===")
            response = llm.generate_response(messages=messages)
            # print(f"Raw LLM response: {response}")
            messages.append({"role": "assistant", "content": response})
            response_object = parse_response_string(response)
            # print(f"Debug:- response_object: {response_object}")

            if response_object is None:
                messages.append({"role": "user", "content": "Invalid response format, please try again."})
                continue

            tool_name = response_object.get("tool_name")
            parameters = response_object.get("parameters")

            if not tool_name or not isinstance(parameters, dict):
                messages.append({"role": "user", "content": "Invalid tool name or parameters received, please try again."})
                continue

            print(f"\n=== Running Tool: {tool_name} ===")
            # print(json.dumps(parameters, indent=2))

            try:
                continue_flag, tool_response = self._run_tool(tool_name, parameters)
            except Exception as e:
                print(f"Tool execution failed: {e}")
                messages.append({"role": "user", "content": f"Tool execution failed with error: {e}"})
                continue

            if continue_flag:
                print("\n=== Tool Output ===")
                print(tool_response)
                messages.append({
                    "role": "user",
                    "content": f"Observations: {json.dumps(tool_response, indent=2)}"
                })
                print("\n=== Generating Next Tool Call ===")
            else:
                print("\n=== Final Response ===")
                final_response = {
                    "summary": tool_response.get("summary", ""),
                    "table": self.stored_table or "No table found."
                }
                # print(json.dumps(final_response, indent=2))
                return final_response

    def _run_tool(self, tool_name, input):
        if tool_name == "browsertool":
            return True, BrowserTool().execute(input)
        elif tool_name == "thinkingtool":
            return True, ThinkingTool().execute(input)
        elif tool_name == "tablecreatortool":
            table_dicts = TableCreatorTool().execute(input).get("table", [])
            self.stored_table = self._convert_table_to_markdown(table_dicts)
            return True, {"table": self.stored_table}
        elif tool_name == "finishtool":
            summary = input.get("summary", "")
            return False, {"summary": summary}
        else:
            return False, {"summary": f"Unknown tool: {tool_name}", "table": ""}

    def _convert_table_to_markdown(self, table_rows):
        if not table_rows:
            return "No table data available."

        headers = list(table_rows[0].keys())
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        for row in table_rows:
            row_values = [str(row.get(h, "")).replace("\n", " ").strip() for h in headers]
            md += "| " + " | ".join(row_values) + " |\n"
        return md


class Tool(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, input):
        pass


class BrowserTool(Tool):
    def __init__(self):
        super().__init__("browsertool", "This is a tool to browse the web")

    def execute(self, input):
        queries = input.get("queries", [])
        if not queries:
            return "No queries to search for"

        final_snippets = []
        for query in queries:
            results = self.search(query)
            snippets = self.get_snippets_from_search_results(results)
            final_snippets.append(snippets)

        joined_snippets = "\n\n".join(final_snippets)
        summary = self.summarize_snippets(joined_snippets)
        return {
            "summary": summary,
            "places": self.extract_places_from_snippets(joined_snippets)
        }

    def search(self, query):
        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps({"q": query}))
        return response.json()

    def get_snippets_from_search_results(self, results):
        return "\n".join([
            result.get("snippet", "") for result in results.get("organic", [])
        ])

    def summarize_snippets(self, snippets):
        return llm.generate_response([
            {"role": "system", "content": "You are a summarizer."},
            {"role": "user", "content": f"Summarize these snippets:\n{snippets}"}
        ])

    def extract_places_from_snippets(self, snippets):
        import re
        matches = re.findall(r"(?:in|at|around)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", snippets)
        return list(set(matches))


class ThinkingTool(Tool):
    def __init__(self):
        super().__init__("thinkingtool", "Breaks down user query to generate search queries")

    def execute(self, input):
        query = input.get("query", "")
        return self.generate_queries(query)

    def generate_queries(self, query):
        prompt = """
        You are an expert planner. Break down the user query into 5 max optimized search queries in JSON.
        Return this format:
        {
          "reasoning": "Why you chose these queries",
          "queries": ["...", "..."]
        }
        Only JSON response.
        """
        response = llm.generate_response([
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"User query: {query}"}
        ])
        return parse_response_string(response)


class TableCreatorTool(Tool):
    def __init__(self):
        super().__init__("tablecreatortool", "Creates tourism data table")

    def execute(self, input):
        table = []
        tourism_places = input.get("tourism_places", {})
        for place, provided_data in tourism_places.items():
            map_link = self.generate_map_link(place)
            data = {
                "🏛️ Place": f"[{place}]({map_link})",
                "📝 Description": provided_data.get("Description"),
                "🕒 Timings": provided_data.get("Timings") ,
                "💰 Entry Fees": provided_data.get("Entry Fees") ,
                "🌤️ Best Time to Visit": provided_data.get("Best Time to Visit"),
                "📍 Google Map Link": f"[Google Map]({map_link})",
                "📖 Mentioned In": provided_data.get("Mentioned In"),
            }
            table.append(data)
        # print("TableCreatorTool executed successfully")
        # print(f"Table data: {table}")
        return {"table": table}

    def generate_map_link(self, place):
        return f"https://www.google.com/maps/search/?q={urllib.parse.quote(place)}"
