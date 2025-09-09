# 🧠 CodeSemio Platform - Sistema de Inteligencia de Código Multi-Aplicación

## 🚀 Instalación Rápida

```bash
# 1. Clonar o copiar esta carpeta
cd /Users/javiergimeno/entornos/DSPy/demo_dspy/CODESEMIO_PLATFORM

# 2. Activar entorno virtual
source ../venv_dspy/bin/activate

# 3. Instalar dependencias (si no están)
pip install pymongo dspy-ai python-dotenv numpy scikit-learn

# 4. Ejecutar la plataforma
python src/main.py
```

## 📁 Estructura del Proyecto

```
CODESEMIO_PLATFORM/
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias
├── .env.example                # Plantilla de configuración
│
├── src/                        # Código fuente principal
│   ├── __init__.py
│   ├── main.py                # Punto de entrada
│   ├── platform.py            # Core de CodeSemio
│   ├── models.py              # Configuración de modelos
│   ├── embeddings.py          # Gestión de embeddings
│   ├── dspy_modules.py        # Módulos DSPy
│   └── mongodb_client.py      # Cliente MongoDB Atlas
│
├── examples/                   # Ejemplos de uso
│   ├── rosetta_integration.py # Integración con Rosetta
│   ├── embat_integration.py   # Integración con Embat
│   └── cross_app_transfer.py  # Transfer learning
│
├── docs/                       # Documentación
│   ├── ARCHITECTURE.md        # Arquitectura técnica
│   ├── API.md                 # Documentación API
│   └── EMBEDDINGS_STRATEGY.md # Estrategia de embeddings
│
└── config/                     # Configuraciones
    ├── models.json            # Configuración de modelos LLM
    └── applications.json      # Aplicaciones registradas
```

## 🎯 Características Principales

### 1. **Multi-Aplicación** 
- Gestión de múltiples aplicaciones con `application_id`
- Aislamiento de conocimiento por aplicación
- Transfer learning entre aplicaciones

### 2. **Multi-Modelo LLM**
- Soporte para GPT-4, Claude, Llama, Mistral
- Selección dinámica según la tarea
- Optimización costo/rendimiento

### 3. **Multi-Embedding**
- CodeBERT para sintaxis
- GraphCodeBERT para flujo de datos
- Ontología vectorizada para dominio
- Embeddings híbridos

### 4. **DSPy Integration**
- Módulos declarativos para reasoning
- Optimización automática de prompts
- Chain of Thought para análisis complejos

## 🔧 Configuración

Crear archivo `.env` con:

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=analisis_semantico

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (opcional)
ANTHROPIC_API_KEY=sk-ant-...
```

## 📊 Uso Básico

```python
from src.platform import CodeSemioPlatform

# Inicializar plataforma
platform = CodeSemioPlatform()

# Seleccionar aplicación
platform.select_application("rosetta_etl")

# Seleccionar modelo
platform.select_model("gpt-4")

# Buscar conocimiento
results = platform.search("¿Cómo procesar CSV?")

# Transfer learning
platform.transfer_knowledge(
    source_app="rosetta_etl",
    target_app="embat_treasury",
    pattern="authentication"
)
```

## 🤝 Integración con DSPy

CodeSemio usa DSPy para:
- Análisis semántico inteligente
- Generación de código adaptativo
- Optimización de búsquedas
- Transfer learning automático

## 📈 Casos de Uso

1. **Rosetta ETL**: Mapeo automático de esquemas
2. **Embat Treasury**: Categorización de transacciones
3. **Cross-Application**: Reutilización de patrones

## 🛠️ Desarrollo

Para añadir una nueva aplicación:

1. Registrar en `config/applications.json`
2. Indexar sus embeddings en MongoDB
3. Configurar módulos DSPy específicos

## 📝 Licencia

Propietario - CodeSemio Platform 2024

## 👥 Contacto

Javier Gimeno - [Tu Email]

---

**"El futuro no es hacer software más rápido. Es hacer software que se entiende a sí mismo."**