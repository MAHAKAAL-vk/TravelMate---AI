#try_mem0.py
from backend.llms.groq_llm.inference import GroqInference
from backend.utils.json_utils import parse_response_string
from mem0 import Memory

config = {
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.1,
            "max_tokens": 1000,
        },
    },
    "embedder": {
        "provider": "huggingface",
        "config": {"model": "multi-qa-MiniLM-L6-cos-v1", "embedding_dims": 384},
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "mem0_collection",
            "path": "mem0_db",
        },
    },
}

mem0 = Memory.from_config(config)


def add_memory_in_mem0(query, user_id):
    """Add relevant memories extracted from query to mem0 memory."""
    relevant_memories = _extract_relevant_memories(query)

    print("\n=== Extracted Memories ===")
    if isinstance(relevant_memories, list):
        print("\nMemories:")
        for i, memory in enumerate(relevant_memories, 1):
            print(f"  {i}. {memory}")
    else:
        print("\nMemories:")
        print(relevant_memories)
    print("\n" + "=" * 24 + "\n")

    for memory in relevant_memories:
        print(f"Adding memory: {memory}")
        mem0.add(memory, user_id=user_id)


def extract_relevant_memories(query, user_id) -> list[str]:
    results = mem0.search(query, user_id=user_id)
    raw_results = results.get("results", [])

    memories = [m.get("memory", "") for m in raw_results if "memory" in m]
    if not memories:
        print("⚠️ No memories extracted from mem0.search() results.")
    return memories


def _extract_relevant_memories(query) -> list[str]:
    """Extract the relevant memories from the query using LLM."""
    llm = GroqInference()

    system_prompt = """
    You are an expert information extractor. You are given a user query and you need to extract the relevant memories from it.
    For example, if the user query is "I am working on improving my tennis skills. Suggest some online courses.", the relevant memories are "improving tennis skills" and "online courses".

    Instructions:
    1. Extract the relevant memories from the user query.
    2. Don't assume any information. Just extract the memories from the user query.
    3. Give the response in the provided JSON FORMAT
    4. Also be careful about the spelling of the memories.
    5. Keep the memories in the same order as they appear in the user query.
    6. Beautify the JSON response.

    The JSON FORMAT is:
    ```json
    {
        "reasoning": "Reasoning for the memories extracted",
        "memories": ["memory1", "memory2", "memory3"]
    }
    ```
    """

    user_prompt = f"""
    User Query: {query}

    Note: Only give the JSON as the response.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = llm.generate_response(messages)
    parsed_response = parse_response_string(response)

    if not parsed_response:
        raise Exception("Failed to extract the relevant memories from the user query.")

    return parsed_response.get("memories", [])


# if __name__ == "__main__":
#     add_memory_in_mem0(
#         "I am working on improving my tennis skills. Suggest some online courses.",
#         "alice",
#     )
#     extracted = extract_relevant_memories("what was the game I searched for last time?", "alice")
#     print("\n[FINAL EXTRACTED MEMORIES]:", extracted)
