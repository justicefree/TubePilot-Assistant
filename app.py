import streamlit as st
from st_paywall import add_auth
import google.generativeai as genai

# --- 1. MANDATORY PAGE SETUP (MUST BE FIRST) ---
st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

# --- 2. THE BOUNCER (Hard Paywall) ---
# This stops anyone who hasn't paid from seeing your secrets or logic.
add_auth(
    required=True,
    active_plan_minutes=1,
)

# Only people who paid reach this line:
st.title("🚀 Welcome to TubePilot Pro, " + st.user.email)

# --- 3. SECURE AI CONFIGURATION ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
You are 'TubePilot Brain', an elite YouTube growth consultant. 
Your tone is analytical, professional, and brutally honest. 
Focus on retention, curiosity gaps, and conversion efficiency.
"""

model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview", 
    system_instruction=SYSTEM_PROMPT
)

# --- 4. NAVIGATION & MODULES ---
st.sidebar.title("TubePilot Control")
menu = st.sidebar.radio(
    "Navigation", 
    ["Title & Hook", "Semantic SEO", "Retention Lab", "Lead-to-Cash"]
)

def get_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to the Brain: {str(e)}"

# --- 5. APP LOGIC (Your existing modules) ---
if menu == "Title & Hook":
    st.header("🪝 Title & Hook Optimizer")
    topic = st.text_input("Enter your video concept:")
    if st.button("Analyze"):
        with st.spinner("Brainstorming viral angles..."):
            result = get_response(f"Suggest 3 high-CTR titles and a 5-second opening hook for: {topic}")
            st.info(result)

elif menu == "Semantic SEO":
    st.header("🔍 Semantic SEO Explorer")
    topic = st.text_input("Target Topic for 2026 Analysis:")
    if st.button("Map Intent"):
        with st.spinner("Mapping AI search intent..."):
            result = get_response(f"Generate a 2026 semantic SEO map for: {topic}")
            st.success(result)

elif menu == "Retention Lab":
    st.header("🧪 Retention Lab: Script Audit")
    script = st.text_area("Paste your YouTube script here:", height=300)
    if st.button("Run Audit"):
        with st.spinner("Auditing for audience drop-offs..."):
            result = get_response(f"Perform a Retention Audit on this script. Identify boredom zones: {script}")
            st.markdown(result)

elif menu == "Lead-to-Cash":
    st.header("💰 Lead-to-Cash: Conversion")
    script = st.text_area("Paste Sales Script/CTA section:")
    if st.button("Check Bridge"):
        with st.spinner("Analyzing the sales bridge..."):
            result = get_response(f"Audit this script for business conversion and CTA strength: {script}")
            st.warning(result)
