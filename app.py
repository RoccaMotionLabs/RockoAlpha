import streamlit as st
import google.generativeai as genai

# Configuración visual de la página
st.set_page_config(
    page_title="Rocko - MDOSS", 
    page_icon="🤖", 
    layout="wide"
)

# Encabezado principal
st.title("🤖 Rocko esta para ti!")
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

# Clave de API
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)

        # Nombre del modelo activo para plan gratuito
        nombre_modelo = "gemini-2.0-flash"

        st.sidebar.success(f"Módulo: {modulo.split(':')[0]}")
        st.sidebar.info(f"Modelo activo: `{nombre_modelo}`")

        # Instrucciones base para Rocko
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

        # Inicialización de Rocko
        modelo = genai.GenerativeModel(
            model_name=nombre_modelo,
            system_instruction=prompt_sistema
        )

        # Historial de conversación
        if "mensajes" not in st.session_state:
            st.session_state.mensajes = [
                {
                    "role": "assistant", 
                    "content": f"¡Hola! Soy **Rocko**, tu asistente técnico para el dossier RML-01. Actualmente estamos listos para trabajar en el **{modulo}**. ¿En qué problema o consulta te puedo ayudar?"
                }
            ]

        for msg in st.session_state.mensajes:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

        if prompt := st.chat_input("Escribe tu problema o consulta técnica aquí..."):
            st.session_state.mensajes.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.write(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Rocko está analizando el problema y evaluando las ecuaciones..."):
                    try:
                        response = modelo.generate_content(prompt)
                        st.write(response.text)
                        st.session_state.mensajes.append({"role": "assistant", "content": response.text})
                    except Exception as err:
                        st.error(f"Error al procesar la respuesta: {err}")

    except Exception as e:
        st.error(f"Error de conexión con la API Key de Gemini: {e}")

else:
    st.warning("⚠️ Por favor, configura la `GEMINI_API_KEY` en los Secrets de Streamlit Cloud para iniciar a Rocko.")
