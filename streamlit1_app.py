import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from api_client import ask_shopit_api
#from monitoring import run_shopit_query


st.set_page_config(
    page_title="Shopit AI",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Shopit AI")

st.subheader(
    "E-commerce Analytics Assistant"
)

st.write(
    "Ask questions about Shopit's sales, customers, "
    "products, orders, and company policies."
)


# ============================================================
# SESSION STATE
# ============================================================

# This stores the complete conversation.
#
# IMPORTANT:
# We are storing not only text, but also:
# - insights
# - SQL
# - data
# - chart information
#
# This allows previous visualizations to remain visible
# after Streamlit reruns.
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# CLEAR CHAT BUTTON
# ============================================================

with st.sidebar:

    st.header("Shopit AI")

    st.write(
        "Conversation Controls"
    )

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# FUNCTION: CREATE CHART
# ============================================================

def render_chart(message):

    """
    Reconstruct and display a previously generated chart.

    The chart data comes from the original SQL DataFrame,
    not from the LLM.
    """

    # --------------------------------------------------------
    # Check whether visualization is required
    # --------------------------------------------------------

    if not message.get(
        "visualization_required",
        False
    ):

        return


    # --------------------------------------------------------
    # Get chart configuration
    # --------------------------------------------------------

    chart_type = message.get(
        "chart_type"
    )

    x_column = message.get(
        "x_column"
    )

    y_column = message.get(
        "y_column"
    )

    chart_title = message.get(
        "chart_title"
    )

    chart_data = message.get(
        "chart_data",
        []
    )


    # --------------------------------------------------------
    # Validate chart data
    # --------------------------------------------------------

    if not chart_data:

        return


    # --------------------------------------------------------
    # Recreate DataFrame
    # --------------------------------------------------------

    try:

        df = pd.DataFrame(
            chart_data
        )

    except Exception:

        return


    # --------------------------------------------------------
    # Validate columns
    # --------------------------------------------------------

    if (
        x_column is None
        or y_column is None
    ):

        return


    if (
        x_column not in df.columns
        or y_column not in df.columns
    ):

        return


    # ========================================================
    # DISPLAY CHART
    # ========================================================

    st.markdown(
        "### 📊 Visualization"
    )


    fig, ax = plt.subplots(
        figsize=(10, 5)
    )


    # ========================================================
    # BAR CHART
    # ========================================================

    if chart_type == "bar":

        ax.bar(
            df[x_column].astype(str),
            df[y_column]
        )

        ax.set_xlabel(
            x_column
        )

        ax.set_ylabel(
            y_column
        )

        ax.tick_params(
            axis="x",
            rotation=45
        )


    # ========================================================
    # LINE CHART
    # ========================================================

    elif chart_type == "line":

        ax.plot(
            df[x_column].astype(str),
            df[y_column],
            marker="o"
        )

        ax.set_xlabel(
            x_column
        )

        ax.set_ylabel(
            y_column
        )

        ax.tick_params(
            axis="x",
            rotation=45
        )


    # ========================================================
    # SCATTER PLOT
    # ========================================================

    elif chart_type == "scatter":

        ax.scatter(
            df[x_column],
            df[y_column]
        )

        ax.set_xlabel(
            x_column
        )

        ax.set_ylabel(
            y_column
        )


    # ========================================================
    # PIE CHART
    # ========================================================

    elif chart_type == "pie":

        ax.pie(
            df[y_column],
            labels=df[x_column].astype(str),
            autopct="%1.1f%%"
        )


    # ========================================================
    # UNKNOWN CHART TYPE
    # ========================================================

    else:

        plt.close(fig)

        return


    # ========================================================
    # TITLE
    # ========================================================

    if chart_title:

        ax.set_title(
            chart_title
        )


    # ========================================================
    # DISPLAY
    # ========================================================

    fig.tight_layout()

    st.pyplot(
        fig
    )

    plt.close(fig)


# ============================================================
# FUNCTION: RENDER ASSISTANT MESSAGE
# ============================================================

def render_assistant_message(message):

    """
    Render a previously stored assistant response.

    This function is important because Streamlit reruns
    the entire application every time the user asks a
    new question.

    We reconstruct the old answer + insights + chart
    from session_state.
    """

    # ========================================================
    # ANSWER
    # ========================================================

    answer = message.get(
        "content",
        ""
    )


    if answer:

        st.markdown(
            "### Answer"
        )

        st.write(
            answer
        )


    # ========================================================
    # INSIGHTS
    # ========================================================

    insights = message.get(
        "insights",
        []
    )


    if insights:

        st.markdown(
            "### Insights"
        )

        for insight in insights:

            st.write(
                f"• {insight}"
            )


    # ========================================================
    # SQL QUERY
    # ========================================================

    sql = message.get(
        "sql"
    )


    if sql:

        with st.expander(
            "View SQL Query"
        ):

            st.code(
                sql,
                language="sql"
            )


    # ========================================================
    # DATA
    # ========================================================

    data_records = message.get(
        "data_records",
        []
    )


    if data_records:

        with st.expander(
            "View Data"
        ):

            try:

                old_df = pd.DataFrame(
                    data_records
                )

                st.dataframe(
                    old_df,
                    use_container_width=True
                )

            except Exception:

                pass


    # ========================================================
    # VISUALIZATION
    # ========================================================

    render_chart(
        message
    )


# ============================================================
# DISPLAY PREVIOUS CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    if message["role"] == "user":

        with st.chat_message(
            "user"
        ):

            st.markdown(
                message["content"]
            )


    # --------------------------------------------------------
    # ASSISTANT MESSAGE
    # --------------------------------------------------------

    elif message["role"] == "assistant":

        with st.chat_message(
            "assistant"
        ):

            render_assistant_message(
                message
            )


# ============================================================
# USER INPUT
# ============================================================

question = st.chat_input(
    "Ask Shopit AI something..."
)


# ============================================================
# PROCESS NEW QUESTION
# ============================================================

if question:

    # ========================================================
    # SAVE USER QUESTION
    # ========================================================

    user_message = {

        "role": "user",

        "content": question
    }


    st.session_state.messages.append(
        user_message
    )


    # ========================================================
    # DISPLAY USER QUESTION
    # ========================================================

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    # ========================================================
    # ASSISTANT RESPONSE
    # ========================================================

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Analyzing your question..."
        ):

            try:

                # ====================================================
                # SEND QUESTION TO LANGGRAPH
                # ====================================================
                #result = run_shopit_query(question)
                result = ask_shopit_api(question)

                # ====================================================
                # GET ANSWER
                # ====================================================

                answer = result.get(
                    "answer",
                    "I could not generate an answer."
                )


                # ====================================================
                # GET INSIGHTS
                # ====================================================

                insights = result.get(
                    "insights",
                    []
                )


                # ====================================================
                # GET SQL
                # ====================================================

                sql = result.get(
                    "sql"
                )


                # ====================================================
                # GET DATAFRAME
                # ====================================================

                df = result.get(
                    "data"
                )


                # ====================================================
                # GET VISUALIZATION INFORMATION
                # ====================================================

                visualization_required = result.get(
                    "visualization_required",
                    False
                )


                chart_type = result.get(
                    "chart_type"
                )


                x_column = result.get(
                    "x_column"
                )


                y_column = result.get(
                    "y_column"
                )


                chart_title = result.get(
                    "chart_title"
                )


                # ====================================================
                # CONVERT REAL DATAFRAME TO RECORDS
                # ====================================================
                #
                # IMPORTANT:
                #
                # We DO NOT ask Gemini to generate chart_data.
                #
                # We take the actual SQL result DataFrame and
                # store it.
                #
                # ====================================================

                if (
                    df is not None
                    and isinstance(df, pd.DataFrame)
                    and not df.empty
                ):

                    data_records = (
                        df.to_dict(
                            orient="records"
                        )
                    )

                else:

                    data_records = []


                # ====================================================
                # BUILD CURRENT MESSAGE
                # ====================================================

                assistant_message = {

                    "role":
                        "assistant",

                    "content":
                        answer,

                    "insights":
                        insights,

                    "sql":
                        sql,

                    # -----------------------------------------------
                    # Store actual SQL result
                    # -----------------------------------------------

                    "data_records":
                        data_records,

                    # -----------------------------------------------
                    # Visualization metadata
                    # -----------------------------------------------

                    "visualization_required":
                        visualization_required,

                    "chart_type":
                        chart_type,

                    "x_column":
                        x_column,

                    "y_column":
                        y_column,

                    "chart_title":
                        chart_title,

                    # -----------------------------------------------
                    # Chart uses REAL DataFrame data
                    # -----------------------------------------------

                    "chart_data":
                        data_records
                }


                # ====================================================
                # DISPLAY CURRENT ANSWER
                # ====================================================

                render_assistant_message(
                    assistant_message
                )


                # ====================================================
                # SAVE COMPLETE ASSISTANT RESPONSE
                # ====================================================

                st.session_state.messages.append(
                    assistant_message
                )


            # ========================================================
            # ERROR HANDLING
            # ========================================================
            except RuntimeError as exc:
                st.error(str(exc))
            except Exception as e:

                error_message = (
                    f"Something went wrong: {str(e)}"
                )


                st.error(
                    error_message
                )


                # Save error as part of chat history

                st.session_state.messages.append({

                    "role":
                        "assistant",

                    "content":
                        error_message,

                    "insights":
                        [],

                    "sql":
                        None,

                    "data_records":
                        [],

                    "visualization_required":
                        False,

                    "chart_type":
                        None,

                    "x_column":
                        None,

                    "y_column":
                        None,

                    "chart_title":
                        None,

                    "chart_data":
                        []
                })