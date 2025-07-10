from langchain.prompts import PromptTemplate

QUERY_PROMPT_TEMPLATE = """
        As a proficient PDF reader and data analyst, your main objectives are:
        1. Provide accurate and detailed responses.
        2. Ensure efficiency in information retrieval and analysis.
        3. if you are not sure of any informatioQUERY_PROMPTn verify it in table_html list (if given) in referance_table along with its file name and page number 
        than provide an answer.
        4. if the information is not mentioned in referance_table then Focus on the context only and generate answer from the context.         
        
        Guidelines:
        - If the answer is unknown, explicitly state so. Avoid conjecture or unverified assumptions.
        - Prioritize relevance and accuracy in the information provided.
        - Maintain clarity and conciseness in explanations.
        - give answer from context if you are unable to varify it from referance_table 

        
        Context:
        {context}

        referance_table:
        {referance_table}
        
        Question:
        {question}
        Expected Answer:
        Let's think step by step
        [Provide a comprehensive and relevant answer, integrating data insights where applicable. If the answer is not available, clearly state the limitations in the current knowledge or data.]
        """

QUERY_PROMPT = PromptTemplate.from_template(template=QUERY_PROMPT_TEMPLATE)


GUILDELINES_PROMPT_TEMPLATE = """
User Query:
{user_query}

Initial LLM Response:
{llm_response}

Admin Instructions:
{admin_instructions}

Task:
Refactor the initial LLM response to align with the Admin Instructions. Ensure the revised answer addresses the User Query effectively. Follow these steps:

1. Review the User Query to understand the core question or information sought.
2. Analyze the Initial LLM Response for its relevance and accuracy in addressing the User Query.
3. Compare the Initial LLM Response with the Admin Instructions. Identify any discrepancies or areas needing improvement.
4. Refactor the answer:
    - If the Initial LLM Response aligns well with the Admin Instructions and adequately addresses the User Query, you may return the same answer.
    - If the Initial LLM Response does not fully comply with the Admin Instructions or could better satisfy the User Query, modify the answer accordingly.
    - Ensure the refactored answer is clear, concise, and directly addresses the User Query, while adhering to the Admin Instructions.
5. Present the refactored answer as the final response.

Final Response:
[Provide the refactored answer here, ensuring it meets the criteria of addressing the User Query effectively and adhering to the Admin Instructions.]

"""

GUILDELINES_PROMPT = PromptTemplate.from_template(template=GUILDELINES_PROMPT_TEMPLATE)

DISCREPANCY_DETECTION_PROMPT = """
I have extracted data from two documents using Azure Document Intelligence: a Letter of Credit (LC) and an Invoice. 

Please review both documents carefully and analyze whether the Invoice correctly aligns with the Letter of Credit. Instead of just listing field-by-field differences, provide a **human-like and meaningful assessment** based on the following:

### 1️ Overall Matching Summary**
- In plain language, summarize whether the Invoice corresponds well with the LC.
- Highlight key matches that confirm they belong to the same transaction.

### 2️ Any Important Concerns?**
- If there are differences, focus on the ones that actually **matter** (e.g., different amounts, reference numbers, or parties).
- Instead of a strict mismatch report, explain why a certain inconsistency might be acceptable or problematic.
- If a discrepancy is likely just a formatting or human entry error, point that out gently.

### 3️ Practical Assessment & Recommendation**
- Based on the comparison, give a **final verdict** on whether the Invoice is likely valid for this LC.
- Use a confidence level (e.g., “This looks like a strong match,” “There are minor inconsistencies but nothing critical,” or “This Invoice does not seem to belong to this LC”).
- Offer guidance on what next steps the user should take if there's an issue.

Keep your response **clear, professional, and easy to understand**—as if you were explaining this to a financial officer who needs to approve the invoice. 

---

## **Letter of Credit (LC) Data**
{lc_response}

## **Invoice Data**
{invoice_response}

"""


COMPARISON_PROMT= PromptTemplate.from_template(template=DISCREPANCY_DETECTION_PROMPT)