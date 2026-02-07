import streamlit as st
import openai
import requests
import json
import pandas as pd
from requests.auth import HTTPBasicAuth
from faker import Faker

# --- INITIALIZATION & CONFIG ---
st.set_page_config(page_title="Jarvis QA Suite", layout="wide", page_icon="🤖")
fake = Faker()

# --- CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #0047AB; color: white; font-weight: bold; }
    .stTextArea>div>div>textarea { font-family: 'Courier New', Monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS: EXTERNAL API FETCH ---
def fetch_jira_data(domain, email, token, key):
    url = f"https://{domain}.atlassian.net/rest/api/3/issue/{key}"
    auth = HTTPBasicAuth(email, token)
    res = requests.get(url, auth=auth)
    if res.status_code == 200:
        data = res.json()
        return f"SUMMARY: {data['fields']['summary']}\nDESCRIPTION: {data['fields'].get('description', '')}"
    return f"Error: {res.status_code}"

def fetch_azure_data(org, project, pat, item_id):
    url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{item_id}?api-version=7.1"
    res = requests.get(url, auth=('', pat))
    if res.status_code == 200:
        fields = res.json()['fields']
        return f"TITLE: {fields['System.Title']}\nDESCRIPTION: {fields.get('System.Description', '')}"
    return f"Error: {res.status_code}"

# --- SIDEBAR: JARVIS CONFIG ---
with st.sidebar:
    st.header("🧠 Jarvis Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    model = st.selectbox("LLM Model", ["gpt-4o", "gpt-4-turbo"])
    
    st.divider()
    st.header("🔗 External Integrations")
    source_type = st.radio("Sync Source", ["Manual", "Jira", "Azure DevOps"])
    
    if source_type == "Jira":
        j_domain = st.text_input("Jira Domain (company.atlassian.net)")
        j_email = st.text_input("Jira Email")
        j_token = st.text_input("Jira API Token", type="password")
    elif source_type == "Azure DevOps":
        a_org = st.text_input("Azure Org Name")
        a_proj = st.text_input("Project Name")
        a_pat = st.text_input("Personal Access Token", type="password")

# --- AI LOGIC CLASS ---
class JarvisAI:
    def __init__(self, key, model):
        self.client = openai.OpenAI(api_key=key)
        self.model = model

    def ask(self, system_msg, user_msg):
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.1
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"Error calling AI: {str(e)}"

# --- MAIN APP FLOW ---
st.title("🛡️ Jarvis: Enterprise QA Generation Tool")

if not api_key:
    st.info("👋 Welcome! Please enter your OpenAI API key in the sidebar to begin.")
    st.stop()

jarvis = JarvisAI(api_key, model)

# Step 1: Input Management
st.subheader("1. Requirements Input")
col_input, col_btn = st.columns([4, 1])

with col_input:
    item_id = st.text_input("Issue ID / Work Item ID", placeholder="e.g., SCRUM-42 or 1024")

with col_btn:
    st.write(" ")
    if st.button("Fetch Requirement"):
        if source_type == "Jira":
            st.session_state['req_content'] = fetch_jira_data(j_domain, j_email, j_token, item_id)
        elif source_type == "Azure DevOps":
            st.session_state['req_content'] = fetch_azure_data(a_org, a_proj, a_pat, item_id)
        else:
            st.warning("Select Jira or Azure in sidebar first.")

user_story = st.text_area("Content for Processing:", value=st.session_state.get('req_content', ""), height=150)

# Step 2: Processing Tabs
tabs = st.tabs(["🔍 Evaluator", "📝 Prep", "🧪 Gen", "📊 Audit", "🔢 Data Factory", "📤 Export"])

# -- 1. EVALUATOR --
with tabs[0]:
    if st.button("Evaluate INVEST"):
        res = jarvis.ask("You are a Senior QA Architect.", f"Evaluate this for INVEST criteria & ambiguity: {user_story}")
        st.markdown(res)

# -- 2. PREP (BDD) --
with tabs[1]:
    if st.button("Generate Scenarios"):
        res = jarvis.ask("You are a BDD Specialist.", f"Convert this to Gherkin Given/When/Then scenarios: {user_story}")
        st.session_state['bdd'] = res
        st.code(res, language='gherkin')

# -- 3. TEST GEN --
with tabs[2]:
    context = st.session_state.get('bdd', user_story)
    if st.button("Generate Test Suite"):
        res = jarvis.ask("You are a Lead QA Engineer.", f"Generate a Test Case Suite with Happy/Negative/Edge paths for: {context}")
        st.session_state['tc'] = res
        st.markdown(res)

# -- 4. AUDIT --
with tabs[3]:
    if st.button("Run QA Audit"):
        res = jarvis.ask("You are a QA Auditor.", f"Identify logic gaps and redundancies in these tests: {st.session_state.get('tc', '')}")
        st.markdown(res)

# -- 5. DATA FACTORY --
with tabs[4]:
    fields = st.multiselect("Data Fields", ["name", "email", "phone_number", "ssn", "address", "company"])
    rows = st.slider("Count", 1, 50, 5)
    if st.button("Generate Synthetic Data"):
        data = [{f: getattr(fake, f)() for f in fields} for _ in range(rows)]
        st.table(data)
        st.session_state['test_data'] = data

# -- 6. EXPORT --
with tabs[5]:
    st.subheader("Export for Jira / Azure")
    if 'tc' in st.session_state:
        if st.button("Prepare Jira CSV"):
            csv_prompt = f"Convert these to CSV format (Summary, Issue Type, Priority, Description, Steps): {st.session_state['tc']}"
            csv_str = jarvis.ask("You are a Data Architect.", csv_prompt)
            st.download_button("Download CSV", data=csv_str, file_name="jira_import.csv", mime="text/csv")
    else:
        st.info("Generate test cases first to enable export.")
