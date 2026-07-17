"""
memory.py

Handles conversation memory for the Personal Chef Agent.
"""

from langgraph.checkpoint.memory import InMemorySaver

# Create the memory object
memory = InMemorySaver()


def get_config(thread_id: str = "default_user"):
    """
    Returns the LangGraph configuration containing
    the conversation thread ID.

    Parameters
    ----------
    thread_id : str
        Unique identifier for each user's conversation.

    Returns
    -------
    dict
    """

    return {
        "configurable": {
            "thread_id": thread_id
        }
    }