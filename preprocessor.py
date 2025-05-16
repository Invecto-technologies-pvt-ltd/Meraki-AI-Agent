# preprocessor.py
# from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM

# Initialize Ollama for advanced NLP-based fallback
llm = OllamaLLM(model="mistral", temperature=0.1)

def match_tool(query: str):
    """
    Match the query with the most relevant tool using LLM or a hard-coded tool matcher.
    """
    query = query.lower()

    if "clients" in query or "list clients" in query:
        return "list_clients"
    if "vpn status" in query:
        return "vpn_status"
    if "vlan" in query:
        return "list_vlans"
    if "switch" in query or "switches" in query:
        return "list_switches"
    if "access point" in query or "ap " in query:
        return "list_access_points"
    if "firewall" in query or "security events" in query:
        return "list_firewall_events"
    if "devices" in query or "list devices" in query:
        return "list_devices"
    if "ssids" in query or "wifi" in query:
        return "list_ssids"
    if "uplinks" in query:
        return "list_uplinks"

    return "ask_llm"
