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
    pdf.set_font("Arial", size=12)
    # Multi_cell handles long content wrapping automatically
    pdf.multi_cell(0, 10, txt=content)
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
                    messages=[{"role": "system", "content": f"You are a {role}. Follow industry standards (INVEST, IEEE 829)."}, 
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
    st.header("🔑 Config")
    groq_key = st.text_input("Groq API Key", type="password")
    model_name = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    if not groq_key: st.stop()

jarvis = JarvisPOC(groq_key, model_name)
user_story = st.text_area("Input Requirement:", height=100)

tabs = st.tabs(["🔍 Evaluator", "📝 Test Cases", "📜 Strategy & Plan", "💻 Scripts", "🔢 Data"])

# 1. EVALUATOR
with tabs[0]:
    if st.button("Audit Story"):
        res = jarvis.ask("Requirement Analyst", f"Audit for INVEST/ambiguity: {user_story}")
        with st.container(height=400, border=True): st.markdown(res)
        st.code(res) # Copy option

# 2. CATEGORIZED TEST CASES
with tabs[1]:
    if st.button("Generate Suite"):
        prompt = f"Categorize as [POSITIVE], [NEGATIVE], [DATA], [OUT-OF-BOX]: {user_story}"
        res = jarvis.ask("QA Lead", prompt)
        st.session_state['tc_suite'] = res
        with st.container(height=450, border=True): st.markdown(res)
        st.code(res)

# 3. TEST STRATEGY & PLAN (IEEE 829 + PDF)
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Gen IEEE 829 Strategy"):
            res = jarvis.ask("QA Director", f"IEEE 829 Test Strategy for: {user_story}")
            st.session_state['strat'] = res
        
        if 'strat' in st.session_state:
            with st.container(height=350, border=True): st.markdown(st.session_state['strat'])
            pdf_bytes = create_pdf("Test Strategy (IEEE 829)", st.session_state['strat'])
            st.download_button("📥 Download Strategy PDF", data=pdf_bytes, file_name="Test_Strategy.pdf", mime="application/pdf")

    with c2:
        if st.button("Gen IEEE 829 Plan"):
            res = jarvis.ask("QA Manager", f"IEEE 829 Test Plan for: {user_story}")
            st.session_state['plan'] = res
            
        if 'plan' in st.session_state:
            with st.container(height=350, border=True): st.markdown(st.session_state['plan'])
            pdf_bytes = create_pdf("Test Plan (IEEE 829)", st.session_state['plan'])
            st.download_button("📥 Download Plan PDF", data=pdf_bytes, file_name="Test_Plan.pdf", mime="application/pdf")

# 4. SCRIPT GEN
with tabs[3]:
    frame = st.selectbox("Framework", ["Cypress", "Playwright"])
    if st.button("Gen Code"):
        res = jarvis.ask("SDET", f"Write {frame} for: {st.session_state.get('tc_suite', user_story)}")
        with st.container(height=450, border=True): st.code(res)
