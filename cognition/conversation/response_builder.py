import re
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ai_models.llm.models import LLMResponse

class RichResponse(BaseModel):
    text: str = Field(..., description="Raw text response")
    markdown: str = Field(..., description="Markdown styled response")
    code_blocks: List[str] = Field(default_factory=list, description="Extracted code blocks")
    citations: List[str] = Field(default_factory=list, description="Citations and document references")
    tool_calls: List[Any] = Field(default_factory=list, description="Tool calls requested")
    reasoning: Optional[str] = Field(None, description="Chain of thought reasoning content")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    latency: float = Field(0.0, description="Latency of response generation in seconds")
    model: str = Field(..., description="Active model ID used")
    engine: str = Field(..., description="Active engine used")
    prompt_tokens: int = Field(0, description="Tokens consumed in prompt")
    completion_tokens: int = Field(0, description="Tokens produced in completion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dict")

class ResponseBuilder:
    def __init__(self):
        pass

    def build_rich_response(self, llm_res: LLMResponse, warnings: List[str] = None, extra_meta: Dict[str, Any] = None) -> RichResponse:
        """Constructs a structured RichResponse from an LLMResponse."""
        text = llm_res.text
        meta = llm_res.metadata or {}
        if extra_meta:
            meta.update(extra_meta)

        # Extract markdown code blocks
        code_blocks = re.findall(r"```[a-zA-Z0-9]*\n(.*?)\n```", text, re.DOTALL)

        # Extract citations
        citations = llm_res.citations or []
        if not citations:
            # Check text for reference annotations (e.g. [Document local])
            refs = re.findall(r"\[Document[^\]]*\]", text)
            citations.extend(refs)

        return RichResponse(
            text=text,
            markdown=llm_res.markdown or text,
            code_blocks=code_blocks,
            citations=citations,
            tool_calls=llm_res.tool_calls or [],
            reasoning=llm_res.reasoning,
            warnings=warnings or [],
            latency=llm_res.latency,
            model=llm_res.model,
            engine=meta.get("engine", "ollama"),
            prompt_tokens=llm_res.tokens_input,
            completion_tokens=llm_res.tokens_output,
            metadata=meta
        )

global_response_builder = ResponseBuilder()
