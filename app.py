import streamlit as st
import time
from groq import Groq
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from faker import Faker

# --- INITIALIZATION & STYLING ---
st.set_page_config(page_title="Gen AI - Quality Assurance", layout="wide", page_icon="🛡️")
fake = Faker()

# Custom CSS for Animations and UI
st.markdown("""
    <style>
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(1); opacity: 0.8; }
    }
    .pulse-shield { font-size: 70px; text-align: center; animation: pulse 2s infinite ease-in-out; }
    .fade-in { animation: fadeIn 1.5s; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .stButton>button { background-color: #00a152; color: white; border-radius: 8px; font-weight: bold; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ---
class JarvisPOC:
    def __init__(self, key, model):
        self.client = Groq(api_key=key)
        self.model = model

    def ask(self, role, content):
        # Professional loading context
        with st.spinner(f"🚀 Jarvis is analyzing as a {role}..."):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": f"You are a professional {role}."}, 
                              {"role": "user", "content": content}],
                    temperature=0.1
                )
                return resp.choices[0].message.content
            except Exception as e:
                return f"❌ Error: {str(e)}"

# --- WELCOME SCREEN ---
def welcome_ui():
    st.markdown('<div class="pulse-shield">🛡️</div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Gen AI - Quality Assurance</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='fade-in'>Next-Gen Software Testing Life Cycle Orchestrator</p>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Cycle Time", "-70%", "Efficiency")
    m2.metric("Defect Leakage", "-40%", "Quality")
    m3.metric("ROI", "5x", "Project Value")
    st.divider()

# --- SIDEBAR & AUTH ---
welcome_ui()

with st.sidebar:
    st.header("🔑 Secure Access")
    groq_key = st.text_input("Groq API Key", type="password", help="Enter key to unlock Jarvis features.")
    model_name = st.selectbox("Intelligence Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
    st.divider()
    st.header("🔗 Integrations")
    source = st.radio("Story Source", ["Manual", "Jira", "Azure DevOps"])
    if source != "Manual":
        st.info(f"Connecting to {source}...")

if not groq_key:
    st.info("👋 To begin the demo, please enter your Groq API key in the sidebar.")
    st.stop()

jarvis = JarvisPOC(groq_key, model_name)

# --- WORKFLOW TABS ---
user_story = st.text_area("Input Requirement / User Story:", height=150, placeholder="As a user, I want to...")

tabs = st.tabs(["🔍 Evaluator", "📝 BDD", "🧪 Test Gen", "🛡️ Edge Cases", "💻 Script Gen", "🔄 Feedback Loop", "🔢 Data Factory"])

with tabs[0]: # Evaluator
    if st.button("Analyze Quality"):
        st.markdown(jarvis.ask("Senior QA Lead", f"Analyze for INVEST & ambiguity: {user_story}"))

with tabs[1]: # BDD
    if st.button("Generate Gherkin"):
        res = jarvis.ask("BDD Specialist", f"Convert to Gherkin: {user_story}")
        st.session_state['bdd'] = res
        st.code(res, language='gherkin')

with tabs[2]: # Test Gen
    if st.button("Build Test Suite"):
        res = jarvis.ask("QA Architect", f"Generate Test Suite for: {st.session_state.get('bdd', user_story)}")
        st.session_state['tc'] = res
        st.markdown(res)

with tabs[3]: # Edge Cases
    if st.button("Scan Vulnerabilities"):
        st.markdown(jarvis.ask("Security Engineer", f"Identify complex edge cases: {user_story}"))

with tabs[4]: # Script Gen
    frame = st.selectbox("Framework", ["Cypress", "Playwright", "Selenium"])
    if st.button("Generate Script"):
        st.code(jarvis.ask("SDET", f"Write {frame} automation for: {st.session_state.get('tc', user_story)}"))

with tabs[5]: # Feedback
    logs = st.text_area("Paste Execution Logs:")
    if st.button("Perform RCA"):
        st.markdown(jarvis.ask("Test Automation Consultant", f"Analyze failure logs: {logs}"))

with tabs[6]: # Data
    fields = st.multiselect("Fields", ["name", "email", "phone_number", "company"])
    if st.button("Generate Data"):
        st.table([{f: getattr(fake, f)() for f in fields} for _ in range(5)])
