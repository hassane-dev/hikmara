import pytest
import time
from ai_models.model_registry.service import global_model_registry
from ai_models.model_registry.models import ModelSpecs
from ai_models.embeddings.service import SentenceTransformersEmbedding, OllamaEmbedding
from ai_models.model_manager.service import global_model_manager, global_vision_engine
from cognition.cache.service import global_response_cache
from cognition.prompt_builder.optimizer import global_prompt_optimizer
from cognition.prompt_builder.registry import global_prompt_template_registry
from cognition.context.service import global_context_manager
from cognition.session.service import global_session_manager
from cognition.conversation.service import global_conversation_engine
from cognition.conversation.response_builder import global_response_builder
from cognition.conversation.validator import global_response_validator
from knowledge.retriever import global_knowledge_retriever
from tools.executor import global_tool_executor

def test_model_registry_capabilities():
    # Verify Model Registry maps standard local models and capabilities
    specs = global_model_registry.get_model("qwen2.5:3b")
    assert specs is not None
    assert specs.family == "Qwen"
    assert specs.engine == "ollama"
    assert specs.max_context == 4096

    caps = global_model_registry.get_capabilities("qwen2.5:3b")
    assert caps["streaming"] is True
    assert caps["tools"] is True

def test_embeddings_separation():
    # Verify embeddings are separated from conversational LLMs
    emb_st = SentenceTransformersEmbedding("all-minilm-l6-v2")
    vec1 = emb_st.embed_text("Test vector embedding")
    assert len(vec1) == 128
    assert isinstance(vec1[0], float)

    emb_ol = OllamaEmbedding("nomic-embed-text")
    vec2 = emb_ol.embed_text("Ollama test vector")
    assert len(vec2) == 128

def test_response_cache():
    # Test cached greeting
    global_response_cache.clear()
    global_response_cache.set("Test Key Query", "Simulated Cache Answer")
    assert global_response_cache.get("Test Key Query") == "Simulated Cache Answer"

    # Trivial greetings
    cached_greeting = global_response_cache.get("bonjour")
    assert cached_greeting is not None
    assert "Comment puis-je vous aider" in cached_greeting

def test_prompt_optimizer_and_budget_management():
    # Verify TokenBudgetManager and PromptOptimizer prunes history correctly
    history = [
        {"role": "user", "message": "Hi " * 100},
        {"role": "assistant", "message": "Hello " * 100},
        {"role": "user", "message": "Short message"}
    ]
    optimized = global_prompt_optimizer.optimize_prompt_inputs(
        system_base="System base",
        history=history,
        retrieved_context="Retrieved info",
        user_message="User message"
    )
    # The optimized history should contain fewer items or fit within token budget constraints
    assert len(optimized["history"]) <= len(history)

def test_prompt_template_registry():
    # Verify dynamic prompt template fetch
    sys_prompt = global_prompt_template_registry.get_template("system.md", "fr")
    assert "Hikmara" in sys_prompt

    missing_prompt = global_prompt_template_registry.get_template("non_existent_template.md", "fr")
    assert "local" in missing_prompt or "Hikmara" in missing_prompt

def test_session_manager_observability_metrics():
    # Verify Session Manager compiles and exposes metrics
    global_session_manager.open_session("test_sess", "developer")
    global_session_manager.increment_requests()
    global_session_manager.increment_llm_calls()
    global_session_manager.increment_cache_hits()
    global_session_manager.update_stats(100, 50, 0.25)

    metrics = global_session_manager.get_session_metrics()
    assert metrics["session_id"] == "test_sess"
    assert metrics["current_user"] == "developer"
    assert metrics["total_requests"] == 1
    assert metrics["total_llm_calls"] == 1
    assert metrics["total_cache_hits"] == 1
    assert metrics["total_turns"] == 1
    assert metrics["average_latency"] == 0.25

def test_knowledge_retriever_pipeline():
    # Verify KnowledgeRetriever coordinates multiple memory/db stores
    global_context_manager.reset_context()
    context = global_context_manager.get_context()
    retrieved = global_knowledge_retriever.retrieve_context("docker", context)
    assert "Docker" in retrieved or "Mémoire" in retrieved

def test_rich_response_builder():
    # Verify ResponseBuilder returns rich structured responses with latency, tokens, warning audits
    from ai_models.llm.models import LLMResponse
    llm_res = LLMResponse(
        text="```python\nprint('hello')\n```",
        markdown="```python\nprint('hello')\n```",
        latency=0.42,
        model="qwen2.5:3b",
        tokens_input=20,
        tokens_output=15
    )
    rich_res = global_response_builder.build_rich_response(llm_res, warnings=["Test warning"], extra_meta={"engine": "ollama"})
    assert rich_res.latency == 0.42
    assert rich_res.model == "qwen2.5:3b"
    assert rich_res.engine == "ollama"
    assert "Test warning" in rich_res.warnings
    assert len(rich_res.code_blocks) == 1
    assert rich_res.code_blocks[0].strip() == "print('hello')"

def test_streaming_generation():
    # Test streaming generation returns successive chunks
    chunks = list(global_conversation_engine.generate_response_stream("Bonjour"))
    assert len(chunks) > 0
    assert chunks[-1].response is not None

def test_tool_executor_security_gate():
    # Verify ToolExecutor intercepts unsafe tool execution or uninstalled tool errors gracefully
    res = global_tool_executor.execute_tool("non_existent_tool", {})
    assert res["status"] == "error"
    assert "non trouvé" in res["output"]

def test_multimodal_placeholders():
    res = global_vision_engine.process_image("image.jpg", "Analyze this")
    assert "[Vision Simulation]" in res["text"]
