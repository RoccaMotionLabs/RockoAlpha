import streamlit as st
import google.generativeai as genai

# Configuración visual de la página
st.set_page_config(page_title="Asistente RML-01", page_icon="⚙️", layout="wide")

st.title("⚙️ Asistente Interactivo Dossier RML-01")
st.caption("Álgebra Aplicada para Mecatrónica y Electromecánica")

# Menú lateral para organizar los 4 módulos
modulo = st.sidebar.selectbox(
    "Selecciona el Módulo de Trabajo:",
    [
        "Módulo 1: Circuitos Eléctricos y Electrónica",
        "Módulo 2: CNC y Maquinado de Precisión",
        "Módulo 3: Mecanismos, Robótica y Cinemática",
        "Módulo 4: Procesos Industriales, Taller y Termofluidos"
    ]
)

st.sidebar.success(f"Módulo activo: {modulo}")

# Configuración del motor de Inteligencia Artificial (Gemini)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.text_input("Ingresa tu API Key de Gemini:", type="password")

if api_key:
    genai.configure(api_key=api_key)

    # Instrucciones base del sistema (System Prompt)
    prompt_sistema = f"""
    Eres el asistente técnico oficial del proyecto RML-01 de Mecatrónica.
    El usuario está consultando sobre el **{modulo}**.

    Instrucciones de actuación:
    1. Lee la consulta del usuario expuesta en palabras/lenguaje natural.
    2. Identifica a cuál de los 40 problemas del dossier corresponde.
    3. Extrae las variables numéricas entregadas.
    4. Aplica el árbol de decisión correspondiente evaluando las condiciones lógicas.
    5. Responde estrictamente con la estructura de 7 secciones del dossier:
       - 1. Contexto
       - 2. Datos
       - 3. Variables
       - 4. Modelo Matemático
       - 5. Procedimiento (Árbol de Decisión / Algoritmo)
       - 6. Solución
       - 7. Interpretación Técnica
    6. Mantén un tono técnico, claro y profesional.
    """

    modelo = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=prompt_sistema
    )

    # Historial de conversación
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Entrada de texto del usuario
    if prompt := st.chat_input("Escribe tu problema o consulta técnica en lenguaje natural..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Procesando consulta y evaluando árbol de decisiones..."):
                response = modelo.generate_content(prompt)
                st.write(response.text)

        st.session_state.mensajes.append({"role": "assistant", "content": response.text})
else:
    st.warning("Por favor, ingresa tu API Key de Gemini para activar el asistente.")
