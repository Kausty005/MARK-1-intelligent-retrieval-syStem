# services/llm_service.py

import google.generativeai as genai
from core.config import settings

# Configure the Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

# System prompt to guide the LLM's response
SYSTEM_PROMPT = """
You are an expert AI assistant specializing in document analysis for insurance, legal, HR, and compliance domains.
Your task is to provide a clear, concise, and accurate answer to the user's question based ONLY on the provided context.

Follow these instructions strictly:
1.  Analyze the 'CONTEXT' section, which contains relevant clauses and text from the source document.
2.  Answer the 'QUESTION' using only the information available in the 'CONTEXT'.
3.  Do not use any external knowledge or make assumptions beyond the provided text.
4.  If the context does not contain the information needed to answer the question, you MUST respond with: "The provided document does not contain information on this topic."
5.  Formulate the answer directly and professionally, as if you were a domain expert.
"""

def get_llm_response(context: str, question: str) -> str:
    """
    Generates a response from the Gemini LLM based on the provided context and question.

    Args:
        context (str): The relevant text snippets from the document.
        question (str): The user's question.

    Returns:
        str: The LLM-generated answer.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        CONTEXT:
        ---
        {context}
        ---
        
        QUESTION: {question}
        """
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        
        response = model.generate_content(full_prompt)
        
        return response.text.strip()

    except Exception as e:
        print(f"Error generating LLM response: {e}")
        # Provide a fallback response in case of an API error
        return "Error: Could not retrieve an answer from the AI model."