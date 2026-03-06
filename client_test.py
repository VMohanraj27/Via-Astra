from langchain_google_genai import ChatGoogleGenerativeAI



MODEL_NAME="gemini-2.5-flash"
GOOGLE_API_KEY="AIzaSyBJOc1cjN-5WYVo9OtSIoHL5FJpTsJtPsM"

def get_llm():
    """Initialize base LLM instance."""
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY
    )
    return llm



llm = get_llm()

output = llm.invoke('what is potato?')

print(output)