import streamlit as st
from google import genai
from google.genai import types

# Configuración visual de la página
st.set_page_config(
    page_title="Rocko - RML Academy", 
    page_icon="🤖", 
    layout="wide"
)

# Estilos CSS personalizados para tarjetas, métricas y pestañas
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-weight: bold;
        color: #ff4b4b;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1e222d;
        border-radius: 8px 8px 0px 0px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e364f;
        border-bottom: 3px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAR MEMORIA DE SESIÓN (SESSION_STATE) ---
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "racha" not in st.session_state:
    st.session_state.racha = 1
if "problemas_resueltos" not in st.session_state:
    st.session_state.problemas_resueltos = 0
if "modo_rocko" not in st.session_state:
    st.session_state.modo_rocko = "Tutor Explicativo"
if "mision_extra_desbloqueada" not in st.session_state:
    st.session_state.mision_extra_desbloqueada = False

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("https://img.icons8.com/color/96/robot-2.png", width=80)
st.sidebar.title("🗺️ RML Academy")

# Panel de Estadísticas
col_xp, col_racha = st.sidebar.columns(2)
col_xp.metric("🪨 Stones", f"{st.session_state.xp} pts")
col_racha.metric("🔥 Racha", f"{st.session_state.racha} días")

nivel = (st.session_state.xp // 100) + 1
st.sidebar.caption(f"🏆 Estudiante: **Nivel {nivel}**")

st.sidebar.divider()

# Módulo de Aprendizaje
modulo = st.sidebar.selectbox(
    "Elige tu Módulo de Aprendizaje:",
    [
        "Módulo 1: Circuitos Eléctricos y Electrónica",
        "Módulo 2: CNC y Maquinado de Precisión",
        "Módulo 3: Mecanismos, Robótica y Cinemática",
        "Módulo 4: Procesos Industriales, Taller y Termofluidos"
    ]
)

# Progreso
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
    if st.session_state.mision_extra_desbloqueada:
        st.write("🌟 **Misión Especial Admin:** Desbloqueada (+150 Stones)")

st.sidebar.divider()

# --- PANEL DE CONTROL ADMIN ---
modo_admin = st.sidebar.checkbox("🔒 Acceso Admin")
es_admin_autenticado = False

if modo_admin:
    clave_admin = st.sidebar.text_input("Contraseña Admin:", type="password")
    if clave_admin == "8323052011":
        st.sidebar.success("🔑 Autenticado como ADMIN")
        es_admin_autenticado = True
    elif clave_admin != "":
        st.sidebar.error("❌ Contraseña incorrecta")

# Configuración de API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

# --- VISTA PRINCIPAL CON ESTRUCTURA MODULAR (PESTAÑAS) ---
st.title("¡Hola! mi nombre es 🤖 Rocko")
st.caption("Puedo ayudarte a comprender más sobre el álgebra, guiándote paso a paso.")

# VISTA DEL ADMIN DASHBOARD (SI SE AUTENTICA)
if modo_admin and es_admin_autenticado:
    with st.expander("⚙️ PANEL DE CONTROL ADMIN (GESTIÓN DE SESIÓN)", expanded=True):
        st.write("Ajusta los parámetros y reglas de la sesión activa en tiempo real:")
        
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        col_a1.metric("Consultas Totales", f"{st.session_state.problemas_resueltos}")
        col_a2.metric("Stones Totales", f"{st.session_state.xp} pts")
        col_a3.metric("Nivel Sesión", f"Nivel {nivel}")
        col_a4.metric("Modo IA", st.session_state.modo_rocko)
        
        st.subheader("🛠️ Modificadores de Sesión")
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
        
        with col_ctrl1:
            monto_stones = st.number_input("Modificar Stones (+/-):", value=50, step=25)
            if st.button("Aplicar Ajuste de Stones"):
                st.session_state.xp = max(0, st.session_state.xp + monto_stones)
                st.toast(f"Stones ajustadas en {monto_stones} pts.", icon="🪨")
                st.rerun()
                
        with col_ctrl2:
            st.session_state.modo_rocko = st.selectbox(
                "Comportamiento de Rocko:",
                ["Tutor Explicativo", "Examen Rápido (Conciso)", "Modo Desafío Avanzado"]
            )
            
        with col_ctrl3:
            if st.button("🔓 Activar Misión Especial"):
                st.session_state.mision_extra_desbloqueada = True
                st.toast("¡Misión especial activada en la sesión!", icon="🌟")
                st.rerun()
                
            if st.button("🔴 Reiniciar Datos de Sesión"):
                st.session_state.xp = 0
                st.session_state.problemas_resueltos = 0
                st.session_state.mision_extra_desbloqueada = False
                st.rerun()
    st.divider()

# --- PESTAÑAS PRINCIPALES DE LA APLICACIÓN ---
tab_academy, tab_chat, tab_perfil = st.tabs(["🗺️ Centro de Aprendizaje", "💬 Consola Rocko NLP", "📊 Expediente de Avance"])

with tab_academy:
    st.subheader(f"Módulo Activo: {modulo}")
    st.info("Selecciona un tema de estudio o redacta tu consulta en la Consola NLP para ser guiado paso a paso por el modelo algebraico.")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("""
        ### 📌 Estructura de Resolución (7 Secciones)
        1. **Contexto:** Definición del marco del problema.
        2. **Datos:** Extraídos del enunciado.
        3. **Variables:** Identificación algebraica.
        4. **Modelo Matemático:** Formulación y ecuaciones.
        5. **Procedimiento:** Evaluación del Árbol de Decisión.
        6. **Solución:** Cómputo y resultado.
        7. **Interpretación Técnica:** Explicación ingenieril.
        """)
    with col_info2:
        st.markdown(f"""
        ### ⚙️ Configuración Actual
        * **Modo de Operación:** `{st.session_state.modo_rocko}`
        * **Nivel de Usuario:** `Nivel {nivel}`
        * **Stones Acumuladas:** `{st.session_state.xp} pts`
        """)

with tab_chat:
    if api_key:
        try:
            client = genai.Client(api_key=api_key)

            prompt_sistema = f"""
            Eres Rocko, un tutor técnico gamificado para RML Academy en Mecatrónica y Electromecánica.
            El usuario está trabajando en el **{modulo}**.
            Modo de operación actual solicitado por el sistema: **{st.session_state.modo_rocko}**.

            Tus directrices de actuación:
            1. Saluda de forma motivadora y breve.
            2. Mapea la consulta del usuario hacia el modelo algebraico del módulo.
            3. Estructura tu respuesta estrictamente en las 7 secciones:
               - 1. Contexto | 2. Datos | 3. Variables | 4. Modelo Matemático | 5. Procedimiento (Árbol de Decisión) | 6. Solución | 7. Interpretación Técnica
            4. Mantén una comunicación profesional y ajustada al modo de operación activo.
            """

            # Historial de Chat
            if "mensajes" not in st.session_state:
                st.session_state.mensajes = [
                    {
                        "role": "assistant", 
                        "content": f"¡Bienvenido a la consola! 🚀 Estoy listo para ayudarte con el **{modulo}** (Modo: {st.session_state.modo_rocko}). Escribe tu consulta para ganar +50 Stones."
                    }
                ]

            for msg in st.session_state.mensajes:
                avatar = "🤖" if msg["role"] == "assistant" else "👤"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.write(msg["content"])

            # Entrada de Texto
            if prompt := st.chat_input("Escribe aquí tu problema o consulta técnica..."):
                st.session_state.mensajes.append({"role": "user", "content": prompt})
                with st.chat_message("user", avatar="👤"):
                    st.write(prompt)

                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Rocko está evaluando tu respuesta y procesando las ecuaciones..."):
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

                            # AUMENTAR GAMIFICACIÓN
                            st.session_state.xp += 50
                            st.session_state.problemas_resueltos += 1
                            st.toast("¡+50 Stones Ganadas! 🎉", icon="🪨")
                            
                            if st.session_state.xp % 100 == 0:
                                st.balloons()

                        except Exception as err:
                            st.error(f"Error al procesar la respuesta: {err}")

        except Exception as e:
            st.error(f"Error con la API Key de Gemini: {e}")
    else:
        st.warning("⚠️ Configura la `GEMINI_API_KEY` en los Secrets de Streamlit Cloud.")

with tab_perfil:
    st.subheader("📊 Resumen de Rendimiento del Estudiante")
    col_p1, col_p2 = st.columns(2)
    col_p1.metric("Puntos Totales (Stones)", f"{st.session_state.xp}")
    col_p2.metric("Problemas Analizados", f"{st.session_state.problemas_resueltos}")
    
    st.write("### Logros de la Sesión")
    if st.session_state.problemas_resueltos > 0:
        st.success("🥇 **Primer Problema Resuelto:** Has iniciado la traducción de lenguaje natural a álgebra.")
    if st.session_state.xp >= 100:
        st.success("🌟 **Nivel 2 Alcanzado:** Dominio de conceptos básicos.")
    if st.session_state.mision_extra_desbloqueada:
        st.info("⚡ **Reconocimiento Admin:** Se ha otorgado una misión especial a este perfil.")
