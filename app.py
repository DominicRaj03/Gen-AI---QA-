import streamlit as st
from groq import Groq
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from faker import Faker

# --- INITIALIZATION & STYLING ---
st.set_page_config(page_title="Gen AI - QA", layout="wide", page_icon="🛡️")
fake = Faker()

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #00a152; color: white; font-weight: bold; border-radius: 8px; height: 3em; }
    .stTextArea>div>div>textarea { font-family: 'monospace'; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- API INTEGRATIONS ---
def fetch_jira(domain, email, token, key):
    url = f"https://{domain}.atlassian.net/rest/api/3/issue/{key}"
    res = requests.get(url, auth=HTTPBasicAuth(email, token))
    if res.status_code == 200:
        fields = res.json()['fields']
        return f"SUMMARY: {fields['summary']}\nDESC: {str(fields.get('description', ''))}"
    return f"Error: {res.status_code}"

def fetch_azure(org, project, pat, item_id):
    url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{item_id}?api-version=7.1"
    res = requests.get(url, auth=('', pat))
    if res.status_code == 200:
        f = res.json()['fields']
        return f"TITLE: {f['System.Title']}\nDESC: {f.get('System.Description', '')}"
    return f"Error: {res.status_code}"

# --- GROQ ENGINE (Updated for 2026) ---
class JarvisPOC:
    def __init__(self, key, model):
        self.client = Groq(api_key=key)
        self.model = model

    def ask(self, role, content):
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": f"You are a {role}."}, 
                          {"role": "user", "content": content}],
                temperature=0.1
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("🧠 POC Settings")
    groq_key = st.text_input("Groq API Key (Free)", type="password")
    # Updated to 2026 high-performance models
    model_name = st.selectbox("LLM Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
    st.divider()
    st.header("🔗 Requirements Sync")
    source = st.radio("Source", ["Manual", "Jira", "Azure DevOps"])
    if source == "Jira":
        j_dom = st.text_input("Domain")
        j_user = st.text_input("Email")
        j_pass = st.text_input("Token", type="password")
    elif source == "Azure DevOps":
        a_org = st.text_input("Org")
        a_proj = st.text_input("Project")
        a_pat = st.text_input("PAT", type="password")

# --- MAIN INTERFACE ---
st.title("🛡️ Jarvis: Enterprise QA POC")

if not groq_key:
    st.info("💡 Get a free API key at console.groq.com to start the POC.")
    st.stop()

jarvis = JarvisPOC(groq_key, model_name)

# 1. Requirement Input
st.subheader("1. Requirement Context")
c1, c2 = st.columns([4, 1])
with c1:
    item_id = st.text_input("Requirement ID", placeholder="QA-123")
with c2:
    st.write(" ")
    if st.button("Sync Data"):
        if source == "Jira":
            st.session_state['req'] = fetch_jira(j_dom, j_user, j_pass, item_id)
        elif source == "Azure DevOps":
            st.session_state['req'] = fetch_azure(a_org, a_proj, a_pat, item_id)

user_story = st.text_area("Requirement Content:", value=st.session_state.get('req', ""), height=150)

# 2. Workflow Tabs
tabs = st.tabs(["🔍 Evaluator", "📝 BDD", "🧪 Test Gen", "🛡️ Edges", "💻 Script Gen", "🔄 Feedback", "🔢 Data"])

with tabs[0]: # Evaluator
    if st.button("Audit Story"):
        st.markdown(jarvis.ask("Senior QA Lead", f"Analyze for INVEST criteria: {user_story}"))

with tabs[1]: # BDD
    if st.button("Gen Gherkin"):
        res = jarvis.ask("BDD Expert", f"Convert to Gherkin: {user_story}")
        st.session_state['bdd'] = res
        st.code(res, language='gherkin')

with tabs[2]: # Test Gen
    if st.button("Gen Test Suite"):
        res = jarvis.ask("QA Architect", f"Generate Test Suite: {st.session_state.get('bdd', user_story)}")
        st.session_state['tc'] = res
        st.markdown(res)

with tabs[3]: # Edge Case
    if st.button("Find Vulnerabilities"):
        st.markdown(jarvis.ask("Security Engineer", f"Identify Security/Perf edge cases: {user_story}"))

with tabs[4]: # Script Gen
    frame = st.selectbox("Framework", ["Cypress", "Playwright", "Selenium"])
    if st.button("Gen Automation"):
        st.code(jarvis.ask("SDET", f"Write {frame} code for: {st.session_state.get('tc', user_story)}"))

with tabs[5]: # Feedback
    logs = st.text_area("Execution Logs:")
    if st.button("Analyze Failures"):
        st.markdown(jarvis.ask("QA Consultant", f"Analyze logs: {logs} \nStory: {user_story}"))

with tabs[6]: # Data
    fields = st.multiselect("Fields", ["name", "email", "company", "phone_number"])
    if st.button("Gen Fake Data"):
        st.table([{f: getattr(fake, f)() for f in fields} for _ in range(5)])
