import streamlit as st
from openai import OpenAI

# --- 1. PAGE CONFIG & LOGO ---
st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

# Initialize OpenAI Client
# This grabs the key you just saved in your Secret Box
client = OpenAI(api_key=st.secrets["openai_api_key"])

# --- 2. AUTHENTICATION (The "Final" 2026 Way) ---
if not st.user.is_logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.title("🚀 TubePilot Assistant")
        st.write("### AI-Powered Strategy for Creators")
        st.info("Please log in to access your SEO Agents and Content Dashboard.")
        
        # Using on_click for a smoother 2026 experience
        st.button("Log in with Google", type="primary", use_container_width=True, on_click=st.login, args=["google"])
        
        st.divider()
        st.caption("Secure login powered by Google Identity.")
    st.stop()

# --- 3. LOGGED-IN SIDEBAR ---
with st.sidebar:
    # Safely get user info
    user_name = st.user.get("name", "Creator")
    user_email = st.user.get("email", "")
    user_pic = st.user.get("picture", "")

    if user_pic:
        st.image(user_pic, width=80)
    
    st.title(f"Hi, {user_name}!")
    st.caption(f"📧 {user_email}")
    
    st.divider()
    
    # Subscription Management
    st.subheader("Subscription")
    st.write("Plan: **TubePilot Premium ($15/mo)**")
    st.link_button("💳 Manage Subscription", st.secrets["stripe"]["stripe_link_live"], use_container_width=True)
    
    st.divider()
    st.button("Logout", on_click=st.logout, use_container_width=True)

# --- 4. MAIN DASHBOARD ---
st.title("📺 TubePilot Control Center")

tab1, tab2, tab3 = st.tabs(["SEO Keyword Agent", "Retention AI", "Topic Research"])

with tab1:
    st.header("SEO Keyword Agent")
    topic = st.text_input("What is your next video about?", placeholder="e.g. How to grow on YouTube 2026")
    
    if topic:
        with st.spinner("GPT-5 Nano Agent is researching keywords..."):
            try:
                # 2026 Responses API call
                response = client.responses.create(
                    model="gpt-5-nano",
                    input=f"Act as a YouTube SEO Expert. For the topic '{topic}', provide: 1. 5 High-Volume Keywords. 2. 3 Viral Title Ideas. 3. An SEO description.",
                    text={"verbosity": "high"} 
                )
                
                if hasattr(response, 'output_text') and response.output_text:
                    st.markdown("### 🤖 Agent Recommendations")
                    st.markdown(response.output_text)
                    st.success("Analysis Complete!")
                else:
                    st.warning("Agent returned an empty response. Check OpenAI credits.")
            except Exception as e:
                st.error(f"Agent Error: {e}")

with tab2:
    st.header("Retention AI")
    st.write("Upload your retention data to find where viewers drop off.")
    uploaded_file = st.file_uploader("Upload YouTube CSV", type=["csv"])
    if uploaded_file:
        st.success("File uploaded! Logic to analyze retention patterns is ready for integration.")

with tab3:
    st.header("Topic Research")
    st.write("Generate high-CTR titles and thumbnail concepts.")
    research_query = st.text_input("Niche or Competitor URL")
    if st.button("Generate Ideas") and research_query:
        st.info("Agent is browsing current trends for your niche...")
        # Future logic for web-searching trends would go here
