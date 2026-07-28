import time
import re
from typing import Dict, Any, Iterator
from cognition.conversation.models import ModelRequest, ModelResponse
from cognition.context.service import global_context_manager
from cognition.nlu.service import global_language_understanding
from cognition.session.service import global_session_manager
from cognition.prompt_builder.service import global_prompt_builder
from cognition.cache.service import global_response_cache
from knowledge.retriever import global_knowledge_retriever
from cognition.router.service import global_intent_router
from ai_models.model_manager.service import global_model_manager
from cognition.conversation.validator import global_response_validator
from cognition.conversation.response_builder import global_response_builder
from cognition.conversation.post_processing import global_post_processor

class ConversationEngine:
    def __init__(self):
        pass

    def change_model(self, engine_type: str, model_name: str) -> bool:
        """Dynamically switches active model/engine at runtime."""
        return global_model_manager.change_model(engine_type, model_name)

    @property
    def active_engine(self) -> str:
        return global_model_manager.active_engine_name

    @property
    def active_model(self) -> str:
        return global_model_manager.active_model_name

    def generate_response(self, prompt: str) -> ModelResponse:
        """
        Main offline conversational pipeline (Phase 2.5).
        No hardcoded templates, greetings, or code-blocks.
        All responses flow dynamically from NLU + Intelligent Router -> Retriever -> LLM -> Validator -> Post Processing.
        """
        start_time = time.time()
        global_session_manager.increment_requests()

        # 1. Check Response Cache for trivial responses (e.g. greetings, common offline status)
        cached_text = global_response_cache.get(prompt)
        if cached_text:
            global_session_manager.increment_cache_hits()
            latency = time.time() - start_time
            global_session_manager.update_stats(len(prompt)//4, len(cached_text)//4, latency)

            # Sync context turns
            global_context_manager.update_context("user", prompt)
            global_context_manager.update_context("assistant", cached_text)

            return ModelResponse(
                response=cached_text,
                metadata={
                    "engine": "cache",
                    "model": self.active_model,
                    "latency_seconds": round(latency, 4),
                    "cache_hit": True
                }
            )

        # 2. Run Language Understanding (NLU) analysis
        nlu = global_language_understanding.analyze(prompt)

        # 3. Route user request to get optimal RoutingDecision (pipeline, tools, agents)
        routing_decision = global_intent_router.route(prompt)

        # 4. Sync turn and RoutingDecision with Conversation Context Manager
        global_context_manager.update_context("user", prompt, routing_decision=routing_decision, nlu_result=nlu)
        context = global_context_manager.get_context()

        # 5. Retrieve background context from Vector database, SQLite base, and files
        retrieved_context = ""
        if routing_decision.requires_memory:
            retrieved_context = global_knowledge_retriever.retrieve_context(prompt, context)

        # 6. Format finalized optimized system & user prompts
        prompt_dict = global_prompt_builder.build_prompt(
            user_message=prompt,
            context=context,
            memory_context=retrieved_context,
            intent=routing_decision.intent,
            active_model=self.active_model
        )

        # 7. Generate response using Model Manager
        global_session_manager.increment_llm_calls()
        llm_response = global_model_manager.generate(
            prompt=prompt_dict["user"],
            system=prompt_dict["system"],
            intent=routing_decision.intent
        )

        raw_text = llm_response.text

        # Cache response if trivial or general
        if nlu.intent in ["greeting", "general_conversation"] and len(raw_text) < 150:
            global_response_cache.set(prompt, raw_text)

        # 8. Validate output structure (Markdown blocks, parentheses)
        validation = global_response_validator.validate(raw_text)
        validated_text = validation["final_text"]

        # 9. Format response using PostProcessor (color coding, formatting system keys)
        cleaned_text = global_post_processor.process_response(validated_text, context)

        # 10. Sync assistant reply with Conversation Context
        global_context_manager.update_context("assistant", cleaned_text)

        # Update last generated code to context reference if code blocks are present
        code_blocks = re.findall(r"```[a-zA-Z0-9]*\n(.*?)\n```", cleaned_text, re.DOTALL)
        if code_blocks:
            global_context_manager.set_last_generated_code(code_blocks[-1].strip())

        # Update session stats
        latency = time.time() - start_time
        global_session_manager.update_stats(llm_response.tokens_input, llm_response.tokens_output, latency)

        # Build Rich Response for deep Technical Observability
        rich_res = global_response_builder.build_rich_response(
            llm_response,
            warnings=validation["warnings"],
            extra_meta={
                "latency_seconds": latency,
                "pipeline": routing_decision.pipeline,
                "complexity": routing_decision.complexity
            }
        )

        return ModelResponse(
            response=cleaned_text,
            metadata=rich_res.model_dump()
        )

    def generate_response_stream(self, prompt: str) -> Iterator[ModelResponse]:
        """Provides streaming interface generating tokens word-by-word."""
        nlu = global_language_understanding.analyze(prompt)
        routing_decision = global_intent_router.route(prompt)

        global_context_manager.update_context("user", prompt, routing_decision=routing_decision, nlu_result=nlu)
        context = global_context_manager.get_context()

        retrieved_context = ""
        if routing_decision.requires_memory:
            retrieved_context = global_knowledge_retriever.retrieve_context(prompt, context)

        prompt_dict = global_prompt_builder.build_prompt(
            user_message=prompt,
            context=context,
            memory_context=retrieved_context,
            intent=routing_decision.intent,
            active_model=self.active_model
        )

        for chunk_res in global_model_manager.generate_stream(prompt_dict["user"], prompt_dict["system"], routing_decision.intent):
            cleaned_text = global_post_processor.process_response(chunk_res.text, context)
            yield ModelResponse(
                response=cleaned_text,
                metadata={
                    "engine": self.active_engine,
                    "model": self.active_model,
                    "streaming": True
                }
            )

global_conversation_engine = ConversationEngine()
