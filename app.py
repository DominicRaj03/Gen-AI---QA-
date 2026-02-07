import streamlit as st
from groq import Groq
from faker import Faker
from fpdf import FPDF

# --- INITIALIZATION ---
st.set_page_config(page_title="Gen AI - Quality Assurance", layout="wide", page_icon="🛡️")
fake = Faker()

# --- UTILITY: PDF GENERATOR ---
def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    safe_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=safe_text)
    return bytes(pdf.output()) # Explicitly return bytes

# --- ENGINE ---
class JarvisPOC:
    def __init__(self, key, model):
        self.client = Groq(api_key=key)
        self.model = model

    def ask(self, role, prompt):
        with st.spinner(f"🚀 Jarvis generating {role} output..."):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": f"You are a professional {role}."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                return resp.choices[0].message.content
            except Exception as e:
                return f"❌ Error: {str(e)}"

# --- UI ---
st.markdown("<h1 style='text-align: center;'>🛡️ Gen AI - Quality Assurance</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔑 Config")
    groq_key = st.text_input("Groq API Key", type="password")
    model_name = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    if not groq_key: st.stop()

jarvis = JarvisPOC(groq_key, model_name)
user_story = st.text_area("Input Story:", height=100)
tabs = st.tabs(["🔍 Evaluator", "🧪 Test Gen", "📜 Strategy & Plan", "💻 Scripts", "🔢 Data"])

with tabs[2]: # Strategy & Plan Tab
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Gen Strategy"):
            st.session_state['strat'] = jarvis.ask("QA Director", f"IEEE 829 Strategy for: {user_story}")
        if 'strat' in st.session_state:
            st.markdown(st.session_state['strat'])
            st.download_button("📥 Download PDF", data=create_pdf("Strategy", st.session_state['strat']), file_name="Strategy.pdf")
    with c2:
        if st.button("Gen Plan"):
            st.session_state['plan'] = jarvis.ask("QA Manager", f"IEEE 829 Plan for: {user_story}")
        if 'plan' in st.session_state:
            st.markdown(st.session_state['plan'])
            st.download_button("📥 Download PDF", data=create_pdf("Plan", st.session_state['plan']), file_name="Plan.pdf")
