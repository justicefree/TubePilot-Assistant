import streamlit as st
import traceback

# MUST be the first Streamlit command
st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

try:
    # ---- Imports ----
    from openai import OpenAI
    import pandas as pd
    from st_copy_to_clipboard import st_copy_to_clipboard
    import stripe

    # ----------------------------
    # 1) SECRETS (SAFE GET)
    # ----------------------------
    OPENAI_KEY = st.secrets.get("openai_api_key", "")
    STRIPE_KEY = st.secrets.get("stripe_secret_key", "")
    STRIPE_UPGRADE_LINK = st.secrets.get("stripe_link_live", "")

    # Create clients only if configured
    client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None
    stripe.api_key = STRIPE_KEY if STRIPE_KEY else None

    # ----------------------------
    # 2) HELPERS
    # ----------------------------
    ADMIN_EMAILS = {"ml.channel7002@gmail.com"}

    def get_user_email() -> str:
        return (getattr(st.user, "email", "") or "").strip().lower()

    def get_user_name() -> str:
        return (getattr(st.user, "name", "") or "Creator").strip()

    def is_subscribed(email: str) -> bool:
        if not email:
            return False

        if email in ADMIN_EMAILS:
            return True

        # If Stripe isn't configured, treat as not subscribed (no crash)
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
    # 3) AUTH CHECK (SINGLE-PROVIDER MODE)
    # ----------------------------
    # If auth isn't activated in this deployment, show a clear message and stop.
    if not hasattr(st, "user") or not hasattr(st.user, "is_logged_in"):
        st.title("🚀 TubePilot Assistant")
        st.error(
            "Authentication is not active in this deployment.\n\n"
            "In Streamlit Secrets, use ONLY:\n"
            "[auth]\n"
            "redirect_uri, cookie_secret, client_id, client_secret, server_metadata_url\n\n"
            "Then reboot the app."
        )
        st.stop()

    if not st.user.is_logged_in:
        cols = st.columns([1, 2, 1])
        with cols[1]:
            st.title("🚀 TubePilot Assistant")
            st.write("### The AI Command Center for Creators")
st.write("Log in to access your creator tools.")
            # IMPORTANT: single-provider mode -> st.login() with NO provider argument
            st.button(
                "Log in with Google",
                type="primary",
                use_container_width=True,
                on_click=st.login,
            )
        st.stop()

    # Logged in
    user_email = get_user_email()
    user_name = get_user_name()
    has_access = is_subscribed(user_email)

    # ----------------------------
    # 4) SIDEBAR
    # ----------------------------
    with st.sidebar:
        st.title(f"Hi, {user_name}!")
        if user_email:
            st.caption(user_email)

        if not has_access:
            st.warning("🔒 Premium Required")
            if STRIPE_UPGRADE_LINK:
                st.link_button("💳 Upgrade for $15/mo", STRIPE_UPGRADE_LINK, use_container_width=True)
            else:
                st.info("Upgrade link not configured (`stripe_link_live`).")
        else:
            st.success("✅ Premium Active")

        st.button("Logout", on_click=st.logout)

    # ----------------------------
    # 5) MAIN
    # ----------------------------
    st.title("📺 TubePilot Control Center")

    if not has_access:
        st.header("Ready to grow your channel?")
        st.write("Upgrade to TubePilot Premium to unlock our AI SEO Agents and Retention Analytics.")
        st.info("Your subscription directly supports the development of more creator tools!")
        st.stop()

    # ----------------------------
    # 6) PREMIUM FEATURES
    # ----------------------------
    tab1, tab2, tab3 = st.tabs(["SEO Keyword Agent", "Retention AI", "Topic Research"])

    with tab1:
        st.header("SEO Keyword Agent")
        topic = st.text_input("What is your next video about?")
        if topic:
            if not client:
                st.error("OpenAI is not configured. Add `openai_api_key` to Streamlit Secrets.")
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
                st.error("OpenAI is not configured. Add `openai_api_key` to Streamlit Secrets.")
            else:
                with st.spinner("Analyzing viral trends..."):
                    res = client.responses.create(model="gpt-5-nano", input=f"5 ideas for {niche}")
                    st_copy_to_clipboard(res.output_text)
                    st.markdown(res.output_text)

except Exception as e:
    # Do NOT call st.set_page_config here (it must only be first)
    st.title("❌ TubePilot crashed — error below")
    st.error(str(e))
    st.code(traceback.format_exc())
    st.stop()
