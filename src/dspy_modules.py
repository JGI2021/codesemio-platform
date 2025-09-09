"""
Módulos DSPy para CodeSemio Platform
Implementa el reasoning y análisis inteligente
"""

import dspy
from typing import Dict, List, Any, Optional
import json


# ===== SIGNATURES DSPy =====

class MultiAppAnalysis(dspy.Signature):
    """Análisis multi-aplicación con contexto enriquecido"""
    query = dspy.InputField(desc="Consulta del usuario")
    application_context = dspy.InputField(desc="Contexto de la aplicación actual")
    search_results = dspy.InputField(desc="Resultados de búsqueda híbrida")
    embedding_types = dspy.InputField(desc="Tipos de embeddings utilizados")
    model_capabilities = dspy.InputField(desc="Capacidades del modelo actual")
    
    analysis = dspy.OutputField(desc="Análisis completo y detallado")
    code_suggestions = dspy.OutputField(desc="Sugerencias de código si aplica")
    recommendations = dspy.OutputField(desc="Recomendaciones específicas")
    confidence_score = dspy.OutputField(desc="Score de confianza 0-1")


class CrossAppKnowledgeTransfer(dspy.Signature):
    """Transferencia de conocimiento entre aplicaciones"""
    source_app = dspy.InputField(desc="Aplicación fuente con su dominio")
    target_app = dspy.InputField(desc="Aplicación destino con su dominio")
    pattern_to_transfer = dspy.InputField(desc="Patrón o conocimiento a transferir")
    source_examples = dspy.InputField(desc="Ejemplos concretos de la fuente")
    target_context = dspy.InputField(desc="Contexto y restricciones del destino")
    
    adapted_pattern = dspy.OutputField(desc="Patrón adaptado al contexto destino")
    implementation_code = dspy.OutputField(desc="Código de implementación si es posible")
    adaptation_strategy = dspy.OutputField(desc="Estrategia de adaptación utilizada")
    potential_issues = dspy.OutputField(desc="Problemas potenciales y mitigaciones")


class SemanticCodeUnderstanding(dspy.Signature):
    """Comprensión semántica profunda del código"""
    code_snippet = dspy.InputField(desc="Fragmento de código a analizar")
    ontology_context = dspy.InputField(desc="Contexto ontológico del dominio")
    embedding_analysis = dspy.InputField(desc="Análisis de embeddings múltiples")
    
    semantic_meaning = dspy.OutputField(desc="Significado semántico del código")
    design_patterns = dspy.OutputField(desc="Patrones de diseño identificados")
    business_logic = dspy.OutputField(desc="Lógica de negocio extraída")
    improvement_suggestions = dspy.OutputField(desc="Sugerencias de mejora")


class IntelligentModelSelection(dspy.Signature):
    """Selección inteligente de modelo LLM"""
    task_description = dspy.InputField(desc="Descripción detallada de la tarea")
    available_models = dspy.InputField(desc="Modelos disponibles con sus características")
    performance_history = dspy.InputField(desc="Historial de rendimiento por modelo")
    constraints = dspy.InputField(desc="Restricciones (costo, velocidad, privacidad)")
    
    recommended_model = dspy.OutputField(desc="Modelo recomendado con justificación")
    alternative_models = dspy.OutputField(desc="Modelos alternativos ordenados")
    configuration_params = dspy.OutputField(desc="Parámetros óptimos para el modelo")
    expected_performance = dspy.OutputField(desc="Rendimiento esperado")


class OntologyBasedReasoning(dspy.Signature):
    """Razonamiento basado en ontología formal"""
    query = dspy.InputField(desc="Consulta o problema a resolver")
    ontology_triples = dspy.InputField(desc="Triples RDF relevantes de la ontología")
    entity_relationships = dspy.InputField(desc="Relaciones entre entidades")
    domain_rules = dspy.InputField(desc="Reglas del dominio")
    
    logical_inference = dspy.OutputField(desc="Inferencias lógicas derivadas")
    semantic_expansion = dspy.OutputField(desc="Expansión semántica del concepto")
    related_concepts = dspy.OutputField(desc="Conceptos relacionados y jerarquía")
    actionable_insights = dspy.OutputField(desc="Insights accionables")


