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
    .stTextArea>div>div>textarea { font-family: 'Courier New', Monospace; border: 1px solid #ddd; }
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

# --- AI ENGINE ---
class JarvisAI:
    def __init__(self, key, model):
        self.client = openai.OpenAI(api_key=key)
        self.model = model

    def ask(self, role, content):
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": f"You are a {role}."}, {"role": "user", "content": content}],
                temperature=0.1
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧠 Jarvis Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    model = st.selectbox("LLM Model", ["gpt-4o", "gpt-4-turbo"])
    st.divider()
    st.header("🔗 Integrations")
    source_type = st.radio("Sync Source", ["Manual", "Jira", "Azure DevOps"])
    if source_type == "Jira":
        j_domain = st.text_input("Jira Domain")
        j_email = st.text_input("Email")
        j_token = st.text_input("Token", type="password")
    elif source_type == "Azure DevOps":
        a_org = st.text_input("Org")
        a_proj = st.text_input("Project")
        a_pat = st.text_input("PAT", type="password")

# --- MAIN UI ---
st.title("🛡️ Jarvis: Enterprise QA Generation Tool")

if not api_key:
    st.info("👋 Enter your OpenAI API key in the sidebar to begin.")
    st.stop()

jarvis = JarvisAI(api_key, model)

# 1. Input Section
st.subheader("1. Requirements Ingestion")
col_in, col_bt = st.columns([4, 1])
with col_in:
    item_id = st.text_input("Issue Key / ID", placeholder="e.g. QA-123")
with col_bt:
    st.write(" ")
    if st.button("Fetch"):
        if source_type == "Jira":
            st.session_state['req_content'] = fetch_jira_data(j_domain, j_email, j_token, item_id)
        elif source_type == "Azure DevOps":
            st.session_state['req_content'] = fetch_azure_data(a_org, a_proj, a_pat, item_id)

user_story = st.text_area("Requirement Content:", value=st.session_state.get('req_content', ""), height=150)

# 2. Main Workflow Tabs
tabs = st.tabs(["🔍 Evaluator", "📝 BDD", "🧪 Test Gen", "🛡️ Edge Cases", "💻 Script Gen", "📊 Audit", "🔢 Data", "📤 Export", "🔄 Feedback Loop"])

with tabs[0]: # Evaluator
    if st.button("Evaluate"):
        st.markdown(jarvis.ask("Senior QA Architect", f"Analyze for INVEST & ambiguity: {user_story}"))

with tabs[1]: # BDD
    if st.button("Gen Gherkin"):
        res = jarvis.ask("BDD Specialist", f"Convert to Gherkin: {user_story}")
        st.session_state['bdd'] = res
        st.code(res, language='gherkin')

with tabs[2]: # Test Gen
    if st.button("Gen Tests"):
        res = jarvis.ask("QA Manager", f"Generate Test Suite for: {st.session_state.get('bdd', user_story)}")
        st.session_state['tc'] = res
        st.markdown(res)

with tabs[3]: # Edge Case
    if st.button("Explore Security"):
        st.markdown(jarvis.ask("Security Engineer", f"Identify complex edge cases for: {user_story}"))

with tabs[4]: # Script Gen
    framework = st.selectbox("Framework", ["Cypress", "Playwright", "Selenium"])
    if st.button("Gen Code"):
        res = jarvis.ask("SDET", f"Convert to {framework} code stubs: {st.session_state.get('tc', user_story)}")
        st.code(res)

with tabs[5]: # Audit
    if st.button("Audit"):
        st.markdown(jarvis.ask("QA Auditor", f"Check for logic gaps in: {st.session_state.get('tc', '')}"))

with tabs[6]: # Data Factory
    fields = st.multiselect("Fields", ["name", "email", "phone_number", "company"])
    rows = st.slider("Count", 1, 50, 5)
    if st.button("Gen Data"):
        st.table([{f: getattr(fake, f)() for f in fields} for _ in range(rows)])

with tabs[7]: # Export
    if st.button("Jira CSV"):
        res = jarvis.ask("Data Architect", f"Format as Jira CSV: {st.session_state.get('tc', '')}")
        st.download_button("Download", data=res, file_name="jira.csv")

# 🔄 3. FEEDBACK LOOP (NEW)
with tabs[8]:
    st.subheader("Analysis of Test Execution Failures")
    log_input = st.text_area("Paste Execution Logs / Error Stack Trace:", height=200)
    if st.button("Analyze Failure"):
        prompt = (f"Analyze this test failure log: {log_input}. "
                  f"Compare it against the requirement: {user_story}. "
                  "Identify if it is a 'Script Issue', 'Environment Issue', or 'Actual Bug'. "
                  "Suggest specific fixes for the Test Case or Automation Script.")
        st.markdown(jarvis.ask("Test Automation Consultant", prompt))
