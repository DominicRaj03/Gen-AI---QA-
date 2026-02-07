import streamlit as st
from groq import Groq
import requests
import json
import pandas as pd
from requests.auth import HTTPBasicAuth
from faker import Faker

# --- INITIALIZATION ---
st.set_page_config(page_title="Jarvis QA POC (Free)", layout="wide", page_icon="🛡️")
fake = Faker()

# --- CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #00a152; color: white; font-weight: bold; }
    .stTextArea>div>div>textarea { font-family: 'monospace'; }
    </style>
    """, unsafe_allow_html=True)

# --- API HELPERS ---
def fetch_jira_data(domain, email, token, key):
    url = f"https://{domain}.atlassian.net/rest/api/3/issue/{key}"
    auth = HTTPBasicAuth(email, token)
    res = requests.get(url, auth=auth)
    if res.status_code == 200:
        data = res.json()
        return f"SUMMARY: {data['fields']['summary']}\nDESC: {str(data['fields'].get('description', ''))}"
    return f"Error: {res.status_code}"

def fetch_azure_data(org, project, pat, item_id):
    url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{item_id}?api-version=7.1"
    res = requests.get(url, auth=('', pat))
    if res.status_code == 200:
        fields = res.json()['fields']
        return f"TITLE: {fields['System.Title']}\nDESC: {fields.get('System.Description', '')}"
    return f"Error: {res.status_code}"

# --- FREE AI ENGINE (GROQ) ---
class JarvisFreeAI:
    def __init__(self, key, model):
        self.client = Groq(api_key=key)
        self.model = model

    def ask(self, role, content):
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a professional {role}."},
                    {"role": "user", "content": content}
                ],
                temperature=0.1
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"POC Error: {str(e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ POC Configuration")
    groq_key = st.text_input("Groq API Key (Free)", type="password", help="Get it from console.groq.com")
    model_name = st.selectbox("Model", ["llama3-70b-8192", "mixtral-8x7b-32768"])
    
    st.divider()
    st.header("🔗 External Sync")
    source_type = st.radio("Requirement Source", ["Manual", "Jira", "Azure DevOps"])
    if source_type == "Jira":
        j_domain = st.text_input("Domain")
        j_email = st.text_input("Email")
        j_token = st.text_input("Token", type="password")
    elif source_type == "Azure DevOps":
        a_org = st.text_input("Org")
        a_proj = st.text_input("Project")
        a_pat = st.text_input("PAT", type="password")

# --- MAIN UI ---
st.title("🛡️ Jarvis: QA Automation POC")
st.caption("Running on Open-Source Models via Groq Free Tier")

if not groq_key:
    st.warning("⚠️ Please enter a Groq API Key to enable AI features.")
    st.stop()

jarvis = JarvisFreeAI(groq_key, model_name)

# 1. Ingestion
st.subheader("1. Requirement Ingestion")
col_id, col_btn = st.columns([4, 1])
with col_id:
    item_id = st.text_input("Issue ID", placeholder="PROJ-101")
with col_btn:
    st.write(" ")
    if st.button("Fetch"):
        if source_type == "Jira":
            st.session_state['req'] = fetch_jira_data(j_domain, j_email, j_token, item_id)
        elif source_type == "Azure DevOps":
            st.session_state['req'] = fetch_azure_data(a_org, a_proj, a_pat, item_id)

user_story = st.text_area("Requirement Text:", value=st.session_state.get('req', ""), height=150)

# 2. Tabs Workflow
tabs = st.tabs(["🔍 Evaluator", "📝 BDD", "🧪 Test Gen", "🛡️ Edge Case", "💻 Script Gen", "🔄 Feedback", "🔢 Data", "📤 Export"])

with tabs[0]: # Evaluator
    if st.button("Run INVEST Audit"):
        st.markdown(jarvis.ask("Senior QA Architect", f"Evaluate for INVEST and ambiguity: {user_story}"))

with tabs[1]: # BDD
    if st.button("Generate Gherkin"):
        res = jarvis.ask("BDD Specialist", f"Convert to Given/When/Then: {user_story}")
        st.session_state['bdd'] = res
        st.code(res, language='gherkin')

with tabs[2]: # Test Gen
    if st.button("Generate Cases"):
        res = jarvis.ask("QA Manager", f"Generate Happy/Negative/Edge test cases for: {st.session_state.get('bdd', user_story)}")
        st.session_state['tc'] = res
        st.markdown(res)

with tabs[3]: # Edge Case
    if st.button("Explore Vulnerabilities"):
        st.markdown(jarvis.ask("Security Engineer", f"Identify Security/Perf edge cases: {user_story}"))

with tabs[4]: # Script Gen
    frame = st.selectbox("Framework", ["Cypress", "Playwright", "Selenium"])
    if st.button("Generate Code"):
        st.code(jarvis.ask("SDET", f"Write {frame} code for: {st.session_state.get('tc', user_story)}"))

with tabs[5]: # Feedback
    logs = st.text_area("Execution Logs:")
    if st.button("Analyze Logs"):
        st.markdown(jarvis.ask("QA Consultant", f"Analyze this failure log against the story: {logs} \nStory: {user_story}"))

with tabs[6]: # Data Factory
    fields = st.multiselect("Fields", ["name", "email", "phone_number", "company", "address"])
    rows = st.slider("Records", 1, 20, 5)
    if st.button("Generate Fake Data"):
        st.table([{f: getattr(fake, f)() for f in fields} for _ in range(rows)])

with tabs[7]: # Export
    if st.button("Jira CSV Format"):
        csv = jarvis.ask("Data Architect", f"Convert to Jira CSV (Summary, Issue Type, Priority, Description, Steps): {st.session_state.get('tc', '')}")
        st.download_button("Download CSV", csv, file_name="poc_tests.csv")
