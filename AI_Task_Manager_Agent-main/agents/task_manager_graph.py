from typing import TypedDict
import uuid, time

from langgraph.graph import StateGraph, END

from core.models import Task
from core.vector_store import get_vector_store, add_task_to_store
from agents.task_categorizer import categorize_and_prioritize


class AgentState(TypedDict):
    input_task_str: str
    categorized_task: dict
    task_id: str


def validate_node(state: AgentState):
    if len(state["input_task_str"]) < 5:
        raise ValueError("Invalid task input")
    return state


def categorize_node(state: AgentState):
    result = categorize_and_prioritize(state["input_task_str"])

    return {
        "input_task_str": state["input_task_str"],
        "categorized_task": result.model_dump(),
        "task_id": str(uuid.uuid4()),
    }


def store_node(state: AgentState):
    cat = state["categorized_task"]

    task = Task(
        task_id=state["task_id"],
        original_input=state["input_task_str"],
        category=cat["category"],
        priority=cat["priority"],
        summary=cat["summary"],
        tags=cat.get("tags", []),
        estimated_duration=cat.get("estimated_duration"),
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
    )

    store = get_vector_store()
    add_task_to_store(store, task)

    return state


def build_task_manager_graph():
    g = StateGraph(AgentState)

    g.add_node("validate", validate_node)
    g.add_node("categorize", categorize_node)
    g.add_node("store", store_node)

    g.set_entry_point("validate")

    g.add_edge("validate", "categorize")
    g.add_edge("categorize", "store")
    g.add_edge("store", END)

    return g.compile()
