import streamlit as st
from groq import Groq
from faker import Faker
from fpdf import FPDF
import json

# --- INITIALIZATION ---
st.set_page_config(page_title="Gen AI - Quality Assurance", layout="wide", page_icon="🛡️")
fake = Faker()

# --- CUSTOM CSS FOR THE GAUGE ---
st.markdown("""
    <style>
    .gauge-container {
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
    }
    .score-text {
        font-size: 60px;
        font-weight: bold;
        color: #00a152; /* Green for excellent */
        margin: 0;
    }
    .score-label { font-size: 20px; color: #555; }
    .stButton>button { background-color: #00a152; color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

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
    return bytes(pdf.output())

# --- ENGINE ---
class JarvisPOC:
    def __init__(self, key, model):
        self.client = Groq(api_key=key)
        self.model = model

    def ask(self, role, prompt, is_json=False):
        with st.spinner(f"🚀 Jarvis is analyzing as {role}..."):
            try:
                response_format = {"type": "json_object"} if is_json else None
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": f"You are a professional {role}."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format=response_format
                )
                return resp.choices[0].message.content
            except Exception as e:
                return f"❌ Error: {str(e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 Config")
    groq_key = st.text_input("Groq API Key", type="password")
    model_name = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    if not groq_key: st.stop()

jarvis = JarvisPOC(groq_key, model_name)

# --- MAIN INPUT ---
user_story = st.text_area("Input User Story / Requirement:", height=150)

if st.button("🚀 Evaluate & Analyze Story", use_container_width=True):
    # Specialized prompt to get the Score Gauge data
    audit_prompt = f"""Audit the following user story and return ONLY a JSON object with:
    'score': (int 0-100),
    'rating': 'Excellent'|'Good'|'Poor',
    'parameters': [{{'name': 'Clarity', 'score': '18/20', 'findings': '...'}}, ...],
    'recommendations': ['...', '...']
    Requirement: {user_story}"""
    
    st.session_state['audit_json'] = json.loads(jarvis.ask("Senior QA Lead", audit_prompt, is_json=True))

# --- TABS ---
tabs = st.tabs(["🔍 Evaluator", "🧪 Test Gen", "📜 Strategy & Plan", "💻 Scripts"])

with tabs[0]: # Evaluator
    if 'audit_json' in st.session_state:
        data = st.session_state['audit_json']
        
        # Render the Gauge (84/100 Look)
        st.markdown(f"""
            <div class="gauge-container">
                <p class="score-label">Total Score</p>
                <p class="score-text">{data['score']}<span style="font-size:25px; color:#888;">/100</span></p>
                <p style="color:#00a152;">✅ {data['rating']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Parameter Table
        df = pd.DataFrame(data['parameters'])
        st.table(df)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        for rec in data['recommendations']:
            st.write(f"- {rec}")

with tabs[1]: # Test Gen
    if st.button("Build Test Suite"):
        st.session_state['tc'] = jarvis.ask("QA Architect", f"Generate Happy, Negative, and Edge cases for: {user_story}")
    if 'tc' in st.session_state:
        st.markdown(st.session_state['tc'])

# ... (Continue with other tabs as per v1.10)
