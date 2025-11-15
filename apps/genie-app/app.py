import streamlit as st
from databricks.sdk import WorkspaceClient
import pandas as pd
import os

w = WorkspaceClient()

SPACE_ID = os.getenv("SPACE_ID")
genie_space_id = SPACE_ID


def display_message(message):
    if "content" in message:
        st.markdown(message["content"])
    if "data" in message:
        st.dataframe(message["data"])
    if "code" in message:
        with st.expander("Show generated code"):
            st.code(message["code"], language="sql", wrap_lines=True)


def get_query_result(statement_id):
    # For simplicity, let's say data fits in one chunk, query.manifest.total_chunk_count = 1

    result = w.statement_execution.get_statement(statement_id)
    return pd.DataFrame(
        result.result.data_array, columns=[i.name for i in result.manifest.schema.columns]
    )


def process_genie_response(response):
    for i in response.attachments:
        if i.text:
            message = {"role": "assistant", "content": i.text.content}
            display_message(message)
        elif i.query:
            data = get_query_result(response.query_result.statement_id)
            message = {
                "role": "assistant", "content": i.query.description, "data": data, "code": i.query.query
            }
            display_message(message)


if prompt := st.chat_input("Ask your question..."):
    # Refer to actual app code for chat history persistence on rerun

    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.get("conversation_id"):
            conversation = w.genie.create_message_and_wait(
                genie_space_id, st.session_state.conversation_id, prompt
            )
            process_genie_response(conversation)
        else:
            conversation = w.genie.start_conversation_and_wait(genie_space_id, prompt)
            process_genie_response(conversation)