import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

# --- 2. SECURE CLIENT INITIALIZATION ---
if "openai_api_key" in st.secrets:
    client = OpenAI(api_key=st.secrets["openai_api_key"])
else:
    st.error("⚠️ Secret Key Missing: Please check your Streamlit Settings > Secrets.")
    st.stop()

# --- 3. AUTHENTICATION GUARD ---
if not st.user.is_logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.title("🚀 TubePilot Assistant")
        st.write("### AI-Powered Strategy for Creators")
        st.info("Please log in to access your SEO Agents and Content Dashboard.")
        if st.button("Log in with Google", type="primary", use_container_width=True):
            st.login("google")
        st.divider()
        st.caption("Secure login powered by Google Identity.")
    st.stop()

# --- 4. LOGGED-IN SIDEBAR ---
with st.sidebar:
    user_name = st.user.get("name", "Creator")
    user_pic = st.user.get("picture", "")
    if user_pic: st.image(user_pic, width=80)
    st.title(f"Hi, {user_name}!")
    st.divider()
    st.subheader("Subscription")
    st.write("Plan: **TubePilot Premium ($15/mo)**")
    if "stripe" in st.secrets:
        st.link_button("💳 Pay or Manage Subscription", st.secrets["stripe"]["stripe_link_live"], use_container_width=True)
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.logout()

# --- 5. MAIN DASHBOARD ---
st.title("📺 TubePilot Control Center")
tab1, tab2, tab3 = st.tabs(["SEO Keyword Agent", "Retention AI", "Topic Research"])

# --- TAB 1: SEO KEYWORD AGENT ---
with tab1:
    st.header("SEO Keyword Agent")
    topic = st.text_input("What is your next video about?", placeholder="e.g. How to grow on YouTube 2026", key="seo_input")
    if topic:
        with st.spinner("Agent researching..."):
            try:
                response = client.responses.create(
                    model="gpt-5-nano",
                    input=f"YouTube SEO for: {topic}. Provide 5 Keywords, 3 Titles, and a Description.",
                    text={"verbosity": "high"}
                )
                output = response.output_text
                st.subheader("🤖 Agent Recommendations")
                st_copy_to_clipboard(output) # Simplified: No 'before_text' to avoid errors
                st.markdown(output)
            except Exception as e:
                st.error(f"Error: {e}")

# --- TAB 2: RETENTION AI ---
with tab2:
    st.header("Retention AI")
    st.write("Upload your YouTube 'Table Data' CSV.")
    uploaded_file = st.file_uploader("Upload YouTube CSV", type=["csv"], key="retention_upload")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df = df[~df.iloc[:, 0].astype(str).str.contains('Total', na=False)]
            
            ret_col = 'Average percentage viewed (%)'
            dur_col = 'Duration'
            
            if ret_col in df.columns:
                df[ret_col] = pd.to_numeric(df[ret_col], errors='coerce')
                df[dur_col] = pd.to_numeric(df[dur_col], errors='coerce')
                df = df.dropna(subset=[ret_col])
                
                avg_ret = df[ret_col].mean()
                st.metric("Avg. Channel Retention", f"{avg_ret:.2f}%")
                
                with st.expander("🔍 View Raw Data Table"):
                    st.dataframe(df)

                fig = px.scatter(
                    df, x=dur_col, y=ret_col, 
                    hover_name=df.columns[0],
                    title="Retention vs. Video Length",
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Column '{ret_col}' not found.")
        except Exception as e:
            st.error(f"Analysis error: {e}")

# --- TAB 3: TOPIC RESEARCH ---
with tab3:
    st.header("Topic Research")
    niche = st.text_input("What is your channel's niche?", placeholder="e.g. Finance, Gaming, Cooking", key="niche_input")
    if st.button("Generate Ideas") and niche:
        with st.spinner("Analyzing..."):
            try:
                res = client.responses.create(
                    model="gpt-5-nano", 
                    input=f"Generate 5 viral video ideas for a {niche} channel."
                )
                topic_output = res.output_text
                st_copy_to_clipboard(topic_output) # Simplified to fix error
                st.markdown(topic_output)
            except Exception as e:
                st.error(f"Error: {e}")
