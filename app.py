import streamlit as st
from google import genai
from google.genai import types

# Configuración de la página
st.set_page_config(
    page_title="Rocko - MDOSS", 
    page_icon="🤖", 
    layout="wide"
)

# Encabezado principal
st.title("🤖 Rocko | MDOSS")
st.caption("Álgebra Aplicada para Mecatrónica y Electromecánica")

# Menú lateral
st.sidebar.image("https://img.icons8.com/color/96/robot-2.png", width=80)
st.sidebar.title("Configuración")

modulo = st.sidebar.selectbox(
    "Selecciona el Módulo de Trabajo:",
    [
        "Módulo 1: Circuitos Eléctricos y Electrónica",
        "Módulo 2: CNC y Maquinado de Precisión",
        "Módulo 3: Mecanismos, Robótica y Cinemática",
        "Módulo 4: Procesos Industriales, Taller y Termofluidos"
    ]
)

# Obtener API Key de Secrets o Sidebar
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

if api_key:
    try:
        # Inicializar el cliente oficial moderno
        client = genai.Client(api_key=api_key)

        st.sidebar.success(f"Módulo: {modulo.split(':')[0]}")
        st.sidebar.info("Modelo activo: `gemini-3.8-flash`")

        # Prompt de sistema para Rocko
        prompt_sistema = f"""
        Eres Rocko, el asistente técnico oficial con IA para el dossier RML-01 de Mecatrónica y Electromecánica.
        El usuario está trabajando actualmente en el **{modulo}**.

        Tus directrices de actuación:
        1. Preséntate cordialmente si es la primera interacción, pero mantén un enfoque técnico, profesional y preciso.
        2. Analiza la consulta en lenguaje natural del usuario e identifícala dentro de los 40 problemas del dossier RML-01.
        3. Extrae claramente las variables numéricas y datos entregados.
        4. Aplica el modelo matemático y el árbol de decisión correspondiente evaluando las condiciones lógicas.
        5. Responde de forma estructurada siguiendo ESTRICTAMENTE estas 7 secciones:
           - 1. Contexto
           - 2. Datos
           - 3. Variables
           - 4. Modelo Matemático
           - 5. Procedimiento (Árbol de Decisión / Algoritmo)
           - 6. Solución
           - 7. Interpretación Técnica
        6. Si el problema carece de datos suficientes, indícale al usuario qué variables específicas hacen falta.
        """

        # Historial de chat
        if "mensajes" not in st.session_state:
            st.session_state.mensajes = [
                {
                    "role": "assistant", 
                    "content": f"¡Hola! Soy **Rocko**, tu asistente técnico para el dossier RML-01. Estamos listos para el **{modulo}**. ¿En qué problema te ayudo?"
                }
            ]

        for msg in st.session_state.mensajes:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

        # Entrada del usuario
        if prompt := st.chat_input("Escribe tu problema o consulta técnica aquí..."):
            st.session_state.mensajes.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.write(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Rocko está analizando el problema y evaluando las ecuaciones..."):
                    try:
                        # Generar contenido usando la API moderna de Google
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=prompt_sistema,
                            ),
                        )
                        st.write(response.text)
                        st.session_state.mensajes.append({"role": "assistant", "content": response.text})
                    except Exception as err:
                        st.error(f"Error al procesar la respuesta: {err}")

    except Exception as e:
        st.error(f"Error con la API Key de Gemini: {e}")

else:
    st.warning("⚠️ Por favor, configura la `GEMINI_API_KEY` en los Secrets de Streamlit Cloud para iniciar a Rocko.")
