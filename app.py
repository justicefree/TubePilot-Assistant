import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px

# --- 1. PAGE CONFIG & LOGO ---
st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

# Initialize OpenAI Client securely from secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])

# --- 2. AUTHENTICATION (Google OIDC) ---
if not st.user.is_logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.title("🚀 TubePilot Assistant")
        st.write("### AI-Powered Strategy for Creators")
        st.info("Please log in to access your SEO Agents and Content Dashboard.")
        
        # Trigger Google Login
        if st.button("Log in with Google", type="primary", use_container_width=True):
            st.login("google")
        
        st.divider()
        st.caption("Secure login powered by Google Identity.")
    st.stop()

# --- 3. LOGGED-IN SIDEBAR ---
with st.sidebar:
    # Get user profile info
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
    # Grabs the link from your secrets
    st.link_button("💳 Pay or Manage Subscription", st.secrets["stripe"]["stripe_link_live"], use_container_width=True)
    
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.logout()

# --- 4. MAIN DASHBOARD ---
st.title("📺 TubePilot Control Center")
st.write("Welcome to your command center. Use the agents below to grow your channel.")

tab1, tab2, tab3 = st.tabs(["SEO Keyword Agent", "Retention AI", "Topic Research"])

# --- TAB 1: SEO KEYWORD AGENT ---
with tab1:
    st.header("SEO Keyword Agent")
    topic = st.text_input("What is your next video about?", placeholder="e.g. How to grow on YouTube 2026")
    
    if topic:
        with st.spinner("GPT-5 Nano Agent is researching keywords..."):
            try:
                # 2026 GPT-5 Nano Responses API
                response = client.responses.create(
                    model="gpt-5-nano",
                    input=f"Act as a YouTube SEO Expert. For the topic '{topic}', provide: 1. 5 High-Volume Keywords. 2. 3 Viral Title Ideas. 3. An SEO description.",
                    text={"verbosity": "high"} 
                )
                if hasattr(response, 'output_text'):
                    st.markdown("### 🤖 Agent Recommendations")
                    st.markdown(response.output_text)
                    st.success("Analysis Complete!")
            except Exception as e:
                st.error(f"Agent Error: {e}")

# --- TAB 2: RETENTION AI ---
with tab2:
    st.header("Retention AI")
    st.write("Upload your YouTube 'Table Data' CSV to find where viewers drop off.")
    uploaded_file = st.file_uploader("Upload YouTube CSV", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # Remove YouTube's 'Total' row if present
        if 'Total' in df.iloc[0].values:
            df = df.iloc[1:]

        try:
            if 'Average percentage viewed (%)' in df.columns:
                avg_ret = df['Average percentage viewed (%)'].astype(float).mean()
                st.metric("Avg. Channel Retention", f"{avg_ret:.2f}%")
                
                # Professional Plotly Chart
                fig = px.scatter(df, x="Duration", y="Average percentage viewed (%)", 
                                 hover_name="Video title", size="Views", 
                                 title="Retention vs. Video Length")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Analysis error: {e}")

# --- TAB 3: TOPIC RESEARCH ---
with tab3:
    st.header("Topic Research")
    st.write("Generate high-CTR titles and thumbnail concepts.")
    niche = st.text_input("What is your channel's niche?")
    
    if st.button("Generate Ideas") and niche:
        with st.spinner("Analyzing viral patterns..."):
            try:
                res = client.responses.create(
                    model="gpt-5-nano",
                    input=f"Generate 5 viral video ideas for a {niche} channel.",
                    text={"verbosity": "high"}
                )
                st.markdown(res.output_text)
            except Exception as e:
                st.error(f"Error: {e}")
               
