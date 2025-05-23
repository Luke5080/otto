from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


class ModelFactory:
    @staticmethod
    def get_model(model):
        match model:
            case "gpt-4o-mini":
                return ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
            case "gpt-4o":
                return ChatOpenAI(model_name="gpt-4o", temperature=0)

            case "gpt-o3-mini":
                return ChatOpenAI(model_name="o3-mini", reasoning_effort="medium")
            case "llama":
                return ChatGroq(model="qwen-2.5-32b", temperature=0)

            case "deepseek-chat":
                return ChatDeepSeek(model_name="deepseek-chat", temperature=0)

            case "claude-3-5-sonnet":
                return ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

            case "gemini":
                return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
