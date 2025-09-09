"""
Configuración de modelos LLM y aplicaciones
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional


class LLMModel(Enum):
    """Modelos LLM disponibles en la plataforma"""
    # OpenAI
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT4_MINI = "gpt-4o-mini"
    GPT35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_INSTANT = "claude-instant"
    
    # Open Source
    LLAMA_70B = "llama-70b"
    LLAMA_13B = "llama-13b"
    MISTRAL_LARGE = "mistral-large"
    MISTRAL_7B = "mistral-7b"
    
    # Specialized
    CODELLAMA = "codellama-34b"
    STARCODER = "starcoder"
    GEMINI_PRO = "gemini-pro"


class Application(Enum):
    """Aplicaciones registradas en CodeSemio"""
    ROSETTA_ETL = "rosetta_etl"
    EMBAT_TREASURY = "embat_treasury"
    SAP_CONNECTOR = "sap_connector"
    DATA_QUALITY = "data_quality"
    ORACLE_INTEGRATION = "oracle_integration"
    SALESFORCE_SYNC = "salesforce_sync"
    GENERIC = "generic"


class EmbeddingType(Enum):
    """Tipos de embeddings disponibles"""
    CODEBERT = "codebert"
    GRAPHCODEBERT = "graphcodebert"
    ONTOLOGY = "ontology"
    HYBRID = "hybrid"
    OPENAI_ADA = "text-embedding-ada-002"
    OPENAI_3_LARGE = "text-embedding-3-large"


@dataclass
class ModelConfig:
    """Configuración detallada de cada modelo"""
    name: str
    provider: str
    context_window: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    speed: str  # fast, medium, slow
    capabilities: List[str]
    best_for: List[str]
    supports_functions: bool = False
    supports_vision: bool = False
    supports_streaming: bool = True


# Configuraciones detalladas de modelos
MODEL_CONFIGS = {
    LLMModel.GPT4: ModelConfig(
        name="GPT-4",
        provider="openai",
        context_window=8192,
        cost_per_1k_input=0.03,
        cost_per_1k_output=0.06,
        speed="slow",
        capabilities=["reasoning", "code", "analysis", "creative"],
        best_for=["complex_analysis", "architecture_design", "code_review"],
        supports_functions=True
    ),
    
    LLMModel.GPT4_MINI: ModelConfig(
        name="GPT-4 Mini",
        provider="openai",
        context_window=128000,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        speed="fast",
        capabilities=["reasoning", "code", "analysis"],
        best_for=["quick_analysis", "code_generation", "chat"],
        supports_functions=True,
        supports_vision=True
    ),
    
    LLMModel.GPT35_TURBO: ModelConfig(
        name="GPT-3.5 Turbo",
        provider="openai",
        context_window=16384,
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.0015,
        speed="fast",
        capabilities=["code", "basic_analysis", "chat"],
        best_for=["quick_responses", "simple_queries", "prototyping"],
        supports_functions=True
    ),
    
    LLMModel.CLAUDE_3_OPUS: ModelConfig(
        name="Claude 3 Opus",
        provider="anthropic",
        context_window=200000,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        speed="medium",
        capabilities=["code", "long_context", "reasoning", "analysis"],
        best_for=["code_generation", "documentation", "complex_reasoning"],
        supports_vision=True
    ),
    
    LLMModel.MISTRAL_LARGE: ModelConfig(
        name="Mistral Large",
        provider="mistral",
        context_window=32000,
        cost_per_1k_input=0.004,
        cost_per_1k_output=0.012,
        speed="fast",
        capabilities=["multilingual", "code", "reasoning"],
        best_for=["european_languages", "fast_inference", "code_completion"],
        supports_functions=True
    ),
    
    LLMModel.LLAMA_70B: ModelConfig(
        name="Llama 2 70B",
        provider="meta",
        context_window=4096,
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.001,
        speed="medium",
        capabilities=["code", "reasoning", "open_source"],
        best_for=["on_premise", "privacy_sensitive", "customization"],
        supports_functions=False
    ),
    
    LLMModel.CODELLAMA: ModelConfig(
        name="Code Llama 34B",
        provider="meta",
        context_window=16384,
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.0005,
        speed="fast",
        capabilities=["code", "completion", "debugging"],
        best_for=["code_generation", "code_completion", "refactoring"],
        supports_functions=False
    )
}


@dataclass
class ApplicationConfig:
    """Configuración de cada aplicación"""
    name: str
    description: str
    primary_language: str
    domain: str
    embedding_types: List[EmbeddingType]
    preferred_models: List[LLMModel]
    ontology_path: Optional[str] = None
    
    
# Configuraciones de aplicaciones
APPLICATION_CONFIGS = {
    Application.ROSETTA_ETL: ApplicationConfig(
        name="Rosetta ETL",
        description="Sistema ETL inteligente con Node.js",
        primary_language="javascript",
        domain="data_integration",
        embedding_types=[
            EmbeddingType.CODEBERT,
            EmbeddingType.GRAPHCODEBERT,
            EmbeddingType.ONTOLOGY,
            EmbeddingType.HYBRID
        ],
        preferred_models=[
            LLMModel.GPT4_MINI,
            LLMModel.CODELLAMA
        ],
        ontology_path="/ontologies/rosetta_etl_complete_ontology.ttl"
    ),
    
    Application.EMBAT_TREASURY: ApplicationConfig(
        name="Embat Treasury Management",
        description="Gestión de tesorería y análisis financiero",
        primary_language="python",
        domain="finance",
        embedding_types=[
            EmbeddingType.ONTOLOGY,
            EmbeddingType.HYBRID,
            EmbeddingType.OPENAI_3_LARGE
        ],
        preferred_models=[
            LLMModel.GPT4,
            LLMModel.CLAUDE_3_OPUS
        ],
        ontology_path="/ontologies/financial_ontology.ttl"
    ),
    
    Application.SAP_CONNECTOR: ApplicationConfig(
        name="SAP Connector",
        description="Integración con sistemas SAP",
        primary_language="java",
        domain="enterprise_integration",
        embedding_types=[
            EmbeddingType.CODEBERT,
            EmbeddingType.ONTOLOGY
        ],
        preferred_models=[
            LLMModel.GPT4,
            LLMModel.MISTRAL_LARGE
        ]
    )
}


class ModelSelector:
    """Selector inteligente de modelos según la tarea"""
    
    @staticmethod
    def select_for_task(task_type: str, 
                        constraints: Dict = None) -> LLMModel:
        """
        Selecciona el mejor modelo para una tarea
        
        Args:
            task_type: Tipo de tarea (code_generation, analysis, etc)
            constraints: Restricciones (max_cost, speed, etc)
        
        Returns:
            Modelo recomendado
        """
        # Mapeo de tareas a modelos
        task_model_map = {
            'code_generation': LLMModel.CODELLAMA,
            'code_review': LLMModel.GPT4,
            'quick_answer': LLMModel.GPT35_TURBO,
            'complex_analysis': LLMModel.GPT4,
            'long_document': LLMModel.CLAUDE_3_OPUS,
            'multilingual': LLMModel.MISTRAL_LARGE,
            'on_premise': LLMModel.LLAMA_70B,
            'vision': LLMModel.GPT4_MINI
        }
        
        recommended = task_model_map.get(task_type, LLMModel.GPT4_MINI)
        
        # Aplicar restricciones si existen
        if constraints:
            if 'max_cost' in constraints:
                max_cost = constraints['max_cost']
                # Filtrar modelos por costo
                affordable_models = [
                    model for model, config in MODEL_CONFIGS.items()
                    if config.cost_per_1k_input <= max_cost
                ]
                if affordable_models:
                    recommended = affordable_models[0]
            
            if 'required_speed' in constraints:
                speed = constraints['required_speed']
                # Filtrar por velocidad
                fast_models = [
                    model for model, config in MODEL_CONFIGS.items()
                    if config.speed == speed
                ]
                if fast_models:
                    recommended = fast_models[0]
        
        return recommended
    
    @staticmethod
    def get_fallback_chain(primary_model: LLMModel) -> List[LLMModel]:
        """
        Obtiene cadena de fallback para un modelo
        
        Args:
            primary_model: Modelo principal
            
        Returns:
            Lista de modelos de fallback en orden de preferencia
        """
        fallback_chains = {
            LLMModel.GPT4: [LLMModel.GPT4_MINI, LLMModel.GPT35_TURBO],
            LLMModel.CLAUDE_3_OPUS: [LLMModel.CLAUDE_3_SONNET, LLMModel.GPT4_MINI],
            LLMModel.LLAMA_70B: [LLMModel.LLAMA_13B, LLMModel.MISTRAL_7B],
            LLMModel.CODELLAMA: [LLMModel.STARCODER, LLMModel.GPT35_TURBO]
        }
        
        return fallback_chains.get(primary_model, [LLMModel.GPT4_MINI])


# Export configurations as JSON for external use
def export_configs_to_json():
    """Exporta configuraciones a JSON para uso externo"""
    import json
    
    models_json = {}
    for model, config in MODEL_CONFIGS.items():
        models_json[model.value] = {
            'name': config.name,
            'provider': config.provider,
            'context_window': config.context_window,
            'cost_input': config.cost_per_1k_input,
            'cost_output': config.cost_per_1k_output,
            'speed': config.speed,
            'capabilities': config.capabilities,
            'best_for': config.best_for
        }
    
    apps_json = {}
    for app, config in APPLICATION_CONFIGS.items():
        apps_json[app.value] = {
            'name': config.name,
            'description': config.description,
            'language': config.primary_language,
            'domain': config.domain,
            'embeddings': [e.value for e in config.embedding_types],
            'preferred_models': [m.value for m in config.preferred_models]
        }
    
    return {
        'models': models_json,
        'applications': apps_json
    }