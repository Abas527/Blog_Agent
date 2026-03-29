from langgraph.graph import StateGraph,END

from app.graph.state import State
from app.graph.nodes import writer_node,trend_node,rag_node,approve_router,human_node,rewrite_node,evaluation_router,evaluator_node,social_node


def build_graph():

    graph = StateGraph(State)
    graph.add_node("writer", writer_node)
    graph.add_node("trend",trend_node)
    graph.add_node("rag",rag_node)
    graph.add_node("human",human_node)
    graph.add_node("rewrite",rewrite_node)
    graph.add_node("evaluator",evaluator_node)
    graph.add_node("social",social_node)


    graph.set_entry_point("trend")
    graph.add_edge("trend","rag")
    graph.add_edge("rag","writer")
    graph.add_edge("writer","evaluator")

    graph.add_conditional_edges(
        "evaluator",evaluation_router,{
            "human":"human",
            "rewrite":"rewrite"
        }
    )
    graph.add_edge("rewrite","evaluator")
    
    graph.add_conditional_edges(
        "human",approve_router,{
            "end":"social",
            "rewrite":"rewrite"
        }
    )
    graph.add_edge("social",END)

    return graph.compile()

