import streamlit as st
from google import genai
from google.genai import types

# Configuración de la página
st.set_page_config(
    page_title="Rocko - RML Academy", 
    page_icon="🤖", 
    layout="wide"
)

# Estilos CSS sutiles para mejorar tarjetas y métricas sin alterar tu tema
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-weight: bold;
    }
    .stButton>button {
        border-radius: 8px;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

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
col_xp.metric("🪨 Stones", f"{st.session_state.xp} pts")
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

# Barra de progreso del módulo
progreso_modulo = min((st.session_state.problemas_resueltos / 10), 1.0)
st.sidebar.write("Progreso del Módulo:")
st.sidebar.progress(progreso_modulo)

# --- SISTEMA DINÁMICO DE MISIONES ---
completada_1 = st.session_state.problemas_resueltos >= 1
completada_2 = st.session_state.xp >= 100
completada_3 = st.session_state.problemas_resueltos >= 3

with st.sidebar.expander("🎯 Misiones del Día", expanded=True):
    st.write(f"{'✅' if completada_1 else '⬜'} **Primer Paso:** Resolver 1 problema (+50 Stones)")
    st.write(f"{'✅' if completada_2 else '⬜'} **Aprendiz:** Acumular 100 Stones (+50 Stones)")
    st.write(f"{'✅' if completada_3 else '⬜'} **Maestría:** Resolver 3 problemas (+100 Stones)")

st.sidebar.divider()

# --- MODO ADMINISTRADOR / PROFESOR ---
modo_admin = st.sidebar.checkbox("🔒 Acceso Admin / Profesor")
es_admin_autenticado = False

if modo_admin:
    clave_admin = st.sidebar.text_input("Contraseña Admin:", type="password")
    if clave_admin == "8323052011":
        st.sidebar.success("🔑 Autenticado como Profesor")
        es_admin_autenticado = True
    elif clave_admin != "":
        st.sidebar.error("❌ Contraseña incorrecta")

# Configuración de API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

# --- ENCABEZADO PRINCIPAL ---
st.title("¡Hola! mi nombre es 🤖 Rocko")
st.caption("Puedo ayudarte a comprender más sobre el álgebra, guiándote paso a paso.")

# VISTA EXCLUSIVA DEL PROFESOR (PANEL DE CONTROL)
if modo_admin and es_admin_autenticado:
    st.info("⚙️ **Panel de Administración RML Academy / Métricas del Docente**")
    
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    col_a1.metric("Consultas Totales", f"{st.session_state.problemas_resueltos}")
    col_a2.metric("Stones Totales", f"{st.session_state.xp} pts")
    col_a3.metric("Nivel Alcanzado", f"Nivel {nivel}")
    col_a4.metric("Módulo Activo", modulo.split(':')[0])
    
    st.subheader("🛠️ Controles")
    col_btn1, col_btn2 = st.columns(2)
    
    if col_btn1.button("🔴 Reiniciar Progreso del Estudiante"):
        st.session_state.xp = 0
        st.session_state.problemas_resueltos = 0
        st.success("Progreso reiniciado correctamente.")
        st.rerun()
        
    if col_btn2.button("🎁 Otorgar Bonificación de +100 Stones"):
        st.session_state.xp += 100
        st.toast("¡Bonificación otorgada al estudiante! 🎉", icon="🪨")
        st.rerun()
        
    st.divider()

# --- PRUEBAS RÁPIDAS PARA DEMOSTRACIÓN (1-CLIC) ---
st.markdown("### ⚡ Pruebas Rápidas para la Academia")
st.write("Selecciona una pregunta para hacer una prueba instantánea con Rocko:")

col_demo1, col_demo2, col_demo3 = st.columns(3)
prompt_demo = None

if col_demo1.button("⚡ Ley de Ohm (Módulo 1)"):
    prompt_demo = "Tengo un circuito en serie con una fuente de 24V y dos resistencias de 100 y 200 ohms. Calcula la corriente total y el voltaje en R2."

if col_demo2.button("⚙️ Velocidad CNC (Módulo 2)"):
    prompt_demo = "Calcula la velocidad de corte Vc para un maquinado de precisión con diámetro D=50mm a N=1200 RPM."

if col_demo3.button("🤖 Torque Robot (Módulo 3)"):
    prompt_demo = "Un brazo robótico de 0.5m sostiene una masa de 2kg en el extremo. ¿Cuál es el torque generado en la articulación?"

st.divider()

if api_key:
    try:
        client = genai.Client(api_key=api_key)

        prompt_sistema = f"""
        Eres Rocko, un tutor técnico gamificado estilo Duolingo para RML Academy en Mecatrónica y Electromecánica.
        El usuario está trabajando en el **{modulo}**.

        Tus directrices:
        1. Saluda de forma motivadora y breve.
        2. Analiza el problema del usuario y aplícalo a la metodología de RML Academy.
        3. Explica el procedimiento paso a paso estructurado estrictamente en las 7 secciones:
           - 1. Contexto | 2. Datos | 3. Variables | 4. Modelo Matemático | 5. Procedimiento (Árbol de Decisión) | 6. Solución | 7. Interpretación Técnica
        4. Al final de tu respuesta, dale una palabra de aliento o una pregunta de refuerzo tipo trivia.
        """

        # Historial de Chat
        if "mensajes" not in st.session_state:
            st.session_state.mensajes = [
                {
                    "role": "assistant", 
                    "content": f"¡Bienvenido a la academia! 🚀 Estoy listo para ayudarte con el **{modulo}**. Envía tu primer problema o usa una prueba rápida para ganar +50 Stones."
                }
            ]

        for msg in st.session_state.mensajes:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

        # Detectar entrada (si viene de la caja de texto o de un botón de demo)
        prompt_input = st.chat_input("Escribe aquí tu problema o consulta...")
        prompt = prompt_demo if prompt_demo else prompt_input

        if prompt:
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
                        
                        # Si alcanza un hito de 100 pts, lanza globos festivos
                        if st.session_state.xp % 100 == 0:
                            st.balloons()

                    except Exception as err:
                        st.error(f"Error al procesar la respuesta: {err}")

    except Exception as e:
        st.error(f"Error con la API Key de Gemini: {e}")
else:
    st.warning("⚠️ Configura la `GEMINI_API_KEY` en los Secrets de Streamlit Cloud.")
