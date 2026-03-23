# main.py

import sys
import os
import re # For command parsing

# Adjust path to import core and agents modules
# This is a good practice for larger projects
sys.path.append(os.path.dirname(__file__))

from agents.task_manager_graph import build_task_manager_graph
from core.config import LLM_MODEL 
from core.vector_store import get_vector_store, retrieve_tasks_from_store # Uses the utility functions

# --- Helper Functions ---

def display_help():
    """Displays available commands and usage."""
    print("\n--- Task Manager Commands ---")
    print("  **ADD <task description>** : Adds a new task to the queue.")
    print("    Example: ADD Review database schema updates.")
    print("  **FIND <query>** : Searches for relevant tasks.")
    print("    Example: FIND research tasks for the Q4 project.")
    print("  **HELP** : Displays this help message.")
    print("  **EXIT/QUIT** : Shuts down the agent.")
    print("-----------------------------")

def parse_command(user_input: str):
    """Parses user input into an action and argument."""
    input_upper = user_input.strip().upper()
    
    if input_upper in ['EXIT', 'QUIT', 'HELP']:
        return input_upper, None
    
    # Regex to split the first word (command) from the rest (argument)
    match = re.match(r"(\w+)\s+(.*)", user_input.strip(), re.IGNORECASE)
    if match:
        command = match.group(1).upper()
        argument = match.group(2).strip()
        if command in ['ADD', 'FIND']:
            return command, argument
    
    return "UNKNOWN", user_input

# --- Main Agent Logic ---

def main():
    """
    Main function to run the AI Task Manager Agent.
    """
    print("--- AI-Based Task Manager Agent Initialization ---")
    print(f"Using Ollama Model: **{LLM_MODEL}**")
    
    # 1. Initialization: Build graph and check vector store
    try:
        vectorstore = get_vector_store()
        app = build_task_manager_graph()
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: Initialization failed.")
        print("Please ensure:")
        print("  1. Ollama is running.")
        print("  2. Models (llama3:8b, nomic-embed-text) are pulled.")
        print(f"Details: {e}")
        return 

    display_help()
    
    # 2. Interaction Loop
    while True:
        user_input = input("\nTask Manager > ")
        command, argument = parse_command(user_input)
        
        if command in ['EXIT', 'QUIT']:
            print("Exiting Task Manager Agent. Goodbye!")
            break
        
        if command == 'HELP':
            display_help()
            continue

        if not argument and command in ['ADD', 'FIND']:
            print(f"🚫 Error: The **{command}** command requires an argument.")
            continue
            
        print(f"\nProcessing command: **{command}**...")

        try:
            if command == 'ADD':
                # Dispatch to LangGraph for categorization & storage
                final_state = app.invoke({"input_task_str": argument})

                print("\n✅ Task Successfully Processed and Stored!")
                
                # Display results
                cat_task = final_state.get("categorized_task", {})
                print("--- New Task Summary ---")
                print(f"ID:       {final_state['task_id']}")
                print(f"Summary:  **{cat_task.get('summary', 'N/A')}**")
                print(f"Category: {cat_task.get('category', 'N/A')}")
                print(f"Priority: {cat_task.get('priority', 'N/A')}")
                print("------------------------")

            elif command == 'FIND':
                # Dispatch to Vector Store for Retrieval
                results = retrieve_tasks_from_store(vectorstore, argument)
                
                if results:
                    print(f"\n🔍 Found {len(results)} relevant tasks for query: '{argument}'")
                    for i, task in enumerate(results):
                        print(f"--- Result {i+1} (Priority: {task['priority']}) ---")
                        print(f"ID:       {task['task_id']}")
                        print(f"Category: {task['category']}")
                        print(f"Summary:  {task['summary']}")
                    print("-------------------------------------------------")
                else:
                    print(f"No tasks found matching '{argument}'.")

            elif command == 'UNKNOWN':
                print("❌ Invalid command or format. Type **HELP** for available commands.")

        except Exception as e:
            print(f"\n❌ An error occurred during the **{command}** operation: {e}")
            print("This often indicates a transient Ollama connection issue. Try the command again.")


if __name__ == "__main__":
    main()