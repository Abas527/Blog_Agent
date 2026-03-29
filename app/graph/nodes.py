

import logging
from app.graph.state import State
from app.llm.model_router import route_model
from app.rag.user_data import USER_DOCUMENT
from app.memory.memory import store_interaction, get_relevant_memory

logger = logging.getLogger(__name__)


def trend_node(state: State) -> dict:
    topic = state["topic"]
    angles = [
        f"Explain {topic} to a complete beginner",
        f"How {topic} works under the hood",
        f"Real-world systems that use {topic}",
        f"Common {topic} interview questions",
        f"Mistakes developers make with {topic}",
        f"How {topic} connects to system design",
        f"{topic} vs alternatives — when to use each",
    ]
    return {"trending": angles}



def rag_node(state: State) -> dict:
    topic = state["topic"]
    relevant_docs = [
        doc for doc in USER_DOCUMENT if topic.lower() in doc.lower()
    ]
    if not relevant_docs:
        logger.warning(
            f"rag_node: No documents found for topic='{topic}'. "
            "Writer will run without grounding context. "
            "Consider adding docs or upgrading to semantic search."
        )
    return {"retrieved_docs": relevant_docs}



def writer_node(state: State) -> dict:
    topic = state["topic"]
    angles = ", ".join(state.get("trending", []))
    context = "\n\n".join(state.get("retrieved_docs", []))
    memory_context = get_relevant_memory(topic)

    context_section = (
        f"REFERENCE DOCS:\n{context}\n"
        if context
        else "REFERENCE DOCS: None available — write from your knowledge.\n"
    )

    prompt = f"""You are a world-class educator, writer, and content creator.
Your niche: AI, DSA, and System Design — taught simply to developers at all levels.

GOAL:
Write a long-form blog post explaining {topic} in a way that:
- A beginner can understand it
- An expert finds it impressive and shareable
- A developer can immediately apply it

RULES:
1. Hook first: Start with a scroll-stopping, curiosity-inducing sentence.
2. Analogy: Use a simple real-world analogy for the core concept.
3. Clarity: Short sentences. No jargon without explanation.
4. Structure:
   - Introduce the problem this concept solves
   - Explain the concept conceptually with the analogy
   - Show a concrete code example (Python preferred)
   - Key takeaway in 2-3 sentences
5. Engagement: Rhetorical questions, subtle humor, relatable examples.
6. Tone: Expert mentor — not a textbook. Conversational but authoritative.
7. No markdown symbols (**, -, #). Plain text only.
8. Length: 1000-2000 words.

CONTENT ANGLES TO WEAVE IN:
{angles}

{context_section}
PREVIOUS KNOWLEDGE CONTEXT:
{memory_context or "None"}

OUTPUT:
TITLE:<title>

BLOG:<blog>
SEO_KEYWORDS:<keywords>
"""

    blog = route_model("blog", prompt)
    return {"blog": blog}


def evaluator_node(state: State) -> dict:
    blog = state["blog"]

    prompt = f"""You are an expert educator and content reviewer for AI, DSA, and System Design content.

Evaluate this blog post on three dimensions:

1. CLARITY — Is the explanation easy to understand for a beginner?
2. SIMPLICITY — Are complex concepts broken down well with analogies?
3. ENGAGEMENT — Is it interesting and shareable for a developer audience?
4. SEO — Does it have good SEO keywords?

BLOG:
{blog}

Return your evaluation EXACTLY in this format (no extra text):

CLARITY SCORE: <0-100>
SIMPLICITY SCORE: <0-100>
ENGAGEMENT SCORE: <0-100>
Feedback: <3-5 specific, actionable improvements the writer should make>
SEO SCORE: <0-100>
"""

    raw_feedback = route_model("fast", prompt)

    try:
        clarity = int(raw_feedback.split("CLARITY SCORE:")[1].split("\n")[0].strip())
        simplicity = int(raw_feedback.split("SIMPLICITY SCORE:")[1].split("\n")[0].strip())
        engagement = int(raw_feedback.split("ENGAGEMENT SCORE:")[1].split("\n")[0].strip())
        seo_score = int(raw_feedback.split("SEO SCORE:")[1].split("\n")[0].strip())

        score = (clarity + simplicity + engagement+ seo_score) // 3
        logger.info(f"evaluator_node: clarity={clarity} simplicity={simplicity} engagement={engagement} avg={score}")
    except (IndexError, ValueError) as e:
        logger.error(f"evaluator_node: Failed to parse scores — {e} | raw: {raw_feedback[:300]}")
        score = 50

    return {"evaluation": raw_feedback, "seo_score": score}


