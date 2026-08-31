import os
import json
import logging
import inspect
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, BaseMessage
try:
    from langchain_groq import ChatGroq
    HAS_CHAT_GROQ = True
except ImportError:
    HAS_CHAT_GROQ = False

try:
    from langchain_community.chat_models import ChatOllama
    HAS_CHAT_OLLAMA = True
except ImportError:
    HAS_CHAT_OLLAMA = False


def _sanitize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("₹", "Rs.").replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return text.encode("ascii", errors="ignore").decode("ascii")


def map_function_to_tool(func) -> Dict[str, Any]:
    if func.__name__ == "run_python_code":
        return {
            "type": "function",
            "function": {
                "name": "run_python_code",
                "description": "Executes Python/pandas code inside a Docker container. Returns the stdout/stderr output from the execution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The complete Python/Pandas code block to run."
                        },
                        "description": {
                            "type": "string",
                            "description": "A short description of what the code checks."
                        }
                    },
                    "required": ["code"]
                }
            }
        }
        
    sig = inspect.signature(func)
    properties = {}
    required = []
    for name, param in sig.parameters.items():
        properties[name] = {
            "type": "string",
            "description": f"Argument {name}"
        }
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__.strip() if func.__doc__ else "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }


class Message:
    def __init__(self, content: Optional[str], tool_calls: Optional[List[Any]] = None):
        self.content = content
        self.tool_calls = tool_calls or []

class ToolCallFunction:
    def __init__(self, name: str, arguments: Dict[str, Any]):
        self.name = name
        self.arguments = arguments

class ToolCall:
    def __init__(self, func_name: str, arguments: Dict[str, Any]):
        self.function = ToolCallFunction(func_name, arguments)

class ChatResponse:
    def __init__(self, content: Optional[str], tool_calls: Optional[List[Any]] = None):
        self.message = Message(content, tool_calls)

class MockModel:
    def __init__(self, model_name: str):
        self.model = model_name

class MockTags:
    def __init__(self, models: List[MockModel]):
        self.models = models


def get_llm(model_name: Optional[str] = None, temperature: float = 0.0) -> BaseChatModel:
    """
    Unified LangChain factory function returning a standard LangChain BaseChatModel.
    When USE_OLLAMA=true, directly returns ChatOllama with gpt-oss:20b-cloud.
    """
    GroqOllamaClient._load_key_pool()
    GroqOllamaClient._load_ollama_pool()

    force_ollama = os.getenv("USE_OLLAMA", "true").strip().lower() in ("true", "1", "yes")

    if force_ollama:
        ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud").strip()
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(model=ollama_model, base_url=host, temperature=temperature)
        except ImportError:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(model=ollama_model, base_url=host, temperature=temperature)

    target_model = model_name or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    if HAS_CHAT_GROQ and GroqOllamaClient._api_keys:
        api_key = GroqOllamaClient._current_key()
        if "gpt-oss" in target_model or "ollama" in target_model.lower():
            target_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        return ChatGroq(model=target_model, groq_api_key=api_key, temperature=temperature)
    elif HAS_CHAT_OLLAMA:
        ollama_model = GroqOllamaClient._current_ollama_model()
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return ChatOllama(model=ollama_model, base_url=host, temperature=temperature)
    else:
        from langchain_community.chat_models import FakeListChatModel
        return FakeListChatModel(responses=["Fallback model response"])


