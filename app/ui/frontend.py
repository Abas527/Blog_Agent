import streamlit as st
import sys
import os

# Fix import paths (important for Streamlit)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.graph.builder import build_graph
from app.graph.nodes import rewriteNode

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="AI Content Agent",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------ STYLING ------------------
st.markdown("""
<style>
body {
    font-family: 'Inter', sans-serif;
}
.stTextArea textarea {
    font-size: 18px;
    line-height: 1.7;
}
.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "result" not in st.session_state:
    st.session_state.result = None

if "blog" not in st.session_state:
    st.session_state.blog = ""

# ------------------ HEADER ------------------
st.title("🚀 Autonomous Content Marketing Agent")
st.caption("Create, optimize, and publish content with AI")

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.header("⚙️ Controls")

    topic = st.text_input("Topic")

    generate = st.button("🚀 Generate Blog", use_container_width=True)

    preview_mode = st.toggle("👁 Preview Mode")

    st.divider()

    st.markdown("### 📅 Scheduling")
    schedule = st.button("📅 Schedule Post", use_container_width=True)

# ------------------ GENERATE ------------------
if generate:
    if not topic:
        st.warning("Enter a topic")
    else:
        with st.spinner("Generating..."):
            graph = build_graph()
            result = graph.invoke({"topic": topic})

        st.session_state.result = result
        st.session_state.blog = result["blog"]

# ------------------ MAIN UI ------------------
if st.session_state.result:

    result = st.session_state.result

    col_editor, col_side = st.columns([3, 1])

    # ------------------ EDITOR ------------------
    with col_editor:
        st.subheader("✍️ Editor")

        edited_blog = st.text_area(
            "",
            value=st.session_state.blog,
            height=600,
            placeholder="Start writing your masterpiece..."
        )

        # autosave feel
        st.session_state.blog = edited_blog

        if preview_mode:
            st.markdown("### 🌐 Preview")
            st.markdown(edited_blog)

    # ------------------ SIDE PANEL ------------------
    with col_side:

        # -------- INSIGHTS --------
        st.subheader("📊 Insights")

        st.metric("SEO Score", result.get("seo_score", "N/A"))

        st.markdown("#### 🤖 AI Feedback")
        st.write(result.get("evaluation", "No feedback"))

        st.divider()

        # -------- FEEDBACK --------
        st.subheader("🧠 Improve")

        quality = st.text_area("Content Quality")
        tone = st.text_area("Tone / Branding")
        seo = st.text_area("SEO Improvements")
        engagement = st.text_area("Engagement")

        st.divider()

        # -------- ACTIONS --------
        st.subheader("⚡ Actions")

        approve = st.button("✅ Approve", use_container_width=True)
        rewrite = st.button("🔄 Rewrite", use_container_width=True)
        save_edit = st.button("💾 Save Edit", use_container_width=True)

        # -------- ACTION HANDLING --------

        if approve:
            st.success("✅ Approved! Ready to publish.")

        if save_edit:
            st.session_state.result["blog"] = st.session_state.blog
            st.success("💾 Saved!")

        if rewrite:
            feedback = f"""
            Content Issues: {quality}
            SEO Issues: {seo}
            Tone Issues: {tone}
            Engagement Issues: {engagement}
            """

            new_state = {
                "topic": topic,
                "blog": st.session_state.blog,
                "retrieved_docs": result.get("retrieved_docs", []),
                "ai_feedback": result.get("evaluation", ""),
                "human_feedback": feedback
            }

            with st.spinner("Improving content..."):
                updated = rewriteNode(new_state)

            st.session_state.blog = updated["blog"]
            st.session_state.result["blog"] = updated["blog"]

            st.success("🚀 Content Improved!")
            st.rerun()

        st.divider()

        # -------- SOCIAL OUTPUT --------
        if result.get("linkedin_post"):
            st.subheader("💼 LinkedIn")
            st.write(result["linkedin_post"])

        if result.get("twitter_thread"):
            st.subheader("🐦 Twitter")
            st.write(result["twitter_thread"])

        # -------- SCHEDULER --------
        if schedule:
            st.success("📅 Post scheduled (demo)")