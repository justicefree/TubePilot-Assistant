import streamlit as st
from openai import OpenAI
import pandas as pd
from st_copy_to_clipboard import st_copy_to_clipboard
import stripe

# ----------------------------
# 1) PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

# ----------------------------
# 2) READ SECRETS SAFELY
# ----------------------------
OPENAI_KEY = st.secrets.get("openai_api_key", "")
STRIPE_KEY = st.secrets.get("stripe_secret_key", "")
STRIPE_UPGRADE_LINK = st.secrets.get("stripe_link_live", "")

# OpenAI client (only create if key exists)
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# Stripe
stripe.api_key = STRIPE_KEY if STRIPE_KEY else None

# ----------------------------
# 3) SMALL HELPERS
# ----------------------------
def get_user_email() -> str:
    # st.user is a Streamlit object; prefer attributes, fall back to dict-like access
    email = getattr(st.user, "email", None)
    if not email:
        try:
            email = st.user.get("email")  # some Streamlit versions allow .get
        except Exception:
            email = None
    return (email or "").strip().lower()


def get_user_name() -> str:
    name = getattr(st.user, "name", None)
    if not name:
        try:
            name = st.user.get("name")
        except Exception:
            name = None
    return (name or "Creator").strip()


def show_setup_missing(message: str):
    st.title("🚀 TubePilot Assistant")
    st.write("### The AI Command Center for Creators")
    st.error(message)
    st.info(
        "Fix this in **Streamlit Cloud → Manage app → Settings → Secrets**. "
        "After saving secrets, reload the app."
    )
    st.stop()


# ----------------------------
# 4) SUBSCRIPTION CHECK LOGIC
# ----------------------------
ADMIN_EMAILS = {"ml.channel7002@gmail.com"}  # keep as-is (lowercase is important)


def is_subscribed(email: str) -> bool:
    if not email:
        return False

    if email in ADMIN_EMAILS:
        return True

    # If Stripe isn’t configured, treat as not subscribed (no crash)
    if not STRIPE_KEY:
        return False

    try:
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            customer_id = customers.data[0].id
            subs = stripe.Subscription.list(customer=customer_id, status="active", limit=5)
            return len(subs.data) > 0
    except Exception:
        return False

    return False


# ----------------------------
# 5) AUTHENTICATION GUARD (FIXED)
# ----------------------------
# IMPORTANT: Do NOT call st.login("google") at import time.
# Only call it from a user action (button click).
if not st.user.is_logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.title("🚀 TubePilot Assistant")
        st.write("### The AI Command Center for Creators")
        st.write("Log in to access your creator tools.")

        st.button(
            "Log in with Google",
            type="primary",
            use_container_width=True,
            on_click=lambda: st.login("google"),
        )
    st.stop()

# ----------------------------
# 6) POST-LOGIN: VALIDATE SETUP
# ----------------------------
user_email = get_user_email()
user_name = get_user_name()

if not user_email:
    show_setup_missing(
        "Login succeeded, but your Google profile didn’t return an email. "
        "In Google OAuth consent / scopes, ensure email is allowed."
    )

# You can run the app without OpenAI/Stripe configured, but show clear messages
if not OPENAI_KEY:
    st.warning("OpenAI is not configured (missing `openai_api_key` in Secrets). Some features will be disabled.")
if not STRIPE_KEY:
    st.warning("Stripe is not configured (missing `stripe_secret_key` in Secrets). Paywall will act as locked.")
if not STRIPE_UPGRADE_LINK:
    st.warning("Stripe upgrade link is missing (`stripe_link_live` in Secrets). Upgrade button will be hidden.")

# ----------------------------
# 7) PAYWALL CHECK
# ----------------------------
has_access = is_subscribed(user_email)

# ----------------------------
# 8) SIDEBAR
# ----------------------------
with st.sidebar:
    st.title(f"Hi, {user_name}!")

    st.caption(user_email)

    if not has_access:
        st.warning("🔒 Premium Required")
        if STRIPE_UPGRADE_LINK:
            st.link_button("💳 Upgrade for $15/mo", STRIPE_UPGRADE_LINK, use_container_width=True)
        else:
            st.info("Upgrade link not configured in Secrets.")
    else:
        st.success("✅ Premium Active")

    st.button("Logout", on_click=st.logout)

# ----------------------------
# 9) MAIN DASHBOARD
# ----------------------------
st.title("📺 TubePilot Control Center")

if not has_access:
    st.header("Ready to grow your channel?")
    st.write("Upgrade to TubePilot Premium to unlock our AI SEO Agents and Retention Analytics.")
    st.info("Your subscription directly supports the development of more creator tools!")
    st.stop()

# ----------------------------
# 10) PREMIUM FEATURES
# ----------------------------
tab1, tab2, tab3 = st.tabs(["SEO Keyword Agent", "Retention AI", "Topic Research"])

with tab1:
    st.header("SEO Keyword Agent")
    topic = st.text_input("What is your next video about?")
    if topic:
        if not client:
            st.error("OpenAI is not configured. Add `openai_api_key` to Secrets to use this feature.")
        else:
            with st.spinner("AI Agent at work..."):
                res = client.responses.create(model="gpt-5-nano", input=f"SEO for: {topic}")
                st_copy_to_clipboard(res.output_text)
                st.markdown(res.output_text)

with tab2:
    st.header("Retention AI")
    uploaded_file = st.file_uploader("Upload YouTube CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

with tab3:
    st.header("Topic Research")
    niche = st.text_input("Your niche?")
    if st.button("Generate Ideas") and niche:
        if not client:
            st.error("OpenAI is not configured. Add `openai_api_key` to Secrets to use this feature.")
        else:
            with st.spinner("Analyzing viral trends..."):
                res = client.responses.create(model="gpt-5-nano", input=f"5 ideas for {niche}")
                st_copy_to_clipboard(res.output_text)
                st.markdown(res.output_text)
