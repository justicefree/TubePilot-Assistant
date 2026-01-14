import streamlit as st

# Show errors in the app instead of a generic "Internal server error"
import traceback

try:
    # ======= YOUR ORIGINAL IMPORTS =======
    from openai import OpenAI
    import pandas as pd
    import plotly.express as px
    from st_copy_to_clipboard import st_copy_to_clipboard
    import stripe
    import authlib  # will crash here if Authlib isn't installed

    # ----------------------------
    # 1) PAGE CONFIG
    # ----------------------------
    st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")

    # Quick sanity checks (safe to show)
    st.write("✅ App booted")
    st.write("Authlib version:", getattr(authlib, "__version__", "unknown"))

    # ----------------------------
    # 2) READ SECRETS SAFELY
    # ----------------------------
    OPENAI_KEY = st.secrets.get("openai_api_key", "")
    STRIPE_KEY = st.secrets.get("stripe_secret_key", "")
    STRIPE_UPGRADE_LINK = st.secrets.get("stripe_link_live", "")

    st.write("OpenAI key present:", bool(OPENAI_KEY), "length:", len(OPENAI_KEY))
    st.write("Stripe key present:", bool(STRIPE_KEY))
    st.write("Stripe upgrade link present:", bool(STRIPE_UPGRADE_LINK))

    client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None
    stripe.api_key = STRIPE_KEY if STRIPE_KEY else None

    # ----------------------------
    # 3) SUBSCRIPTION CHECK
    # ----------------------------
    ADMIN_EMAILS = {"ml.channel7002@gmail.com"}

    def is_subscribed(email: str) -> bool:
        if not email:
            return False
        email = email.strip().lower()
        if email in ADMIN_EMAILS:
            return True
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
    # 4) AUTH GUARD
    # ----------------------------
    if not st.user.is_logged_in:
        cols = st.columns([1, 2, 1])
        with cols[1]:
            st.title("🚀 TubePilot Assistant")
            st.write("### The AI Command Center for Creators")
            st.button(
                "Log in with Google",
                type="primary",
                use_container_width=True,
                on_click=lambda: st.login("google"),
            )
        st.stop()

    user_email = (getattr(st.user, "email", "") or "").strip().lower()
    user_name = (getattr(st.user, "name", "") or "Creator").strip()

    st.write("✅ Logged in as:", user_email)

    has_access = is_subscribed(user_email)

    # ----------------------------
    # 5) SIDEBAR
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
    # 6) MAIN UI
    # ----------------------------
    st.title("📺 TubePilot Control Center")

    if not has_access:
        st.header("Ready to grow your channel?")
        st.write("Upgrade to TubePilot Premium to unlock our AI SEO Agents and Retention Analytics.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["SEO Keyword Agent", "Retention AI", "Topic Research"])

    with tab1:
        st.header("SEO Keyword Agent")
        topic = st.text_input("What is your next video about?")
        if topic:
            if not client:
                st.error("OpenAI is not configured. Add `openai_api_key` to Secrets.")
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
                st.error("OpenAI is not configured. Add `openai_api_key` to Secrets.")
            else:
                with st.spinner("Analyzing viral trends..."):
                    res = client.responses.create(model="gpt-5-nano", input=f"5 ideas for {niche}")
                    st_copy_to_clipboard(res.output_text)
                    st.markdown(res.output_text)

except Exception as e:
    st.set_page_config(page_title="TubePilot Assistant", page_icon="🚀", layout="wide")
    st.title("❌ TubePilot crashed — real error below")
    st.error(str(e))
    st.code(traceback.format_exc())
    st.stop()