class HybridEmbeddingFusion(dspy.Signature):
    """Fusión inteligente de múltiples embeddings"""
    codebert_analysis = dspy.InputField(desc="Análisis desde CodeBERT")
    graphcodebert_analysis = dspy.InputField(desc="Análisis desde GraphCodeBERT")
    ontology_analysis = dspy.InputField(desc="Análisis desde embeddings de ontología")
    query_context = dspy.InputField(desc="Contexto de la consulta")
    
    fused_understanding = dspy.OutputField(desc="Comprensión fusionada y enriquecida")
    confidence_per_source = dspy.OutputField(desc="Confianza por cada fuente")
    synthesis = dspy.OutputField(desc="Síntesis integrada")
    missing_information = dspy.OutputField(desc="Información faltante identificada")


# ===== MÓDULOS DSPY =====

class CodeSemioAnalyzer(dspy.Module):
    """Analizador principal de CodeSemio con DSPy"""
    
    def __init__(self):
        super().__init__()
        
        # Módulos principales
        self.multi_app_analyzer = dspy.ChainOfThought(MultiAppAnalysis)
        self.semantic_understander = dspy.ChainOfThought(SemanticCodeUnderstanding)
        self.ontology_reasoner = dspy.ChainOfThought(OntologyBasedReasoning)
        self.embedding_fusioner = dspy.Predict(HybridEmbeddingFusion)
        
    def analyze_query(self, 
                     query: str,
                     search_results: List[Dict],
                     app_context: Dict,
                     model_info: Dict) -> Dict:
        """
        Análisis principal de una consulta
        
        Args:
            query: Consulta del usuario
            search_results: Resultados de búsqueda
            app_context: Contexto de la aplicación
            model_info: Información del modelo actual
            
        Returns:
            Análisis completo
        """
        # Preparar contextos
        app_context_str = f"App: {app_context.get('name', 'Unknown')}, Domain: {app_context.get('domain', 'General')}"
        search_results_str = self._format_search_results(search_results)
        embedding_types = app_context.get('embedding_types', [])
        model_caps = model_info.get('capabilities', [])
        
        # Análisis multi-aplicación
        result = self.multi_app_analyzer(
            query=query,
            application_context=app_context_str,
            search_results=search_results_str,
            embedding_types=", ".join(embedding_types),
            model_capabilities=", ".join(model_caps)
        )
        
        return {
            'analysis': result.analysis,
            'code_suggestions': result.code_suggestions,
            'recommendations': result.recommendations,
            'confidence': result.confidence_score
        }
    
    def understand_code_semantically(self,
                                    code: str,
                                    ontology: Dict,
                                    embeddings: Dict) -> Dict:
        """
        Comprensión semántica profunda del código
        
        Args:
            code: Código a analizar
            ontology: Contexto ontológico
            embeddings: Análisis de embeddings
            
        Returns:
            Comprensión semántica
        """
        result = self.semantic_understander(
            code_snippet=code[:1000],  # Limitar tamaño
            ontology_context=json.dumps(ontology, default=str)[:500],
            embedding_analysis=json.dumps(embeddings, default=str)[:500]
        )
        
        return {
            'semantic_meaning': result.semantic_meaning,
            'patterns': result.design_patterns,
            'business_logic': result.business_logic,
            'improvements': result.improvement_suggestions
        }
    
    def reason_with_ontology(self,
                            query: str,
                            ontology_data: Dict) -> Dict:
        """
        Razonamiento basado en ontología
        
        Args:
            query: Consulta
            ontology_data: Datos de la ontología
            
        Returns:
            Inferencias y insights
        """
        # Extraer componentes de la ontología
        triples = ontology_data.get('triples', [])
        relationships = ontology_data.get('relationships', {})
        rules = ontology_data.get('rules', [])
        
        result = self.ontology_reasoner(
            query=query,
            ontology_triples=json.dumps(triples[:10], default=str),
            entity_relationships=json.dumps(relationships, default=str),
            domain_rules=json.dumps(rules[:5], default=str)
        )
        
        return {
            'inference': result.logical_inference,
            'expansion': result.semantic_expansion,
            'related': result.related_concepts,
            'insights': result.actionable_insights
        }
    
    def fuse_embeddings(self,
                       query: str,
                       embedding_results: Dict) -> Dict:
        """
        Fusiona análisis de múltiples embeddings
        
        Args:
            query: Consulta original
            embedding_results: Resultados por tipo de embedding
            
        Returns:
            Comprensión fusionada
        """
        result = self.embedding_fusioner(
            codebert_analysis=json.dumps(embedding_results.get('codebert', {}), default=str),
            graphcodebert_analysis=json.dumps(embedding_results.get('graphcodebert', {}), default=str),
            ontology_analysis=json.dumps(embedding_results.get('ontology', {}), default=str),
            query_context=query
        )
        
        return {
            'fused': result.fused_understanding,
            'confidence': result.confidence_per_source,
            'synthesis': result.synthesis,
            'gaps': result.missing_information
        }
    
    def _format_search_results(self, results: List[Dict]) -> str:
        """Formatea resultados de búsqueda para DSPy"""
        formatted = []
        for r in results[:5]:  # Top 5
            formatted.append(
                f"Type: {r.get('type', 'unknown')}, "
                f"Score: {r.get('score', 0):.2f}, "
                f"Text: {r.get('text', '')[:100]}..."
            )
        return "\n".join(formatted)


