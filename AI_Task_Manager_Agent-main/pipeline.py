from agents.task_manager_graph import build_task_manager_graph

app = build_task_manager_graph()


def run_pipeline(task_input: str):
    try:
        result = app.invoke({"input_task_str": task_input})

        return {
            "stored": True,
            "task_id": result["task_id"],
            "categorized_task": result["categorized_task"],
            "validation_message": "Passed",
        }

    except Exception as e:
        return {"stored": False, "error": str(e)}
