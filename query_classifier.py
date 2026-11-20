
import re
import logging

logger = logging.getLogger("shopit.classifier")


# ==================================================
# 1. KEYWORDS FOR CLASSIFICATION
# ==================================================

DATABASE_PATTERNS = [
    r"\bsales?\b",
    r"\brevenue\b",
    r"\border(s)?\b",
    r"\bcustomer(s)?\b",
    r"\bproducts?\b",
    r"\btop\s+\d+\b",
    r"\bhighest\b",
    r"\blowest\b",
    r"\bbest[- ]selling\b",
    r"\baverage\b",
    r"\btotal\b",
    r"\bprofit\b",
    r"\bquantity\b",
    r"\bhow many\b",
    r"\bpercentage\b",
    r"\bgrowth\b",
    r"\btrend(s)?\b",
    r"\bperformance\b",
    r"\bspending\b",
    r"\bpurchased\b",
    r"\bpurchase(s)?\b",
    r"\bmonthly\b",
    r"\bweekly\b",
    r"\bdaily\b",
    r"\bcategory\b",
    r"\bcompare\b",
    r"\branking\b",
    r"\bretention\b",
    r"\bchurn\b",
    r"\bcohort\b",
    r"\brfm\b",
    r"\bbasket\b",
    r"\bforecast\b",
    r"\bdiscount\b",
    r"\brefund rate\b",
    r"\breturn rate\b"
]


RAG_PATTERNS = [
    r"\breturn policy\b",
    r"\brefund policy\b",
    r"\bshipping policy\b",
    r"\bcancellation policy\b",
    r"\bprivacy policy\b",
    r"\bseller policy\b",
    r"\bterms and conditions\b",
    r"\bhow can i cancel\b",
    r"\bhow do i cancel\b",
    r"\bhow many days.*return\b",
    r"\bdelivery rules\b",
    r"\bcompany policy\b",
    r"\bcompany information\b",
    r"\bwho owns shopit\b",
    r"\bwho founded shopit\b",
    r"\bceo of shopit\b",
    r"\bhead of .* department\b"
]


# ==================================================
# 2. CLASSIFIER FUNCTION
# ==================================================

def classify_query(question: str) -> str:

    if not isinstance(question, str) or not question.strip():
        return "UNKNOWN"

    question = question.lower().strip()

    # Check policy and company information first
    for pattern in RAG_PATTERNS:

        if re.search(pattern, question):
            logger.info("Query classified as RAG")
            return "RAG"

    # Check database-related questions
    for pattern in DATABASE_PATTERNS:

        if re.search(pattern, question):
            logger.info("Query classified as DATABASE")
            return "DATABASE"

    # Anything outside supported categories
    logger.info("Query classified as UNKNOWN")

    return "UNKNOWN"


# ==================================================
# 3. TEST CLASSIFIER
# ==================================================

if __name__ == "__main__":

    test_questions = [
        "How many products are there?",
        "Show top 10 products by revenue",
        "Which customers spend the most?",
        "What is Shopit's return policy?",
        "How can I cancel my order?",
        "What is today's weather?",
        "Explain quantum physics",
        "Calculate monthly sales growth",
    ]

    for question in test_questions:

        category = classify_query(question)

        print(f"\nQuestion: {question}")
        print(f"Category: {category}")
