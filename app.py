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
    # multi_cell ensures text doesn't get cut off in the PDF
    pdf.multi_cell(0, 10, txt=content.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S')

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

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center;'>🛡️ Gen AI - Quality Assurance</h1>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 Configuration")
    groq_key = st.text_input("Groq API Key", type="password")
    model_name = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    st.divider()
    if not groq_key: st.stop()

jarvis = JarvisPOC(groq_key, model_name)

# --- MAIN WORKFLOW ---
user_story = st.text_area("Input Requirement / User Story:", height=150)

# Back to original Tab structure with addition of Strategy & Plan
tabs = st.tabs(["🔍 Evaluator", "🧪 Test Gen", "📜 Strategy & Plan", "💻 Script Gen", "🔢 Data Factory"])

# 1. EVALUATOR
with tabs[0]:
    if st.button("Analyze Quality"):
        res = jarvis.ask("Senior QA Lead", f"Analyze for INVEST & ambiguity: {user_story}")
        with st.container(height=400, border=True): st.markdown(res)
        st.code(res)

# 2. TEST GEN
with tabs[1]:
    if st.button("Build Test Suite"):
        res = jarvis.ask("QA Architect", f"Generate Happy, Negative, and Edge