class KnowledgeTransferEngine(dspy.Module):
    """Motor de transferencia de conocimiento entre aplicaciones"""
    
    def __init__(self):
        super().__init__()
        self.transfer_module = dspy.ChainOfThought(CrossAppKnowledgeTransfer)
        
    def transfer(self,
                source_app: str,
                target_app: str,
                pattern: str,
                source_data: List[Dict],
                target_data: List[Dict]) -> Dict:
        """
        Transfiere conocimiento entre aplicaciones
        
        Args:
            source_app: Aplicación fuente
            target_app: Aplicación destino
            pattern: Patrón a transferir
            source_data: Datos de la fuente
            target_data: Datos del destino
            
        Returns:
            Patrón adaptado e implementación
        """
        result = self.transfer_module(
            source_app=source_app,
            target_app=target_app,
            pattern_to_transfer=pattern,
            source_examples=json.dumps(source_data[:3], default=str),
            target_context=json.dumps(target_data[:3], default=str)
        )
        
        return {
            'adapted_pattern': result.adapted_pattern,
            'code': result.implementation_code,
            'strategy': result.adaptation_strategy,
            'warnings': result.potential_issues
        }


class ModelOptimizer(dspy.Module):
    """Optimizador de selección de modelos"""
    
    def __init__(self):
        super().__init__()
        self.selector = dspy.ChainOfThought(IntelligentModelSelection)
        
    def select_optimal_model(self,
                            task: str,
                            available_models: List[Dict],
                            history: Dict = None,
                            constraints: Dict = None) -> Dict:
        """
        Selecciona el modelo óptimo para una tarea
        
        Args:
            task: Descripción de la tarea
            available_models: Modelos disponibles
            history: Historial de rendimiento
            constraints: Restricciones
            
        Returns:
            Modelo recomendado y configuración
        """
        result = self.selector(
            task_description=task,
            available_models=json.dumps(available_models, default=str),
            performance_history=json.dumps(history or {}, default=str),
            constraints=json.dumps(constraints or {}, default=str)
        )
        
        return {
            'model': result.recommended_model,
            'alternatives': result.alternative_models,
            'config': result.configuration_params,
            'performance': result.expected_performance
        }


