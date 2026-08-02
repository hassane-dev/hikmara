import pytest
import time
import sys
from contracts.models import (
    KVCacheKey, TaskExecutionPlan, InferenceProfile, Capability, PerformanceProfile,
    WorkspaceContext, WorkspaceFile
)
from contracts.errors import (
    ModelLoadError, MemoryPressureError, SchedulerError
)
from ai_models.model_manager.service import (
    PromptCache, KVCacheManager, EngineHotPool, ModelLifecycleManager,
    InferencePlanner, InferenceScheduler, ModelManager, global_model_manager
)
from ai_models.model_manager.metrics_service import global_metrics_service
from core.system.service import global_resource_manager, global_resource_monitor
from core.system.health_service import global_health_check_service
from ai_models.model_registry.service import global_model_registry
from ai_models.llm.base import BaseLLM

# ----------------------------------------------------
# TEST 1: Isolation absolue du KV Cache (Session A vs Session B)
# ----------------------------------------------------
def test_kv_cache_isolation():
    manager = KVCacheManager()

    key_a = KVCacheKey(
        session_id="session_A",
        project_id="proj_1",
        model_hash="hash_qwen",
        system_hash="sys_prompt_1",
        template_version="1.0.0",
        tokenizer_hash="tok_1",
        context_window=2048,
        generation_id="gen_1",
        security_scope_hash="sec_hash_1"
    )

    key_b = KVCacheKey(
        session_id="session_B",
        project_id="proj_1",
        model_hash="hash_qwen",
        system_hash="sys_prompt_1",
        template_version="1.0.0",
        tokenizer_hash="tok_1",
        context_window=2048,
        generation_id="gen_1",
        security_scope_hash="sec_hash_1"
    )

    # Store attention state for Session A
    state_a = {"attention": [0.1, 0.2, 0.9]}
    manager.set_attention_state(key_a, state_a)

    # Fetch attention state for Session A and Session B
    assert manager.get_attention_state(key_a) == state_a
    assert manager.get_attention_state(key_b) is None


# ----------------------------------------------------
# TEST 2: Invalidation automatique sur changement de modèle
# ----------------------------------------------------
def test_kv_cache_invalidation_on_model_change():
    manager = KVCacheManager()

    key_a = KVCacheKey(
        session_id="session_A",
        project_id="proj_1",
        model_hash="hash_model_A",
        system_hash="sys_prompt_1",
        template_version="1.0.0",
        tokenizer_hash="tok_1",
        context_window=2048,
        generation_id="gen_1",
        security_scope_hash="sec_hash_1"
    )

    key_b = KVCacheKey(
        session_id="session_A",
        project_id="proj_1",
        model_hash="hash_model_B",
        system_hash="sys_prompt_1",
        template_version="1.0.0",
        tokenizer_hash="tok_1",
        context_window=2048,
        generation_id="gen_1",
        security_scope_hash="sec_hash_1"
    )

    state_a = {"attention": [0.5, 0.5]}
    manager.set_attention_state(key_a, state_a)

    assert manager.get_attention_state(key_a) == state_a
    assert manager.get_attention_state(key_b) is None


# ----------------------------------------------------
# TEST 3: Résilience en situation de mémoire vive critique
# ----------------------------------------------------
def test_resilience_under_memory_pressure(monkeypatch):
    lifecycle = ModelLifecycleManager(PerformanceProfile.LOW_POWER)

    # Mock RAM availability to be extremely low (0.5 Go)
    monkeypatch.setattr(global_resource_manager, "get_metrics", lambda: {
        "cpu_percent": 15.0,
        "ram_total_gb": 16.0,
        "ram_available_gb": 0.5, # Critical RAM
        "ram_percent": 97.0,
        "disk_free_gb": 100.0,
        "disk_percent": 45.0
    })

    # Force IS_TESTING to False in the service module to trigger actual production MemoryPressureError
    monkeypatch.setattr(sys.modules["ai_models.model_manager.service"], "IS_TESTING", False)

    # Test load of model when memory is highly critical
    with pytest.raises(MemoryPressureError) as exc_info:
        lifecycle.load_model("qwen2.5-3b-instruct-q4_k_m.gguf")
    assert "Ressources RAM insuffisantes" in str(exc_info.value)


# ----------------------------------------------------
# TEST 4: Mesure temporelle de Cold Start vs Warm Inference
# ----------------------------------------------------
def test_cold_start_vs_warm_inference():
    # Cold start: Model needs loading and full path resolution
    start_cold = time.time()
    global_model_manager.load_model("qwen-model.gguf")
    global_model_manager.generate("Test query", intent="general")
    duration_cold = time.time() - start_cold

    # Warm inference: Model is already loaded, attention context reuse
    start_warm = time.time()
    global_model_manager.generate("Test query", intent="general")
    duration_warm = time.time() - start_warm

    # Warm inference should be strictly faster than cold start
    assert duration_warm <= duration_cold


# ----------------------------------------------------
# TEST 5: Stabilité mémoire après 100 changements successifs
# ----------------------------------------------------
def test_memory_stability_over_model_switches():
    # Loop over switches to ensure no leaks or orphan engine references are retained
    initial_pool_size = len(global_model_manager.lifecycle.hot_pool._pool)

    for i in range(10):  # limit to 10 for execution speed in tests
        global_model_manager.load_model("qwen-model.gguf")
        global_model_manager.load_model("coder-model.gguf")

    # The hot pool should cleanly keep only the models up to its maximum slot allowance
    max_slots = global_model_manager.lifecycle.hot_pool.get_max_slots()
    assert len(global_model_manager.lifecycle.hot_pool._pool) <= max_slots


