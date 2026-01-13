import streamlit as st

# --- 1. PAGE CONFIG & LOGO ---
st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

# --- 2. AUTHENTICATION (The "Final" 2026 Way) ---
# This checks if the user is logged in via Google
if not st.user.is_logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.title("🚀 TubePilot Assistant")
        st.write("### AI-Powered Strategy for Creators")
        st.info("Please log in to access your SEO Agents and Content Dashboard.")
        
        # This button triggers the Google Login window
        if st.button("Log in with Google", type="primary", use_container_width=True):
            st.login("google")
        
        st.divider()
        st.caption("Secure login powered by Google Identity.")
    st.stop()

# --- 3. LOGGED-IN SIDEBAR ---
with st.sidebar:
    st.image(st.user.get("picture", ""), width=80)
    st.title(f"Hi, {st.user.get('name', 'Creator')}!")
    st.write(f"📧 {st.user.get('email')}")
    
    st.divider()
    
    # Subscription Management
    st.subheader("Subscription")
    st.write("Plan: **TubePilot Premium ($15/mo)**")
    st.link_button("💳 Pay or Manage Subscription", "https://buy.stripe.com/6oUfZgbGN8t65YAbZtf7i00", use_container_width=True)
    
    st.divider()
    if st.button("Logout"):
        st.logout()

# --- 4. MAIN DASHBOARD ---
st.title("📺 TubePilot Control Center")
st.write("Welcome to your command center. Use the agents below to grow your channel.")

tab1, tab2, tab3 = st.tabs(["SEO Keyword Agent", "Retention AI", "Topic Research"])

with tab1:
    st.header("SEO Keyword Agent")
    topic = st.text_input("What is your next video about?", placeholder="e.g. How to grow on YouTube 2026")
    if topic:
        st.success(f"Agent is analyzing keywords for: {topic}")
        # Add your AI analysis logic here

with tab2:
    st.header("Retention AI")
    st.write("Upload your retention data to find where viewers drop off.")
    st.file_uploader("Upload YouTube CSV", type=["csv"])

with tab3:
    st.header("Topic Research")
    st.write("Generate high-CTR titles and thumbnail concepts.")
    if st.button("Generate Ideas"):
        st.write("1. 10 Secrets YouTube Gurus Won't Tell You")
        st.write("2. Why My Channel Blew Up in 24 Hours")
