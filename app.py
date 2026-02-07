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
    # multi_cell preserves line breaks and wraps text
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
    st.caption("v1.6 | Clean Revert + IEEE 829 & PDF")
    if not groq_key: st.stop()

jarvis = JarvisPOC(groq_key, model_name)

# --- MAIN WORKFLOW ---
user_story = st.text_area("Input Requirement / User Story:", height=150)

# Reverted to v1 Tab structure with Strategy & Plan added
tabs = st.tabs(["🔍 Evaluator", "🧪 Test Gen", "📜 Strategy & Plan", "💻 Scripts", "🔢 Data Factory"])

# 1. EVALUATOR
with tabs[0]:
    if st.button("Audit Story"):
        res = jarvis.ask("Senior QA Lead", f"Analyze for INVEST & ambiguity: {user_story}")
        with st.container(height=400, border=True): 
            st.markdown(res)
        st.code(res) # Copy option

# 2. TEST GEN
with tabs[1]:
    if st.button("Generate Suite"):
        res = jarvis.ask("QA Architect", f"Generate Happy, Negative, and Edge test cases for: {user_story}")
        st.session_state['v1_tc'] = res
        with st.container(height=450, border=True): 
            st.markdown(res)
        st.code(res)

# 3. TEST STRATEGY & PLAN (IEEE 829 Support)
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Gen IEEE 829 Strategy"):
            res = jarvis.ask("QA Director", f"Generate an IEEE 829 Test Strategy (Scope, Tools, Metrics) for: {user_story}")
            st.session_state['v1_strat'] = res
        if 'v1_strat' in st.session_state:
            with st.container(height=400, border=True): st.markdown(st.session_state['v1_strat'])
            pdf_bytes = create_pdf("Test Strategy (IEEE 829)", st.session_state['v1_strat'])
            st.download_button("📥 Download PDF", data=pdf_bytes, file_name="Strategy.pdf", mime="application/pdf", key="strat_dl")

    with c2:
        if st.button("Gen IEEE 829 Plan"):
            res = jarvis.ask("QA Manager", f"Generate an IEEE 829 Test Plan (Items, Risks, Criteria) for: {user_story}")
            st.session_state['v1_plan'] = res
        if 'v1_plan' in st.session_state:
            with st.container(height=400, border=True): st.markdown(st.session_state['v1_plan'])
            pdf_bytes = create_pdf("Test Plan (IEEE 829)", st.session_state['v1_plan'])
            st.download_button("📥 Download PDF", data=pdf_bytes, file_name="Plan.pdf", mime="application/pdf", key="plan_dl")

# 4. SCRIPT GEN
with tabs[3]:
    frame = st.selectbox("Framework", ["Cypress", "Playwright", "Selenium"])
    if st.button("Generate Automation"):
        res = jarvis.ask("SDET", f"Write {frame} scripts for: {st.session_state.get('v1_tc', user_story)}")
        with st.container(height=450, border=True): 
            st.code(res)

# 5. DATA FACTORY
with tabs[4]:
    fields = st.multiselect("Fields", ["name", "email", "phone_number", "company"])
    if st.button("Generate Fake Data"):
        st.table([{f: getattr(fake, f)() for f in fields} for _ in range(5)])
