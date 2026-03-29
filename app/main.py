from app.graph.builder import build_graph
import re
from app.memory.memory import store_interaction,display_memory



def run():
    graph = build_graph()

    user_input=input("Enter a topic: ")

    result = graph.invoke({
        "topic": user_input
    })

    #store each interaction
    store_interaction(result)

    display_memory()

if __name__ == "__main__":
    run()