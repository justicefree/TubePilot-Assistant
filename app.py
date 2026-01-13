import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
from st_copy_to_clipboard import st_copy_to_clipboard
import stripe

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

# --- 2. SECURE KEYS ---
OPENAI_KEY = st.secrets.get("openai_api_key")
STRIPE_KEY = st.secrets.get("stripe_secret_key")
client = OpenAI(api_key=OPENAI_KEY)
stripe.api_key = STRIPE_KEY

# --- 3. SUBSCRIPTION CHECK LOGIC ---
def is_subscribed(email):
    # --- ADMIN BYPASS ---
    # REPLACE THE EMAIL BELOW WITH YOUR ACTUAL GMAIL
    if email in ["ml.channel7002@gmail.com"]: 
        return True
    
    if not STRIPE_KEY:
        return False
        
    try:
        # Checks Stripe for active customers with this email
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            customer_id = customers.data[0].id
            subs = stripe.Subscription.list(customer=customer_id, status='active')
            return len(subs.data) > 0
    except Exception:
        return False
    return False

# --- 4. AUTHENTICATION GUARD ---
if not st.user.is_logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.title("🚀 TubePilot Assistant")
        st.write("### The AI Command Center for Creators")
        if st.button("Log in with Google", type="primary", use_container_width=True):
            st.login("google")
    st.stop()

# --- 5. PAYWALL CHECK ---
user_email = st.user.get("email")
has_access = is_subscribed(user_email)

# --- 6. LOGGED-IN SIDEBAR ---
with st.sidebar:
    st.title(f"Hi, {st.user.get('name')}!")
    if not has_access:
        st.warning("🔒 Premium Required")
        st.link_button("💳 Upgrade for $15/mo", st.secrets["stripe_link_live"], use_container_width=True)
    else:
        st.success("✅ Premium Active")
    
    if st.button("Logout"):
        st.logout()

# --- 7. MAIN DASHBOARD ---
st.title("📺 TubePilot Control Center")

if not has_access:
    st.header("Ready to grow your channel?")
    st.write("Upgrade to TubePilot Premium to unlock our AI SEO Agents and Retention Analytics.")
    st.info("Your subscription directly supports the development of more creator tools!")
    st.stop() # This line ensures you never pay for non-paying users!

# --- ALL PREMIUM FEATURES BELOW THIS LINE ---
tab1, tab2, tab3 = st.tabs(["SEO Keyword Agent", "Retention AI", "Topic Research"])

with tab1:
    st.header("SEO Keyword Agent")
    topic = st.text_input("What is your next video about?")
    if topic:
        with st.spinner("AI Agent at work..."):
            res = client.responses.create(model="gpt-5-nano", input=f"SEO for: {topic}")
            st_copy_to_clipboard(res.output_text)
            st.markdown(res.output_text)

with tab2:
    st.header("Retention AI")
    uploaded_file = st.file_uploader("Upload YouTube CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df) # Your visualization code remains safe here

with tab3:
    st.header("Topic Research")
    niche = st.text_input("Your niche?")
    if st.button("Generate Ideas") and niche:
        with st.spinner("Analyzing viral trends..."):
            res = client.responses.create(model="gpt-5-nano", input=f"5 ideas for {niche}")
            st_copy_to_clipboard(res.output_text)
            st.markdown(res.output_text)
