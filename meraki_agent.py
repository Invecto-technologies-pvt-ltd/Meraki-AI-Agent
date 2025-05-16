# meraki_agent.py

import meraki_tools
# from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
import streamlit as st
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from preprocessor import match_tool

# Initialize local Mistral model via Ollama for dynamic response generation
llm = OllamaLLM(model="mistral", temperature=0.1)

# Initialize sentence transformer model for generating embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Initialize FAISS index
faiss_index = faiss.IndexFlatL2(model.get_sentence_embedding_dimension())

# Sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


def ask_llm(prompt):
    return llm.invoke(prompt)


def format_result(result):
    """
    Format the result to present it in a clean, readable way with bullet points or
    relevant format, ensuring each point appears on a new line.
    """
    # If the result is a list of dictionaries, create a bullet point list
    if isinstance(result, list) and isinstance(result[0], dict):
        headers = result[0].keys()
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        for row in result:
            table += "| " + " | ".join(str(row.get(h, '')) for h in headers) + " |\n"
        return table
    # Fallback to plain text
    return str(result)


def add_query_embeddings_to_faiss(queries):
    """
    Generate embeddings for the queries and add to the FAISS index.
    """
    embeddings = np.array([model.encode(query) for query in queries])
    faiss_index.add(embeddings)


def get_best_match(query):
    """
    Find the best matching query from the FAISS index.
    """
    query_embedding = np.array([model.encode(query)])
    _, indices = faiss_index.search(query_embedding, k=1)
    return queries[indices[0][0]]

def analyze_sentiment(query):
    """
    Analyze the sentiment of the user's query and adapt response accordingly.
    """
    sentiment = analyzer.polarity_scores(query)
    if sentiment['compound'] < -0.2:
        return "It seems you're frustrated. Let me assist you as quickly as possible."
    return None


def run_meraki_agent(user_query: str):
    # Check sentiment first
    sentiment_response = analyze_sentiment(user_query)
    if sentiment_response:
        return sentiment_response

    tool = match_tool(user_query)

    if st.session_state.selected_network_id:
        network_id = st.session_state.selected_network_id
    else:
        return "❌ Please select a network first."

    if tool:
        if tool == "list_clients":
            return format_result(meraki_tools.list_clients(network_id))

        elif tool == "list_devices":
            devices = meraki_tools.list_devices(network_id)
            st.session_state.map_data = [
                {"lat": d["lat"], "lon": d["lng"]} for d in devices if d.get("lat") and d.get("lng")
            ]
            return format_result(devices)

        elif tool == "list_ssids":
            return format_result(meraki_tools.list_ssids(network_id))

        elif tool == "list_vlans":
            return format_result(meraki_tools.list_vlans(network_id))

        elif tool == "list_access_points":
            return format_result(meraki_tools.list_access_points(network_id))

        elif tool == "list_switches":
            return format_result(meraki_tools.list_switches(network_id))

        elif tool == "list_uplinks":
            return format_result(meraki_tools.list_uplinks(network_id))

        elif tool == "list_firewall_events":
            return format_result(meraki_tools.list_firewall_events(network_id))

        elif tool == "vpn_status":
            return format_result(meraki_tools.get_vpn_status(meraki_tools.client, network_id))

    return ask_llm(f"You are a Cisco Meraki expert. Answer this: {user_query}")