# ===== OPTIMIZADORES DSPy =====

class CodeSemioOptimizer:
    """Optimizador de prompts y módulos para CodeSemio"""
    
    def __init__(self, metric_fn=None):
        """
        Inicializa el optimizador
        
        Args:
            metric_fn: Función de métrica para evaluar calidad
        """
        self.metric = metric_fn or self.default_metric
        
    def optimize_module(self, module: dspy.Module, trainset: List) -> dspy.Module:
        """
        Optimiza un módulo DSPy con ejemplos
        
        Args:
            module: Módulo a optimizar
            trainset: Conjunto de entrenamiento
            
        Returns:
            Módulo optimizado
        """
        from dspy.teleprompt import BootstrapFewShot
        
        optimizer = BootstrapFewShot(metric=self.metric)
        optimized = optimizer.compile(module, trainset=trainset)
        
        return optimized
    
    def default_metric(self, example, prediction) -> float:
        """Métrica por defecto para evaluación"""
        # Verificar que la predicción tiene los campos esperados
        if hasattr(prediction, 'analysis') and prediction.analysis:
            score = 1.0
        else:
            score = 0.0
            
        # Bonus por confianza alta
        if hasattr(prediction, 'confidence_score'):
            try:
                conf = float(prediction.confidence_score)
                score *= conf
            except:
                pass
                
        return score
    
    def create_trainset_from_history(self, history: List[Dict]) -> List:
        """
        Crea conjunto de entrenamiento desde historial
        
        Args:
            history: Historial de interacciones
            
        Returns:
            Conjunto de entrenamiento para DSPy
        """
        trainset = []
        
        for item in history:
            example = dspy.Example(
                query=item.get('query', ''),
                application_context=item.get('app_context', ''),
                search_results=item.get('search_results', ''),
                analysis=item.get('analysis', ''),
                confidence_score=item.get('confidence', 0.5)
            )
            trainset.append(example)
            
        return trainset


# ===== PIPELINE COMPLETO =====

class CodeSemioDSPyPipeline:
    """Pipeline completo de procesamiento con DSPy"""
    
    def __init__(self):
        self.analyzer = CodeSemioAnalyzer()
        self.transfer_engine = KnowledgeTransferEngine()
        self.model_optimizer = ModelOptimizer()
        self.optimizer = CodeSemioOptimizer()
        
    def process_query(self,
                     query: str,
                     context: Dict) -> Dict:
        """
        Procesa una consulta completa
        
        Args:
            query: Consulta del usuario
            context: Contexto completo (app, model, search results)
            
        Returns:
            Respuesta procesada
        """
        # 1. Análisis principal
        analysis = self.analyzer.analyze_query(
            query=query,
            search_results=context.get('search_results', []),
            app_context=context.get('app_context', {}),
            model_info=context.get('model_info', {})
        )
        
        # 2. Si hay código, comprensión semántica
        if context.get('code_snippet'):
            semantic = self.analyzer.understand_code_semantically(
                code=context['code_snippet'],
                ontology=context.get('ontology', {}),
                embeddings=context.get('embeddings', {})
            )
            analysis['semantic_understanding'] = semantic
        
        # 3. Si hay ontología, razonamiento
        if context.get('ontology_data'):
            reasoning = self.analyzer.reason_with_ontology(
                query=query,
                ontology_data=context['ontology_data']
            )
            analysis['ontology_reasoning'] = reasoning
        
        # 4. Si hay múltiples embeddings, fusión
        if context.get('embedding_results'):
            fusion = self.analyzer.fuse_embeddings(
                query=query,
                embedding_results=context['embedding_results']
            )
            analysis['embedding_fusion'] = fusion
        
        return analysis