import os
import requests
import json
import logging
import inspect
from typing import List, Dict, Any, Optional

def _sanitize_text(text: str) -> str:
    if not text:
        return ""
    # Replace common currency symbols and punctuation
    text = text.replace("₹", "Rs.").replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    # Encode to ASCII and decode back to string to strip emojis and other non-ASCII chars
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

class GroqOllamaClient:
    # --- Class-level shared key pool so all agents rotate together (Groq) ---
    _api_keys: List[str] = []
    _key_index: int = 0
    _pool_initialized: bool = False

    # --- Class-level Ollama model pool so all agents rotate together ---
    _ollama_models: List[str] = []
    _ollama_model_index: int = 0
    _ollama_pool_initialized: bool = False

    @classmethod
    def _load_key_pool(cls) -> None:
        """Load all Groq API keys from groq_api_keys.txt and .env into the shared pool."""
        if cls._pool_initialized:
            return

        keys: List[str] = []

        # 1. Load from groq_api_keys.txt (format: NAME = "gsk_...")
        keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "groq_api_keys.txt")
        if os.path.exists(keys_file):
            with open(keys_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    # Support: KEY = "value" or KEY = value
                    if "=" in line:
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val.startswith("gsk_"):
                            keys.append(val)

        # 2. Also include .env GROQ_API_KEY if not already in the list
        env_key = os.getenv("GROQ_API_KEY", "").strip()
        if env_key and env_key not in keys:
            keys.insert(0, env_key)

        cls._api_keys = keys
        cls._pool_initialized = True

        if keys:
            logging.info(f"[GroqKeyPool] Loaded {len(keys)} API key(s) into rotation pool.")
        else:
            logging.warning("[GroqKeyPool] No Groq API keys found. Will fall back to Ollama.")

    @classmethod
    def _current_key(cls) -> str:
        return cls._api_keys[cls._key_index % len(cls._api_keys)] if cls._api_keys else ""

    @classmethod
    def _rotate_key(cls) -> str:
        """Advance to the next key and return it."""
        cls._key_index = (cls._key_index + 1) % len(cls._api_keys)
        new_key = cls._current_key()
        logging.warning(f"[GroqKeyPool] Rotated to key index {cls._key_index} (ends ...{new_key[-6:]})")
        return new_key


    @classmethod
    def _load_ollama_pool(cls) -> None:
        """Load Ollama models from OLLAMA_MODELS env var (comma-separated) into the shared pool."""
        if cls._ollama_pool_initialized:
            return
        # OLLAMA_MODELS takes priority; fall back to OLLAMA_MODEL for single-model setup
        raw = os.getenv("OLLAMA_MODELS", "").strip()
        if raw:
            cls._ollama_models = [m.strip() for m in raw.split(",") if m.strip()]
        else:
            default = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud").strip()
            cls._ollama_models = [default]
        cls._ollama_pool_initialized = True
        logging.info(f"[OllamaModelPool] Loaded {len(cls._ollama_models)} model(s): {cls._ollama_models}")

    @classmethod
    def _current_ollama_model(cls) -> str:
        return cls._ollama_models[cls._ollama_model_index % len(cls._ollama_models)] if cls._ollama_models else "gpt-oss:20b-cloud"

    @classmethod
    def _rotate_ollama_model(cls) -> str:
        """Advance to the next Ollama model and return it."""
        cls._ollama_model_index = (cls._ollama_model_index + 1) % len(cls._ollama_models)
        new_model = cls._current_ollama_model()
        logging.warning(f"[OllamaModelPool] Rotated to model index {cls._ollama_model_index}: '{new_model}'")
        return new_model

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self.default_model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

        # Initialize the shared key pool on first use
        GroqOllamaClient._load_key_pool()
        GroqOllamaClient._load_ollama_pool()

        # USE_OLLAMA=true forces local Ollama regardless of whether Groq keys are present
        force_ollama = os.getenv("USE_OLLAMA", "false").strip().lower() in ("true", "1", "yes")

        # Fallback to local Ollama client if no Groq keys are available OR forced
        self.use_ollama = force_ollama or not bool(self._api_keys)
        if self.use_ollama:
            import ollama
            self.ollama_client = ollama.Client(host=host or os.getenv("OLLAMA_HOST", "http://localhost:11434"))
            reason = "USE_OLLAMA=true" if force_ollama else "no Groq API keys found"
            logging.info(f"Using Ollama client ({reason}). Model pool: {self._ollama_models}")
        else:
            logging.info(f"Using Groq key pool ({len(self._api_keys)} keys). Model: {self.default_model}")


    def list(self) -> Any:
        if self.use_ollama:
            return self.ollama_client.list()
        return MockTags([MockModel(self.default_model)])

    def chat(self, model: Optional[str] = None, messages: Optional[List[Dict[str, Any]]] = None, tools: Optional[List[Any]] = None, options: Optional[Dict[str, Any]] = None) -> ChatResponse:
        # Sanitize messages to avoid tokenizer crashes on special unicode characters
        sanitized_messages = []
        if messages:
            for msg in messages:
                content = msg.get("content")
                if isinstance(content, str):
                    content = _sanitize_text(content)
                sanitized_msg = dict(msg)
                sanitized_msg["content"] = content
                sanitized_messages.append(sanitized_msg)
        messages = sanitized_messages

        if self.use_ollama:

            max_attempts = len(self._ollama_models) if self._ollama_models else 1
            last_error: Optional[Exception] = None
            for attempt in range(max_attempts):
                target_model = self._current_ollama_model()
                try:
                    result = self.ollama_client.chat(
                        model=target_model,
                        messages=messages,
                        tools=tools,
                        options=options
                    )
                    # Check for empty/useless response and rotate if so
                    content = getattr(getattr(result, "message", None), "content", None) or ""
                    tool_calls = getattr(getattr(result, "message", None), "tool_calls", None)
                    if not content.strip() and not tool_calls:
                        logging.warning(f"[OllamaModelPool] Model '{target_model}' returned empty response (attempt {attempt+1}/{max_attempts}). Rotating...")
                        self._rotate_ollama_model()
                        last_error = RuntimeError(f"Empty response from '{target_model}'")
                        continue
                    return result
                except Exception as e:
                    logging.warning(f"[OllamaModelPool] Model '{target_model}' failed (attempt {attempt+1}/{max_attempts}): {e}. Rotating...")
                    self._rotate_ollama_model()
                    last_error = e
            # All models failed — raise last error
            raise RuntimeError(
                f"[OllamaModelPool] All {max_attempts} Ollama model(s) failed. Last error: {last_error}"
            )

        target_model = model or self.default_model
        # Map model name: if code passes an Ollama model name, override it to use the Groq model
        if "gpt-oss" in target_model or "ollama" in target_model.lower():
            target_model = self.default_model

        groq_messages = []
        for msg in messages:
            gm: Dict[str, Any] = {
                "role": msg.get("role"),
                "content": msg.get("content"),
            }
            # Preserve tool-related fields required by the OpenAI/Groq chat spec
            if "name" in msg:
                gm["name"] = msg["name"]
            if "tool_call_id" in msg:
                gm["tool_call_id"] = msg["tool_call_id"]
            # Serialize tool_calls to plain dicts (handles both ToolCall objects and raw dicts)
            raw_tcs = msg.get("tool_calls")
            if raw_tcs:
                serialized = []
                for tc in raw_tcs:
                    if isinstance(tc, dict):
                        serialized.append(tc)
                    else:
                        # ToolCall / _InlineToolCall duck-typed object
                        import json as _json
                        args = tc.function.arguments
                        serialized.append({
                            "type": "function",
                            "id": getattr(tc, "id", f"call_{tc.function.name}"),
                            "function": {
                                "name": tc.function.name,
                                "arguments": _json.dumps(args) if isinstance(args, dict) else args,
                            },
                        })
                gm["tool_calls"] = serialized
            groq_messages.append(gm)

        payload = {
            "model": target_model,
            "messages": groq_messages,
            "temperature": options.get("temperature", 0.0) if options else 0.0
        }

        if tools:
            payload["tools"] = [map_function_to_tool(t) if callable(t) else t for t in tools]

        url = "https://api.groq.com/openai/v1/chat/completions"

        # --- Retry loop: rotate keys on 429 (rate limit) errors ---
        max_attempts = len(self._api_keys) if self._api_keys else 1
        last_error: Optional[Exception] = None

        for attempt in range(max_attempts):
            current_key = self._current_key()
            headers = {
                "Authorization": f"Bearer {current_key}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)

                if response.status_code == 429:
                    logging.warning(
                        f"[GroqKeyPool] 429 Rate limit on key ...{current_key[-6:]} "
                        f"(attempt {attempt + 1}/{max_attempts}). Rotating key..."
                    )
                    self._rotate_key()
                    last_error = requests.exceptions.HTTPError(response=response)
                    continue  # retry with next key

                response.raise_for_status()
                res_json = response.json()

                choice = res_json["choices"][0]
                msg_data = choice["message"]
                content = msg_data.get("content")

                tool_calls = []
                if "tool_calls" in msg_data:
                    for tc in msg_data["tool_calls"]:
                        func_data = tc["function"]
                        name = func_data["name"]
                        args_str = func_data["arguments"]
                        try:
                            args = json.loads(args_str)
                        except Exception:
                            args = {"code": args_str}
                        tool_calls.append(ToolCall(name, args))

                return ChatResponse(content, tool_calls)

            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    logging.warning(
                        f"[GroqKeyPool] 429 HTTPError on key ...{current_key[-6:]} "
                        f"(attempt {attempt + 1}/{max_attempts}). Rotating key..."
                    )
                    self._rotate_key()
                    last_error = e
                    continue
                raise  # re-raise non-429 HTTP errors immediately

        # All keys exhausted
        raise RuntimeError(
            f"[GroqKeyPool] All {max_attempts} Groq API key(s) hit the rate limit. "
            "Please wait before retrying or add more keys to groq_api_keys.txt."
        ) from last_error
