#chat.py
from typing import List, Dict
import json
from concurrent.futures import ThreadPoolExecutor

from backend.memory.chroma_memory.retrieve_data import query_chroma
from backend.llms.groq_llm.inference import GroqInference
from backend.memory.mem0_memory.try_mem0 import extract_relevant_memories, add_memory_in_mem0
from backend.utils.json_utils import pre_process_the_json_response, load_object_from_string
from backend.Agents.Agent_frameworks.agent_001 import BrowserAgent
from backend.utils.semantic import is_similar_query

groq_llm = GroqInference()


def print_section(title: str = "", content: str = "", separator: str = "=") -> None:
    print(f"\n{separator * 80}")
    if title:
        print(f"\n{title}")
        print(f"{'-' * 80}")
    if content:
        print(f"\n{content}\n")
    if separator == "=":
        print(f"{separator * 80}")


def chat_with_tourism_assistant(user_id: str, user_query: str, messages: List[Dict[str, str]]):
    system_prompt = """
        -You are a tourism expert and historian. Use provided structured knowledge (documents, tables, maps) and user memories to answer the query clearly.
        -Return only a **clear, concise summary** in markdown format — no tables, no follow-up questions.
        -Do not repeat the user query. Do not use headings like "Summary of the answer". Just write the answer in plain markdown text.
        -If there are specific tourist spots, highlight them naturally in the text with emojis (e.g., 🏛️, 🏞️, 📍) when relevant.

        Instructions:   
        - Use the documents and agent-generated data (table/maps) to answer.
        - Use memories only to enrich summary (never to build the table).
        - If you're unsure, say "I don't know" instead of guessing.
        - Never change table data given to you. Keep it short and crisp.
        - Always return the final answer in markdown.
    """.strip()

    print_section()

    use_memory = False
    memories = []

    if not user_query.strip() or len(user_query.strip().split()) < 3:
        use_memory = True
        memories = extract_relevant_memories(user_query, user_id) or []
    else:
        candidate_memories = extract_relevant_memories(user_query, user_id) or []
        for mem in candidate_memories:
            if is_similar_query(user_query, mem):
                use_memory = True
                memories = candidate_memories
                break

    print_section("🧠 Memories", "\n".join(memories) if memories else "No relevant memories used.")

    rephrased_query = rephrase_user_query(user_query, memories)
    print_section("🔁 Rephrased Query", rephrased_query)

    documents = query_chroma(rephrased_query, collection_name="travel_data", n_results=3)
    print_section("📚 Knowledge Source", documents)

    agent = BrowserAgent()
    try:
        agent_output = agent.run(rephrased_query)
        print_section("🛠️ Agent Output", json.dumps(agent_output, indent=2) if isinstance(agent_output, dict) else str(agent_output))
    except Exception as e:
        print(f"⚠️ Exception during agent.run(): {e}")
        import traceback
        traceback.print_exc()
        agent_output = {"summary": "Agent execution failed.", "table": ""}

    messages.append({"role": "system", "content": system_prompt})
    messages.append({
        "role": "user",
        "content": f"""
        USER QUERY: {user_query}

        RELEVANT MEMORIES:
        {memories}

        RELEVANT DOCUMENTS:
        {documents}

        AGENT OUTPUT:
        {json.dumps(agent_output, indent=2) if isinstance(agent_output, dict) else str(agent_output)}
        """
    })

    try:
        summary = groq_llm.generate_response(messages).strip()
    except Exception as e:
        summary = "⚠️ Sorry, I couldn't generate a summary right now."

    assistant_answer = {
        "summary": summary,
        "table": agent_output.get("table", "") if isinstance(agent_output, dict) else ""
    }

    messages.append({"role": "assistant", "content": f"{summary}\n\n{assistant_answer['table']}"})

    with ThreadPoolExecutor() as executor:
        executor.submit(add_memory_in_mem0, user_query, user_id)

    return assistant_answer, messages


def rephrase_user_query(query: str, memories: List[str]) -> str:
    llm = GroqInference()
    memory_text = "\n".join(memories)

    system_prompt = """
    You are an expert in rephrasing user queries. You are given a user query and some relevant memories.
    Rephrase the user query to make it clearer, more specific, and suitable for travel-related document and web searches.
    Keep it natural and avoid making up details.

    Respond ONLY in this JSON format:
    ```json
    {
    "rephrased_query": "Your rephrased query"
    }
    ```
    """.strip()

    user_prompt = f"""
        User Query: {query}

        RELEVANT MEMORIES:
        {memory_text}

        Note: Only respond with the JSON containing the rephrased query.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = llm.generate_response(messages)
        pre_processed = pre_process_the_json_response(response)
        obj = load_object_from_string(pre_processed)
        return obj["rephrased_query"]
    except Exception as e:
        print("⚠️ Error in rephrasing, using original query.")
        return query
