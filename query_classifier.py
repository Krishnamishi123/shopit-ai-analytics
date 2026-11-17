import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


# =========================================================
# 1. LOAD ENVIRONMENT
# =========================================================

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY not found in .env file"
    )


# =========================================================
# 2. GEMINI MODEL
# =========================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)


# =========================================================
# 3. CLASSIFIER PROMPT
# =========================================================

classifier_prompt = ChatPromptTemplate.from_template(
    """
You are the query classification agent for Shopit's
AI Analytics system.

Your job is ONLY to classify the user's query.

Choose exactly ONE category:

DATABASE
RAG
UNKNOWN


=========================
DATABASE
=========================

Use DATABASE when the user is asking about:

- sales
- revenue
- orders
- customers
- products
- product performance
- customer behavior
- quantities
- prices
- averages
- totals
- rankings
- comparisons
- trends
- statistics
- numerical/business analysis

These questions require information from the Shopit
database.


Examples:

"Which product sold the most?"

"What is the total revenue?"

"Who are the top 10 customers?"

"What is the average order value?"

"Which category generated the highest sales?"

"How many orders did customer 101 place?"


=========================
RAG
=========================

Use RAG when the user is asking about Shopit's
company information, policies, rules, procedures,
or other information contained in Shopit's documents.

Examples:

"What is Shopit's return policy?"

"How many days do I have to return a product?"

"How can I cancel an order?"

"What is Shopit's shipping policy?"

"What is Shopit's seller policy?"

"Who is the head of the sales department?"

"Who owns Shopit?"


=========================
UNKNOWN
=========================

Use UNKNOWN when:

- the question is unrelated to Shopit
- the required information does not exist in the
  Shopit database or documents
- the question is general knowledge
- the question requires current external information
- the question is meaningless or impossible to answer


Examples:

"What is the weather today?"

"Who is the Prime Minister of India?"

"Explain quantum physics."

"What happened in yesterday's cricket match?"


=========================
IMPORTANT RULES
=========================

Return ONLY ONE of:

DATABASE
RAG
UNKNOWN

Do not provide an explanation.

User Query:

{question}
"""
)


# =========================================================
# 4. CLASSIFIER FUNCTION
# =========================================================

def classify_query(question):

    messages = classifier_prompt.format_messages(
        question=question
    )

    response = llm.invoke(messages)

    # Gemini may return either a string or content blocks
    if isinstance(response.content, list):

        result = "".join(
            block.get("text", "")
            for block in response.content
            if block.get("type") == "text"
        )

    else:

        result = response.content

    result = result.strip().upper()

    # Safety check
    if result not in [
        "DATABASE",
        "RAG",
        "UNKNOWN"
    ]:

        return "UNKNOWN"

    return result


# =========================================================
# 5. TEST CLASSIFIER
# =========================================================

if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk Shopit: "
        )

        if question.lower() == "exit":
            break

        category = classify_query(
            question
        )

        print(
            "\nCLASSIFICATION:",
            category
        )