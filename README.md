# Telegram Chat Analyzer

Aplicación de escritorio para analizar chats exportados de Telegram con IA.

## ✨ Características

- **📥 Importa chats HTML** exportados de Telegram
- **🤖 Análisis con IA** (Gemini o OpenAI) para extraer:
  - Tareas pendientes y completadas
  - Perfiles de personas con roles detectados
  - Habilidades y puntuaciones
  - Patrones de comunicación
- **👤 Mi Perfil** - Evaluación personal con comparativas
- **🔄 Auto-actualización** desde GitHub
- **💾 Base de datos local** SQLite

## 🚀 Instalación Rápida

### Opción 1: Ejecutar con Python (Recomendado para desarrollo)

```bash
# Clonar repositorio
git clone https://github.com/Freskan23/TelegramChatAnalyzer.git
cd TelegramChatAnalyzer

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python TelegramChatAnalyzer.py
```

### Opción 2: Crear ejecutable .exe

```bash
# Después de instalar dependencias
pip install pyinstaller

pyinstaller --name=TelegramChatAnalyzer --onefile --windowed --clean --noconfirm --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=sqlite3 --hidden-import=bs4 --hidden-import=lxml --hidden-import=google.genai --hidden-import=openai TelegramChatAnalyzer.py
```

El ejecutable estará en `dist/TelegramChatAnalyzer.exe`

## 📋 Uso

1. **Exporta tu chat de Telegram:**
   - Abre Telegram Desktop
   - Ve al chat que quieres exportar
   - Menú ⋮ → Exportar historial de chat
   - Selecciona formato HTML

2. **Configura la IA:**
   - Ve a ⚙️ Configuración
   - Añade tu API Key de Gemini (gratis en ai.google.dev)

3. **Importa y analiza:**
   - Clic en "Importar Chat"
   - Selecciona el archivo HTML
   - Confirma el análisis con IA

## 🔄 Actualizaciones

La aplicación incluye un sistema de auto-actualización:

1. Ve a ⚙️ Configuración
2. Clic en "🔍 Buscar actualizaciones"
3. Si hay una nueva versión, clic en "⬇️ Descargar e instalar"
4. Reinicia la aplicación

## 📁 Estructura

```
TelegramChatAnalyzer/
├── TelegramChatAnalyzer.py  # Aplicación principal
├── requirements.txt          # Dependencias
├── VERSION                   # Versión actual
└── README.md                 # Este archivo
```

## 🛠️ Requisitos

- Python 3.10+
- PyQt6
- beautifulsoup4
- google-genai (para Gemini)
- openai (opcional)

## 📄 Licencia

MIT License
