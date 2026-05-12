"""Genie AI assistant integration for Streamlit."""

import os
from typing import Dict, Any, Optional
from databricks.sdk import WorkspaceClient


def ask_genie(question: str, store_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Send a question to Genie and get a response.

    Args:
        question: The question to ask Genie
        store_id: Optional store ID to add context

    Returns:
        Dict with 'answer', 'sql', and 'conversation_id' keys
    """
    space_id = os.getenv("GENIE_SPACE_ID")

    if not space_id:
        return {
            "answer": "Genie Space not configured. Set GENIE_SPACE_ID environment variable.",
            "sql": None,
            "conversation_id": None
        }

    try:
        client = WorkspaceClient()

        # Add store context to the question if store_id provided
        if store_id:
            question = f"For store ID {store_id}: {question}"

        # Start a conversation
        response = client.genie.start_conversation_and_wait(
            space_id=space_id,
            content=question
        )

        # Extract the response
        answer = ""
        sql = None
        conversation_id = None

        if response:
            # Get conversation_id from response
            conversation_id = getattr(response, 'conversation_id', None)

            # Extract attachments directly from response
            attachments = getattr(response, 'attachments', None)

            if attachments:
                for attachment in attachments:
                    # Extract text response
                    if hasattr(attachment, "text") and attachment.text:
                        text_obj = attachment.text
                        answer = getattr(text_obj, 'content', None) or str(text_obj)
                    # Extract SQL query
                    if hasattr(attachment, "query") and attachment.query:
                        query_obj = attachment.query
                        sql = getattr(query_obj, 'query', None) or getattr(query_obj, 'body', None)

            # Fallback: try common response attributes if no attachments found
            if not answer:
                for attr in ['result', 'content', 'text', 'message', 'answer']:
                    val = getattr(response, attr, None)
                    if val:
                        answer = str(val)
                        break

        return {
            "answer": answer or "I couldn't generate a response. Please try rephrasing your question.",
            "sql": sql,
            "conversation_id": conversation_id
        }

    except Exception as e:
        return {
            "answer": f"I encountered an error: {str(e)}. Please try again.",
            "sql": None,
            "conversation_id": None
        }


def get_sample_questions() -> Dict[str, list]:
    """Get sample questions organized by category."""
    return {
        "Sales": [
            "What were my sales yesterday?",
            "How am I tracking against budget this week?",
            "Which categories have the highest sales this month?",
            "Show me my YoY growth trend"
        ],
        "Products": [
            "Show me my top 10 selling articles by APSD",
            "Which products have declining sales vs last year?",
            "What are my highest margin products?"
        ],
        "Inventory": [
            "What items should I reorder today?",
            "Show me my projected out-of-stock items",
            "List dead stock in Hot Food ranked by cost"
        ],
        "Write-offs": [
            "What were my write-offs yesterday?",
            "Am I writing off more than other stores in my cluster?",
            "Show me write-off anomalies this week"
        ],
        "Food Service": [
            "How many meat pies should I cook at noon tomorrow?",
            "What's my recommended cook quantity for lunch peak?",
            "Show me hourly sales patterns for Hot Food"
        ]
    }
