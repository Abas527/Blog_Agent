---

# Blog_Agent

An autonomous multi‑agent workflow for AI‑powered blog generation, evaluation, rewriting, and social media publishing.  
This project uses LangGraph, Groq LLMs, and Streamlit to simulate a writer’s workflow: from topic ideation → draft writing → evaluation → rewrite → human approval → social media post generation.

---

## Features
- Dual Interfaces: Run via CLI or Streamlit UI.
- Workflow Automation: Trend analysis, retrieval‑augmented generation (RAG), drafting, evaluation, rewriting, approval, and social post creation.
- LLM Integration: Uses Groq‑backed models for fast evaluation and structured blog generation.
- Memory Persistence: Stores past posts and feedback in JSON for contextual reuse.
- Social Media Output: Generates LinkedIn posts and Twitter‑style threads from blogs.

---

## Project Structure
```
Blog_Agent/
│── app/                  # Core application code
│   ├── graph/            # Workflow graph and nodes
│   ├── memory.py         # Local JSON persistence
│   ├── config/settings.py# Environment + model configs
│   ├── ui.py             # Streamlit frontend
│   └── main.py           # CLI entrypoint
│── requirements.txt      # Dependencies
│── graph.png             # Architecture diagram
│── README.md             # Documentation
│── LICENSE               # MIT License
```

---

## System Architecture
The workflow is built as a LangGraph state machine:

1. Trend Node → Generates topic‑specific angles.  
2. RAG Node → Retrieves grounding docs from `USER_DOCUMENT`.  
3. Writer Node → Drafts blog using Groq LLM.  
4. Evaluator Node → Scores clarity, simplicity, engagement, SEO.  
5. Evaluation Router → Decides rewrite vs human review.  
6. Rewrite Node → Improves blog using evaluation + feedback.  
7. Human Node → CLI approval/edit loop.  
8. Approve Router → Routes approved blogs to social stage.  
9. Social Node → Generates LinkedIn + Twitter thread posts.  
10. Memory Layer → Stores posts + feedback for reuse.

---

## Setup

### 1. Clone the repo
```
git clone https://github.com/Abas527/Blog_Agent.git
cd Blog_Agent
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file:
```
GROQ_API_KEY=your_api_key_here
DEFAULT_MODEL=llama3-70b
FAST_MODEL=llama3-8b
```

---

## Usage

### CLI Mode
```
python app/main.py
```
- Prompts for a topic.
- Runs workflow end‑to‑end.
- Stores results in `memory.json`.

### Streamlit UI
```
streamlit run app/ui.py
```
- Enter topic in sidebar.
- Click “Generate Blog”.
- View blog, evaluation, SEO score, rewrite options, and social posts.

---

## Workflow State Keys
| Key             | Produced By       | Consumed By         |
|-----------------|------------------|---------------------|
| topic           | UI/CLI input     | trend, rag, writer  |
| trending        | trend_node       | writer_node         |
| retrieved_docs  | rag_node         | writer, rewrite     |
| blog            | writer/rewrite   | evaluator, social   |
| evaluation      | evaluator_node   | rewrite_node        |
| seo_score       | evaluator_node   | routers             |
| approved        | human_node       | approve_router      |
| human_feedback  | human_node       | rewrite_node        |
| rewrite_count   | rewrite_node     | evaluation_router   |
| linkedin_post   | social_node      | persistence/UI      |
| thread_post     | social_node      | persistence/UI      |

---

## License
MIT License © 2026 Abas527

---