class GroqOllamaClient:
    """
    LangChain-backed LLM client maintaining key rotation and backwards compatibility.
    """
    _api_keys: List[str] = []
    _key_index: int = 0
    _pool_initialized: bool = False

    _ollama_models: List[str] = []
    _ollama_model_index: int = 0
    _ollama_pool_initialized: bool = False

    @classmethod
    def _load_key_pool(cls) -> None:
        if cls._pool_initialized:
            return
        keys: List[str] = []
        keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "groq_api_keys.txt")
        if os.path.exists(keys_file):
            with open(keys_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val.startswith("gsk_"):
                            keys.append(val)
        env_key = os.getenv("GROQ_API_KEY", "").strip()
        if env_key and env_key not in keys:
            keys.insert(0, env_key)
        cls._api_keys = keys
        cls._pool_initialized = True

    @classmethod
    def _current_key(cls) -> str:
        return cls._api_keys[cls._key_index % len(cls._api_keys)] if cls._api_keys else ""

    @classmethod
    def _rotate_key(cls) -> str:
        cls._key_index = (cls._key_index + 1) % len(cls._api_keys)
        new_key = cls._current_key()
        logging.warning(f"[GroqKeyPool] Rotated to key index {cls._key_index}")
        return new_key

    @classmethod
    def _load_ollama_pool(cls) -> None:
        if cls._ollama_pool_initialized:
            return
        raw = os.getenv("OLLAMA_MODELS", "").strip()
        if raw:
            cls._ollama_models = [m.strip() for m in raw.split(",") if m.strip()]
        else:
            default = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud").strip()
            cls._ollama_models = [default]
        cls._ollama_pool_initialized = True

    @classmethod
    def _current_ollama_model(cls) -> str:
        return cls._ollama_models[cls._ollama_model_index % len(cls._ollama_models)] if cls._ollama_models else "gpt-oss:20b-cloud"

    @classmethod
    def _rotate_ollama_model(cls) -> str:
        cls._ollama_model_index = (cls._ollama_model_index + 1) % len(cls._ollama_models)
        return cls._current_ollama_model()

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self.default_model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        GroqOllamaClient._load_key_pool()
        GroqOllamaClient._load_ollama_pool()

        force_ollama = os.getenv("USE_OLLAMA", "true").strip().lower() in ("true", "1", "yes")
        self.use_ollama = force_ollama or not bool(self._api_keys)

    def get_langchain_model(self, model: Optional[str] = None, temperature: float = 0.0) -> BaseChatModel:
        return get_llm(model or self.default_model, temperature=temperature)

    def list(self) -> Any:
        return MockTags([MockModel(self.default_model)])

    def chat(self, model: Optional[str] = None, messages: Optional[List[Dict[str, Any]]] = None, tools: Optional[List[Any]] = None, options: Optional[Dict[str, Any]] = None) -> ChatResponse:
        temperature = options.get("temperature", 0.0) if options else 0.0

        # Convert dict messages to LangChain BaseMessage instances
        lc_messages: List[BaseMessage] = []
        if messages:
            for msg in messages:
                role = msg.get("role")
                content = _sanitize_text(msg.get("content") or "")
                if role == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif role == "user":
                    lc_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))
                elif role == "tool":
                    lc_messages.append(ToolMessage(content=content, tool_call_id=msg.get("tool_call_id", "call_1")))
                else:
                    lc_messages.append(HumanMessage(content=content))

        ai_msg = None
        if self.use_ollama:
            llm = self.get_langchain_model(model=model, temperature=temperature)
            if tools:
                try:
                    llm_with_tools = llm.bind_tools(tools)
                    ai_msg = llm_with_tools.invoke(lc_messages)
                except Exception:
                    ai_msg = llm.invoke(lc_messages)
            else:
                ai_msg = llm.invoke(lc_messages)
        else:
            max_attempts = max(len(GroqOllamaClient._api_keys), 1)
            last_exception = None

            for attempt in range(max_attempts):
                llm = self.get_langchain_model(model=model, temperature=temperature)
                try:
                    if tools:
                        try:
                            llm_with_tools = llm.bind_tools(tools)
                            ai_msg = llm_with_tools.invoke(lc_messages)
                        except Exception as e_bind:
                            if "429" in str(e_bind) or "rate_limit" in str(e_bind).lower():
                                raise e_bind
                            ai_msg = llm.invoke(lc_messages)
                    else:
                        ai_msg = llm.invoke(lc_messages)
                    break
                except Exception as ex:
                    last_exception = ex
                    err_str = str(ex).lower()
                    if ("429" in err_str or "rate_limit" in err_str or "rate limit" in err_str) and GroqOllamaClient._api_keys:
                        logging.warning(f"[GroqKeyPool] 429 Rate limit encountered on key index {GroqOllamaClient._key_index}. Rotating key...")
                        GroqOllamaClient._rotate_key()
                    else:
                        break

        if ai_msg is None:
            logging.warning("[GroqKeyPool] All Groq API keys failed or rate-limited. Falling back to local Ollama (gpt-oss:20b-cloud)...")
            try:
                ollama_model_name = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud").strip()
                host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                try:
                    from langchain_ollama import ChatOllama
                    ollama_llm = ChatOllama(model=ollama_model_name, base_url=host, temperature=temperature)
                except ImportError:
                    from langchain_community.chat_models import ChatOllama
                    ollama_llm = ChatOllama(model=ollama_model_name, base_url=host, temperature=temperature)

                if tools:
                    try:
                        ollama_with_tools = ollama_llm.bind_tools(tools)
                        ai_msg = ollama_with_tools.invoke(lc_messages)
                    except Exception:
                        ai_msg = ollama_llm.invoke(lc_messages)
                else:
                    ai_msg = ollama_llm.invoke(lc_messages)
            except Exception as e_ollama:
                logging.error(f"[OllamaFallback] Ollama gpt-oss:20b-cloud fallback failed: {e_ollama}")
                if last_exception:
                    raise last_exception
                from langchain_community.chat_models import FakeListChatModel
                ai_msg = FakeListChatModel(responses=["Fallback model response"]).invoke(lc_messages)

        content = ai_msg.content if isinstance(ai_msg.content, str) else str(ai_msg.content)
        tool_calls = []
        if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
            for tc in ai_msg.tool_calls:
                tool_calls.append(ToolCall(tc["name"], tc.get("args", {})))

        return ChatResponse(content, tool_calls)