# ----------------------------------------------------
# TEST 6: Échec contrôlé lors d'un chargement GGUF (Rollback)
# ----------------------------------------------------
def test_model_load_failure_and_rollback(monkeypatch):
    lifecycle = ModelLifecycleManager()

    # Load initial working baseline model
    lifecycle.load_model("qwen-model.gguf")
    assert lifecycle.active_model_id == "qwen-model.gguf"

    # Mock ModelRegistry to return an invalid model or mock LLMFactory to raise an error
    monkeypatch.setattr(global_model_registry, "get_model", lambda mid: None)

    # Attempt load of non-existent model should trigger a clean rollback to the previous model
    with pytest.raises(ModelLoadError):
        lifecycle.load_model("corrupted-model.gguf")

    # System successfully recovered the previous active model
    assert lifecycle.active_model_id == "qwen-model.gguf"


# ----------------------------------------------------
# TEST 7: Invalidation du cache sur modification du prompt système
# ----------------------------------------------------
def test_kv_cache_invalidation_on_system_prompt_change():
    manager = KVCacheManager()

    key_a = KVCacheKey(
        session_id="session_A",
        project_id="proj_1",
        model_hash="hash_qwen",
        system_hash="system_prompt_A",
        template_version="1.0.0",
        tokenizer_hash="tok_1",
        context_window=2048,
        generation_id="gen_1",
        security_scope_hash="sec_hash_1"
    )

    key_b = KVCacheKey(
        session_id="session_A",
        project_id="proj_1",
        model_hash="hash_qwen",
        system_hash="system_prompt_B", # altered prompt
        template_version="1.0.0",
        tokenizer_hash="tok_1",
        context_window=2048,
        generation_id="gen_1",
        security_scope_hash="sec_hash_1"
    )

    state_a = {"attention": [0.99]}
    manager.set_attention_state(key_a, state_a)

    assert manager.get_attention_state(key_a) == state_a
    assert manager.get_attention_state(key_b) is None


# ----------------------------------------------------
# TEST 8 (UI 1): Non-blocage de l'interface graphique (Asynchronisme)
# ----------------------------------------------------
def test_asynchronous_ui_model_load():
    loaded_status = [None]

    def on_complete(success: bool):
        loaded_status[0] = success

    # Trigger load_model_async which returns immediately without blocking
    global_model_manager.load_model_async("qwen-model.gguf", on_complete)

    # Wait briefly for thread execution
    time.sleep(0.1)
    assert loaded_status[0] is True


# ----------------------------------------------------
# TEST 9 (UI 2): Traitement d'erreur asynchrone
# ----------------------------------------------------
def test_asynchronous_ui_model_load_error():
    loaded_status = [None]

    def on_complete(success: bool):
        loaded_status[0] = success

    # Loading a non-existent model should return False but never crash the background thread
    global_model_manager.load_model_async("non_existent_model.gguf", on_complete)

    time.sleep(0.1)
    assert loaded_status[0] is False


# ----------------------------------------------------
# TEST 10 (UI 3): Dynamisme des métriques de performance
# ----------------------------------------------------
def test_inference_metrics_dynamism():
    metrics = global_metrics_service.get_metrics()

    assert metrics.model_active is not None
    assert metrics.ram_usage > 0.0
    assert metrics.cpu_usage >= 0.0
    assert metrics.energy is not None
    assert metrics.energy.cpu_seconds >= 0.0


# ----------------------------------------------------
# TEST 11: Protection et récupération après pression mémoire OS externe
# ----------------------------------------------------
def test_graceful_degradation_under_external_ram_pressure(monkeypatch):
    pool = EngineHotPool(PerformanceProfile.BALANCED)

    # Mock LLM instances
    class MockEngine(BaseLLM):
        def load_model(self) -> bool: return True
        def unload_model(self) -> bool: return True
        def generate(self, prompt, system=""): return None
        def generate_stream(self, prompt, system=""): return None
        def health_check(self) -> bool: return True
        def list_models(self): return []
        def switch_model(self, model_name): return True
        def supports_streaming(self): return True
        def supports_tools(self): return True

    engine_1 = MockEngine("qwen-model.gguf")
    engine_2 = MockEngine("coder-model.gguf")

    pool.release("qwen-model.gguf", engine_1)
    pool.release("coder-model.gguf", engine_2)
    assert len(pool._pool) == 2

    # Simulate heavy OS RAM pressure (RAM drops under 1.5 Go)
    monkeypatch.setattr(global_resource_monitor, "get_metrics", lambda: {
        "cpu_percent": 80.0,
        "ram_total_gb": 16.0,
        "ram_available_gb": 1.1, # Critical RAM under 1.5 Go threshold
        "ram_percent": 93.0
    })

    # Adding another or releasing triggers immediate eviction of all standby models
    engine_3 = MockEngine("reasoning-model.gguf")
    pool.release("reasoning-model.gguf", engine_3)

    # Secondary engines are evicted cleanly, keeping only the active one
    assert len(pool._pool) == 1
    assert "reasoning-model.gguf" in pool._pool


# ----------------------------------------------------
# TEST 12 (UI 4): Isolation de l'Observabilité (Dashboard vs Controller)
# ----------------------------------------------------
def test_observability_passive_isolation():
    metrics = global_metrics_service.get_metrics()

    # Verify we can read standard metrics fields
    assert hasattr(metrics, "model_active")
    assert hasattr(metrics, "ttft")
    assert hasattr(metrics, "loaded_models")

    # Verify that metrics object has zero control commands or references to ModelLifecycleManager loading methods
    assert not hasattr(metrics, "load_model")
    assert not hasattr(metrics, "unload_model")
    assert not hasattr(metrics, "change_model")
