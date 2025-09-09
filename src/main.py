#!/usr/bin/env python3
"""
CodeSemio Platform - Main Entry Point
Sistema de Inteligencia de Código Multi-Aplicación
"""

import os
import sys
from datetime import datetime
from typing import Optional

# Añadir src al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from platform import CodeSemioPlatform
from models import LLMModel, Application, MODEL_CONFIGS
from dspy_modules import CodeSemioDSPyPipeline


class CodeSemioUI:
    """Interfaz de usuario interactiva para CodeSemio"""
    
    def __init__(self):
        """Inicializa la UI"""
        print("\n" + "="*70)
        print("🧠 CODESEMIO PLATFORM v1.0.0")
        print("Knowledge Acquisition System for Applications")
        print("="*70)
        
        self.platform = CodeSemioPlatform()
        self.running = True
        
    def run(self):
        """Ejecuta el loop principal de la UI"""
        while self.running:
            self._show_status()
            self._show_menu()
            self._handle_input()
    
    def _show_status(self):
        """Muestra el estado actual"""
        print(f"\n📍 Session: {self.platform.session_id}")
        print(f"📱 App: {self.platform.current_app or 'None'}")
        print(f"🤖 Model: {self.platform.current_model.value}")
        print("-" * 70)
    
    def _show_menu(self):
        """Muestra el menú principal"""
        print("\n📋 MENÚ PRINCIPAL:")
        print("1. 📱 Seleccionar Aplicación")
        print("2. 🤖 Seleccionar Modelo LLM")
        print("3. 🔍 Buscar Conocimiento")
        print("4. 🧠 Análisis con DSPy")
        print("5. 🔄 Transfer Learning")
        print("6. ⚡ Optimizar Modelo")
        print("7. 📊 Estadísticas")
        print("8. 🎯 Demo Embat + Rosetta")
        print("9. ℹ️  Ayuda")
        print("0. 🚪 Salir")
    
    def _handle_input(self):
        """Maneja la entrada del usuario"""
        try:
            choice = input("\n👉 Selecciona opción: ").strip()
            
            if choice == '0':
                self._exit()
            elif choice == '1':
                self._select_application()
            elif choice == '2':
                self._select_model()
            elif choice == '3':
                self._search()
            elif choice == '4':
                self._analyze()
            elif choice == '5':
                self._transfer_knowledge()
            elif choice == '6':
                self._optimize_model()
            elif choice == '7':
                self._show_stats()
            elif choice == '8':
                self._demo_embat_rosetta()
            elif choice == '9':
                self._show_help()
            else:
                print("❌ Opción no válida")
                
        except KeyboardInterrupt:
            self._exit()
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _select_application(self):
        """Selecciona aplicación"""
        print("\n📱 APLICACIONES DISPONIBLES:")
        
        # Mostrar aplicaciones descubiertas
        discovered = list(self.platform.app_embeddings.keys())[:10]
        for i, app in enumerate(discovered, 1):
            info = self.platform.app_embeddings[app]
            print(f"{i}. {app}")
            print(f"   Ontology: {info.get('ontology_count', 0)} docs")
            print(f"   Code: {info.get('code_count', 0)} docs")
        
        # Mostrar aplicaciones predefinidas
        print("\nAPLICACIONES PREDEFINIDAS:")
        for i, app in enumerate(Application, len(discovered) + 1):
            print(f"{i}. {app.value} - {app.name}")
        
        choice = input("\n📱 Selecciona aplicación (número o nombre): ").strip()
        
        # Procesar selección
        try:
            idx = int(choice) - 1
            if idx < len(discovered):
                app_id = discovered[idx]
            else:
                app_idx = idx - len(discovered)
                apps = list(Application)
                if app_idx < len(apps):
                    app_id = apps[app_idx].value
                else:
                    app_id = choice
        except:
            app_id = choice
        
        if self.platform.select_application(app_id):
            print(f"✅ Aplicación '{app_id}' seleccionada")
        else:
            print(f"❌ No se pudo seleccionar '{app_id}'")
    
    def _select_model(self):
        """Selecciona modelo LLM"""
        print("\n🤖 MODELOS DISPONIBLES:")
        
        for i, (model, config) in enumerate(MODEL_CONFIGS.items(), 1):
            print(f"\n{i}. {config.name} ({model.value})")
            print(f"   Provider: {config.provider}")
            print(f"   Speed: {config.speed}")
            print(f"   Cost: ${config.cost_per_1k_input}/1k input, ${config.cost_per_1k_output}/1k output")
            print(f"   Best for: {', '.join(config.best_for[:3])}")
        
        choice = input("\n🤖 Selecciona modelo (1-7): ").strip()
        
        model_map = {
            '1': LLMModel.GPT4,
            '2': LLMModel.GPT4_TURBO,
            '3': LLMModel.GPT4_MINI,
            '4': LLMModel.GPT35_TURBO,
            '5': LLMModel.CLAUDE_3_OPUS,
            '6': LLMModel.MISTRAL_LARGE,
            '7': LLMModel.LLAMA_70B
        }
        
        if choice in model_map:
            if self.platform.select_model(model_map[choice]):
                print(f"✅ Modelo seleccionado")
    
    def _search(self):
        """Realiza búsqueda"""
        if not self.platform.current_app:
            print("⚠️ Primero selecciona una aplicación")
            return
        
        query = input("\n🔍 ¿Qué quieres buscar? ").strip()
        if not query:
            return
        
        print("\nModo de búsqueda:")
        print("1. Smart (automático)")
        print("2. Híbrido")
        print("3. Solo Ontología")
        print("4. Solo Código")
        
        mode_choice = input("Modo [1]: ").strip() or '1'
        mode_map = {'1': 'smart', '2': 'hybrid', '3': 'ontology', '4': 'code'}
        mode = mode_map.get(mode_choice, 'smart')
        
        print(f"\n⏳ Buscando en modo {mode}...")
        results = self.platform.search(query, mode=mode, limit=10)
        
        print(f"\n📊 {len(results)} RESULTADOS:")
        for i, r in enumerate(results[:5], 1):
            print(f"\n{i}. [{r.get('type', 'unknown')}] Score: {r.get('score', 0):.3f}")
            print(f"   {r.get('text', '')[:200]}...")
            if 'metadata' in r:
                print(f"   Metadata: {r['metadata']}")
    
    def _analyze(self):
        """Análisis con DSPy"""
        if not self.platform.current_app:
            print("⚠️ Primero selecciona una aplicación")
            return
        
        query = input("\n🧠 ¿Qué quieres analizar? ").strip()
        if not query:
            return
        
        print("\n⏳ Analizando con DSPy...")
        result = self.platform.analyze(query)
        
        print("\n📖 ANÁLISIS:")
        if 'analysis' in result:
            print(result['analysis'])
        
        if 'code_suggestions' in result:
            print("\n💻 SUGERENCIAS DE CÓDIGO:")
            print(result['code_suggestions'])
        
        if 'recommendations' in result:
            print("\n💡 RECOMENDACIONES:")
            print(result['recommendations'])
        
        if 'confidence' in result:
            print(f"\n🎯 Confianza: {result['confidence']}")
    
    def _transfer_knowledge(self):
        """Transfer learning entre aplicaciones"""
        print("\n🔄 TRANSFER LEARNING")
        
        source = input("Aplicación fuente [rosetta_etl]: ").strip() or "rosetta_etl"
        target = input("Aplicación destino [embat_treasury]: ").strip() or "embat_treasury"
        pattern = input("Patrón a transferir: ").strip()
        
        if not pattern:
            print("❌ Debes especificar un patrón")
            return
        
        print(f"\n⏳ Transfiriendo '{pattern}' de {source} a {target}...")
        
        try:
            result = self.platform.transfer_knowledge(source, target, pattern)
            
            print("\n✅ TRANSFERENCIA COMPLETADA:")
            print(f"\n📝 Patrón Adaptado:")
            print(result.get('adapted_pattern', 'N/A'))
            
            if 'code' in result:
                print(f"\n💻 Código:")
                print(result['code'])
            
            if 'strategy' in result:
                print(f"\n🎯 Estrategia:")
                print(result['strategy'])
            
            if 'warnings' in result:
                print(f"\n⚠️ Advertencias:")
                print(result['warnings'])
                
        except Exception as e:
            print(f"❌ Error en transferencia: {e}")
    
    def _optimize_model(self):
        """Optimización de selección de modelo"""
        print("\n⚡ OPTIMIZACIÓN DE MODELO")
        
        task = input("Describe la tarea: ").strip()
        if not task:
            return
        
        print("\nRestricciones (opcional, Enter para saltar):")
        max_cost = input("Costo máximo por 1k tokens: ").strip()
        speed = input("Velocidad (fast/medium/slow): ").strip()
        privacy = input("Requiere privacidad (s/n): ").strip()
        
        constraints = {}
        if max_cost:
            constraints['max_cost'] = float(max_cost)
        if speed:
            constraints['required_speed'] = speed
        if privacy == 's':
            constraints['privacy'] = True
        
        print("\n⏳ Optimizando...")
        result = self.platform.optimize_model_selection(task, constraints)
        
        print(f"\n🎯 MODELO RECOMENDADO:")
        print(result.get('model', 'N/A'))
        
        if 'alternatives' in result:
            print(f"\n🔄 Alternativas:")
            print(result['alternatives'])
        
        if 'config' in result:
            print(f"\n⚙️ Configuración:")
            print(result['config'])
        
        if 'performance' in result:
            print(f"\n📈 Rendimiento esperado:")
            print(result['performance'])
    
    def _show_stats(self):
        """Muestra estadísticas"""
        stats = self.platform.get_platform_stats()
        
        print("\n📊 ESTADÍSTICAS DE LA PLATAFORMA")
        print("="*50)
        
        print(f"\n🆔 Session: {stats['session_id']}")
        print(f"📱 App actual: {stats['current_app']}")
        print(f"🤖 Modelo actual: {stats['current_model']}")
        
        print(f"\n📚 Aplicaciones:")
        print(f"   Total: {stats['applications']['total']}")
        print(f"   Cargadas: {stats['applications']['loaded']}")
        
        print(f"\n🧬 Embeddings:")
        for emb_type, info in stats['embeddings'].items():
            status = "✅" if info['loaded'] else "❌"
            print(f"   {status} {emb_type}: {info['count']} docs, {info['dimension']}d")
        
        print(f"\n📈 Actividad:")
        print(f"   Modelos en cache: {stats['models_cached']}")
        print(f"   Interacciones: {stats['interaction_history']}")
    
    def _demo_embat_rosetta(self):
        """Demo de integración Embat + Rosetta"""
        print("\n🎯 DEMO: INTEGRACIÓN EMBAT + ROSETTA CON DSPY")
        print("="*60)
        
        print("\n1️⃣ Seleccionando Rosetta ETL...")
        self.platform.select_application("rosetta_etl")
        
        print("\n2️⃣ Analizando capacidades de Rosetta...")
        rosetta_analysis = self.platform.analyze("dataFunction apirest authentication")
        print(f"   ✅ Análisis completado")
        
        print("\n3️⃣ Seleccionando Embat Treasury...")
        self.platform.select_application("embat_treasury")
        
        print("\n4️⃣ Analizando requisitos de Embat...")
        embat_analysis = self.platform.analyze("treasury management transactions API")
        print(f"   ✅ Análisis completado")
        
        print("\n5️⃣ Transfiriendo conocimiento de autenticación...")
        transfer = self.platform.transfer_knowledge(
            "rosetta_etl",
            "embat_treasury", 
            "API authentication JWT"
        )
        
        if 'adapted_pattern' in transfer:
            print(f"\n✅ Patrón adaptado:")
            print(transfer['adapted_pattern'][:500])
        
        print("\n6️⃣ Optimizando modelo para producción...")
        optimization = self.platform.optimize_model_selection(
            "Real-time financial transaction categorization",
            {"max_cost": 0.01, "required_speed": "fast"}
        )
        
        print(f"\n🎯 Modelo óptimo: {optimization.get('model', 'GPT-4 Mini')}")
        
        print("\n✅ Demo completada - Integración diseñada con DSPy")
    
    def _show_help(self):
        """Muestra ayuda"""
        print("\n❓ AYUDA - CODESEMIO PLATFORM")
        print("="*60)
        
        print("\n🎯 CONCEPTOS CLAVE:")
        print("\n1. MULTI-APLICACIÓN:")
        print("   - Cada aplicación tiene su propio conocimiento")
        print("   - Puedes transferir patrones entre aplicaciones")
        
        print("\n2. MULTI-MODELO:")
        print("   - Selecciona el modelo LLM según la tarea")
        print("   - Optimización automática de selección")
        
        print("\n3. MULTI-EMBEDDING:")
        print("   - CodeBERT: Sintaxis del código")
        print("   - GraphCodeBERT: Flujo de datos")
        print("   - Ontology: Conocimiento del dominio")
        print("   - Hybrid: Fusión inteligente")
        
        print("\n4. DSPY INTEGRATION:")
        print("   - Análisis semántico profundo")
        print("   - Generación de código")
        print("   - Transfer learning")
        print("   - Optimización automática")
        
        print("\n📚 FLUJO TÍPICO:")
        print("1. Selecciona aplicación")
        print("2. Selecciona modelo (o usa optimización)")
        print("3. Busca o analiza")
        print("4. Transfiere conocimiento si es necesario")
    
    def _exit(self):
        """Sale de la aplicación"""
        print("\n👋 ¡Hasta luego!")
        print(f"📊 Sesión {self.platform.session_id} finalizada")
        self.running = False
        sys.exit(0)


def main():
    """Función principal"""
    try:
        ui = CodeSemioUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()