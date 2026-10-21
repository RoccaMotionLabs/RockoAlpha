import streamlit as st
from google import genai
from google.genai import types

# Configuración de la página
st.set_page_config(
    page_title="Rocko - RML Academy", 
    page_icon="🤖", 
    layout="wide"
)

# --- INICIALIZAR GAMIFICACIÓN EN SESSION_STATE ---
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "racha" not in st.session_state:
    st.session_state.racha = 1
if "problemas_resueltos" not in st.session_state:
    st.session_state.problemas_resueltos = 0

# --- BARRA LATERAL TIPO DUOLINGO ---
st.sidebar.image("https://img.icons8.com/color/96/robot-2.png", width=80)
st.sidebar.title("🗺️ RML Academy")

# Panel de Estadísticas
col_xp, col_racha = st.sidebar.columns(2)
col_xp.metric("🪨 Stones Ganadas", f"{st.session_state.xp} pts")
col_racha.metric("🔥 Racha", f"{st.session_state.racha} días")

# Nivel del Usuario según XP
nivel = (st.session_state.xp // 100) + 1
st.sidebar.caption(f"🏆 Nivel del Estudiante: **Nivel {nivel}**")

st.sidebar.divider()

# Selección de Módulo con Barra de Progreso
modulo = st.sidebar.selectbox(
    "Elige tu Módulo de Aprendizaje:",
    [
        "Módulo 1: Circuitos Eléctricos y Electrónica",
        "Módulo 2: CNC y Maquinado de Precisión",
        "Módulo 3: Mecanismos, Robótica y Cinemática",
        "Módulo 4: Procesos Industriales, Taller y Termofluidos"
    ]
)

# Barra de progreso del dossier (Simulando avance)
progreso_modulo = min((st.session_state.problemas_resueltos / 10), 1.0)
st.sidebar.write("Progreso del Módulo:")
st.sidebar.progress(progreso_modulo)

# Desafío Activo
with st.sidebar.expander("🎯 Misión Activa"):
    st.write("• Resuelve 1 problema del dossier RML-01 para ganar +50 XP.")

# --- ENCABEZADO PRINCIPAL ---
st.title("¡Hola! mi nombre es 🤖 Rocko ")
st.caption("Puedo ayudarte a comprender más sobre el álgebra, guíandote paso a paso.")

# Configuración de API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

if api_key:
    try:
        client = genai.Client(api_key=api_key)

        prompt_sistema = f"""
        Eres Rocko, un tutor técnico gamificado estilo Duolingo para el dossier RML-01 de Mecatrónica.
        El usuario está trabajando en el **{modulo}**.

        Tus directrices:
        1. Saluda de forma motivadora y breve.
        2. Analiza el problema del usuario y aplícalo al dossier RML-01.
        3. Explica el procedimiento paso a paso estructurado en las 7 secciones del dossier:
           - 1. Contexto | 2. Datos | 3. Variables | 4. Modelo Matemático | 5. Procedimiento (Árbol de Decisión) | 6. Solución | 7. Interpretación Técnica
        4. Al final de tu respuesta, dale una palabra de aliento o una pregunta de refuerzo tipo trivia.
        """

        # Historial de Chat
        if "mensajes" not in st.session_state:
            st.session_state.mensajes = [
                {
                    "role": "assistant", 
                    "content": f"¡Bienvenido a la academia! 🚀 Estoy listo para ayudarte con el **{modulo}**. Envía tu primer problema para ganar +50 XP."
                }
            ]

        for msg in st.session_state.mensajes:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

        # Entrada de Texto
        if prompt := st.chat_input("Escribe aquí tu problema del dossier o consulta..."):
            st.session_state.mensajes.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.write(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Rocko está evaluando tu respuesta y calculando las ecuaciones..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=prompt_sistema,
                            ),
                        )
                        st.write(response.text)
                        st.session_state.mensajes.append({"role": "assistant", "content": response.text})

                        # AUMENTAR GAMIFICACIÓN AL RESPONDER
                        st.session_state.xp += 50
                        st.session_state.problemas_resueltos += 1
                        st.toast("¡+50 Stones Ganadas! 🎉", icon="🪨")
                        
                        # Si alcanza un hito, lanza globos festivos en la pantalla
                        if st.session_state.xp % 100 == 0:
                            st.balloons()

                    except Exception as err:
                        st.error(f"Error al procesar la respuesta: {err}")

    except Exception as e:
        st.error(f"Error con la API Key de Gemini: {e}")
else:
    st.warning("⚠️ Configura la `GEMINI_API_KEY` en los Secrets de Streamlit Cloud.")
