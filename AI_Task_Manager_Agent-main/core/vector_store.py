from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

import os, json, shutil

from core.config import EMBEDDING_MODEL, FAISS_INDEX_PATH, OLLAMA_BASE_URL
from core.models import Task


def get_vector_store():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)

    if os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.faiss")):
        return FAISS.load_local(
            FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )

    dummy = Document(page_content=json.dumps({"task_id": "0"}))
    store = FAISS.from_documents([dummy], embeddings)
    store.save_local(FAISS_INDEX_PATH)
    return store


def add_task_to_store(store, task: Task):
    doc = Document(page_content=json.dumps(task.model_dump()))
    store.add_documents([doc])
    store.save_local(FAISS_INDEX_PATH)


def retrieve_tasks_from_store(store, query, k=5):
    docs = store.similarity_search(query, k=k)
    results = []

    for d in docs:
        try:
            t = json.loads(d.page_content)
            if t.get("task_id") != "0":
                results.append(t)
        except:
            pass

    return results


# -------- FULL CRUD --------


def get_all_tasks(store):
    return retrieve_tasks_from_store(store, "", k=100)


def rebuild_index(tasks):
    if os.path.exists(FAISS_INDEX_PATH):
        shutil.rmtree(FAISS_INDEX_PATH)

    store = get_vector_store()

    for t in tasks:
        add_task_to_store(store, Task(**t))


def update_task_status(store, task_id, status):
    tasks = get_all_tasks(store)

    for t in tasks:
        if t["task_id"] == task_id:
            t["status"] = status

    rebuild_index(tasks)
    return True


def delete_task(store, task_id):
    tasks = get_all_tasks(store)
    tasks = [t for t in tasks if t["task_id"] != task_id]

    rebuild_index(tasks)
    return True
