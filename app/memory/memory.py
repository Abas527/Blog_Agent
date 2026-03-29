import json
import os
import re
from app.graph.state import State

MEMORY_FILE = "app/memory/memory.json"
def clean_text(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # remove **
    text = re.sub(r"\*(.*?)\*", r"\1", text)      # remove *
    text = re.sub(r"- ", "", text)               # remove bullets
    return text.strip()

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"posts": [], "feedback": []}
    
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)
def store_interaction(state:State):
    memory = load_memory()
    memory["posts"].append({
        "topic": clean_text(state["topic"]),
        "blog": clean_text(state["blog"]),
        "linkedin_post": clean_text(state["linkedin_post"]),
        "thread_post": clean_text(state["thread_post"]),
    })
    memory["feedback"].append({
        "topic": clean_text(state["topic"]),
        "human_feedback":state["human_feedback"],
        "ai_feedback":clean_text(state["evaluation"])
    })
    save_memory(memory)


def get_relevant_memory(topic):
    memory=load_memory()

    past_posts=memory["posts"][-2:]

    context="\n\n".join([f"Topic: {post['topic']}\n content: {post['blog'][:100]}" for post in past_posts])

    return context

def display_memory():
    memory = load_memory()
    for post in memory["posts"][-1:]:
        print(f"Topic: {post['topic']}\nBlog: {post['blog']}\nLinkedIn Post: {post['linkedin_post']}\nThread Post: {post['thread_post']}\n{'-'*40}")