def rewrite_node(state: State) -> dict:
    blog = state["blog"]
    evaluation = state.get("evaluation", "")
    human_feedback = state.get("human_feedback", "")
    context = "\n\n".join(state.get("retrieved_docs", []))
    rewrite_count = state.get("rewrite_count", 0) + 1

    context_section = f"REFERENCE DOCS:\n{context}\n" if context else ""

    prompt = f"""You are an expert teacher and editor for AI, DSA, and System Design content.

Improve the blog using ALL feedback below. Human feedback has highest priority.

HUMAN FEEDBACK (highest priority):
{human_feedback or "None provided"}

EXPERT EVALUATION FEEDBACK:
{evaluation}

{context_section}
CURRENT BLOG:
{blog}

INSTRUCTIONS:
- Make explanations simpler and clearer
- Add or improve the real-world analogy
- Break up any long paragraphs (max 3 sentences each)
- Improve logical flow — each paragraph should lead to the next
- Keep it engaging for developers of all levels
- Fix any specific issues mentioned in the feedback above
- No markdown symbols. Plain text only.

OUTPUT:
TITLE:<title>
BLOG:<blog>
SEO_KEYWORDS:<keywords>
"""

    improved_blog = route_model("blog", prompt)
    return {"blog": improved_blog, "rewrite_count": rewrite_count}


def human_node(state: State) -> dict:
    print("\n" + "=" * 70)
    print("BLOG FOR REVIEW:")
    print("=" * 70)
    print(state["blog"])
    print("=" * 70 + "\n")

    while True:
        decision = input("Approve (a), Edit (e), Reject (r): ").strip().lower()

        if decision == "a":
            logger.info("human_node: Blog approved.")
            return {"approved": True, "human_feedback": ""}

        elif decision == "e":
            edited = input("\nEnter your edited blog:\n").strip()  # FIX: no .lower()
            if not edited:
                print("No edits entered — keeping original.")
                edited = state["blog"]
            logger.info("human_node: Blog edited and approved.")
            return {"blog": edited, "approved": True, "human_feedback": ""}

        elif decision == "r":
            feedback = input("\nWhat should be improved?\n").strip()
            logger.info(f"human_node: Blog rejected. Feedback: {feedback}")
            return {
                "approved": False,
                "human_feedback": feedback or "No specific feedback provided.",
            }

        else:
            print("Invalid input. Please enter 'a' to approve, 'e' to edit, or 'r' to reject.")



def approve_router(state: State) -> str:
    if state.get("approved"):
        logger.info(f"approve_router: Approved → carousel. Final score={state.get('seo_score')}")
        return "end"
    else:
        logger.info("approve_router: Rejected → rewrite.")
        return "rewrite"


def evaluation_router(state: State) -> str:
    score = state.get("seo_score", 0)
    retries = state.get("rewrite_count", 0)

    if score >= 75 or retries >= 3:
        logger.info(f"evaluation_router: score={score} retries={retries} → human")
        return "human"
    else:
        logger.info(f"evaluation_router: score={score} retries={retries} → rewrite")
        return "rewrite"


def social_node(state: State) -> dict:
    blog = state["blog"]
    topic = state.get("topic", "")

    prompt = f"""You are a content creator who teaches AI, DSA, and System Design to developers.

Convert this blog into two social media formats.

BLOG:
{blog}

OUTPUT FORMAT — return EXACTLY this structure:

LINKEDIN:
<LinkedIn post here — strong hook, one key insight, short readable lines, no markdown>

TWITTER:
1. <tweet 1>
2. <tweet 2>
3. <tweet 3>
4. <tweet 4>
5. <tweet 5>

RULES:
- No markdown (**, -, #)
- Plain text only
- LinkedIn: 150-200 words, professional but human
- Twitter: each tweet max 280 chars, teach one idea per tweet
"""

    result = route_model("fast", prompt)

    try:
        linkedin = result.split("LINKEDIN:")[1].split("TWITTER:")[0].strip()
        twitter = result.split("TWITTER:")[1].strip()
    except (IndexError, AttributeError) as e:
        logger.error(f"social_node: Failed to parse output — {e}")
        linkedin = result
        twitter = result

    return {"linkedin_post": linkedin, "thread_post": twitter}