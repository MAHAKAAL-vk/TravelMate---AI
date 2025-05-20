from backend.memory.chroma_memory.add_data import add_pdf_to_chroma
# from backend.memory.mem0_memory.try_mem0 import add_memory_in_mem0, extract_relevant_memories
# from backend.Agents.Agent_frameworks.agent_001 import BrowserTool
# from backend.Agents.Agent_frameworks.agent_001 import BrowserAgent

# import uvicorn
# from backend.App.api import app

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    

# from backend.Conversations.chat import chat_with_travel_assistant

# if __name__ == "__main__":
    
#     user_id = "alice"
#     user_query = "What's a good beach destination in Europe?"
#     messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": user_query}
#     ]

#     assistant = chat_with_travel_assistant(user_id, user_query, messages)
#     print("Assistant response:\n", assistant)

    
    base_path = r"/media/mahakaal/VK_s/TravelMate - AI/Dataset"
    pdf_files = [
        # "/Andhra_Pradesh.pdf","/Arunachal_Pradesh.pdf","/Assam.pdf","/Bihar.pdf","/Chhattisgarh.pdf","/Goa.pdf","/Gujarat.pdf","/Haryana.pdf","/Himachal_Pradesh.pdf","/India.pdf",
        # "/Jharkhand.pdf","/Karnataka.pdf","/Madhya_Pradesh.pdf","/Maharashtra.pdf",
        # "/Manipur.pdf","/Meghalaya.pdf","/Mizoram.pdf","/Nagaland.pdf","/Odisha.pdf",
        "/Punjab.pdf",
        "/Rajasthan.pdf","/Sikkim.pdf","/Tamil_Nadu.pdf","/Telangana.pdf","/Tripura.pdf","/UT_Andaman_and_Nicobar_Islands.pdf","/UT_Chandigarh.pdf","/UT_Dadra_and_Nagar_Haveli_and_Daman_and_Diu.pdf",
        "/UT_Delhi.pdf","/UT_Jammu_and_Kashmir.pdf","/UT_Ladakh.pdf","/UT_Lakshadweep.pdf",
        "/UT_Puducherry.pdf","/Uttar_Pradesh.pdf","/Uttarakhand.pdf","/West_Bengal.pdf",
    ]
    pdf_paths = [base_path + pdf_file for pdf_file in pdf_files]
    for pdf_path in pdf_paths:
        add_pdf_to_chroma(pdf_path)

    # tool = BrowserTool()
    # results = tool.search("Give me some information about places to visit in Jaipur")
    # snippets = tool.get_snippets_from_search_results(results)
    # summary = tool.summarize_snippets(snippets)
    # print(summary)

    # agent = BrowserAgent()
    # agent.run("Make an plan for a 10 days trip to Bangalore")