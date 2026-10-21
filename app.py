import streamlit as st
from google import genai
from google.genai import types

# 1. Configuración de página
st.set_page_config(
    page_title="RML Academy - Rocko", 
    page_icon="🤖", 
    layout="wide"
)

# 2. Estilos CSS Personalizados (Tonos Azul Frío / Pastel / Gris Sobrio)
st.markdown("""
<style>
    /* Estilo general */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    /* Tarjetas de Métricas */
    [data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px;
    }
    [data-testid="stMetricValue"] {
        color: #93c5fd !important;
        font-weight: bold;
    }
    /* Nodos de la Ruta de Aprendizaje (Estilo Duolingo) */
    .node-card {
        background-color: #1e293b;
        border: 2px solid #3b82f6;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    /* Pestañas de Navegación */
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        color: #94a3b8;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #334155 !important;
        color: #60a5fa !important;
        border-bottom: 3px solid #60a5fa !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicializar Estados en Memoria (session_state)
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "racha" not in st.session_state:
    st.session_state.racha = 1
if "problemas_resueltos" not in st.session_state:
    st.session_state.problemas_resueltos = 0
if "misiones" not in st.session_state:
    st.session_state.misiones = [
        {"id": 1, "titulo": "Resolver 1er problema de Ley de Ohm", "recompensa": 50, "completada": False},
        {"id": 2, "titulo": "Alcanzar 100 Stones acumuladas", "recompensa": 50, "completada": False},
        {"id": 3, "titulo": "Completar 3 análisis en la Consola NLP", "recompensa": 100, "completada": False}
    ]

# 4. BARRA LATERAL (SIDEBAR) CON IMAGEN DE ROCKO
col_logo_side, col_title_side = st.sidebar.columns([1, 2])
with col_logo_side:
    st.image("https://i.imgur.com/3Yp7j7j.png", width=65)
with col_title_side:
    st.sidebar.title("🗺️ RML Academy")

col_xp, col_racha = st.sidebar.columns(2)
col_xp.metric("🪨 Stones", f"{st.session_state.xp} pts")
col_racha.metric("🔥 Racha", f"{st.session_state.racha} días")

nivel = (st.session_state.xp // 100) + 1
st.sidebar.caption(f"🏆 Nivel Estudiante: **Nivel {nivel}**")
st.sidebar.divider()

modulo = st.sidebar.selectbox(
    "Módulo de Aprendizaje:",
    [
        "Módulo 1: Circuitos Eléctricos y Electrónica",
        "Módulo 2: CNC y Maquinado de Precisión",
        "Módulo 3: Mecanismos, Robótica y Cinemática",
        "Módulo 4: Procesos Industriales y Termofluidos"
    ]
)

# Misiones en Sidebar
with st.sidebar.expander("🎯 Misiones de la Sesión", expanded=True):
    for m in st.session_state.misiones:
        check = "✅" if m["completada"] else "⬜"
        st.write(f"{check} **{m['titulo']}** (+{m['recompensa']} 🪨)")

st.sidebar.divider()

# Acceso Admin
modo_admin = st.sidebar.checkbox("🔒 Panel Admin")
es_admin = False
if modo_admin:
    clave = st.sidebar.text_input("Clave Admin:", type="password")
    if clave == "8323052011":
        st.sidebar.success("🔑 Autenticado como ADMIN")
        es_admin = True
    elif clave != "":
        st.sidebar.error("❌ Clave incorrecta")

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("API Key Gemini:", type="password")

# 5. ENCABEZADO PRINCIPAL CON LOGO DE ROCKO
col_head_img, col_head_txt = st.columns([1, 5])

with col_head_img:
    st.image("https://i.imgur.com/3Yp7j7j.png", width=100)

with col_head_txt:
    st.title("🤖 Rocko | RML Academy")
    st.caption("Plataforma interactiva de traducción de lenguaje natural a modelos algebraicos.")

# 6. PANEL DE CONTROL ADMIN (GESTIÓN EN TIEMPO REAL)
if modo_admin and es_admin:
    with st.expander("⚙️ PANEL DE CONTROL DE MISIONES Y PARÁMETROS ADMIN", expanded=True):
        st.subheader("🛠️ Gestor Global de Misiones")
        
        with st.form("nueva_mision_form"):
            col_m1, col_m2 = st.columns([3, 1])
            nueva_m_titulo = col_m1.text_input("Título de la nueva misión:")
            nueva_m_pts = col_m2.number_input("Stones 🪨:", value=50, step=25)
            btn_crear_mision = st.form_submit_button("➕ Agregar Misión")
            
            if btn_crear_mision and nueva_m_titulo:
                st.session_state.misiones.append({
                    "id": len(st.session_state.misiones) + 1,
                    "titulo": nueva_m_titulo,
                    "recompensa": nueva_m_pts,
                    "completada": False
                })
                st.toast("¡Nueva misión agregada con éxito!", icon="🎯")
                st.rerun()

        col_adm1, col_adm2 = st.columns(2)
        if col_adm1.button("🎁 Otorgar +100 Stones 🪨"):
            st.session_state.xp += 100
            st.toast("Bonificación aplicada.")
            st.rerun()
        if col_adm2.button("🔴 Resetear Datos de Sesión"):
            st.session_state.xp = 0
            st.session_state.problemas_resueltos = 0
            for m in st.session_state.misiones:
                m["completada"] = False
            st.rerun()
    st.divider()

# 7. ESTRUCTURA EN PESTAÑAS
tab_ruta, tab_consola, tab_reporte = st.tabs(["🗺️ Ruta de Aprendizaje", "💬 Consola Rocko NLP", "📊 Diagnóstico Técnico"])

# PESTAÑA 1: RUTA DE APRENDIZAJE
with tab_ruta:
    st.subheader(f"Ruta Interactiva: {modulo}")
    st.write("Selecciona un nodo de la ruta para cargar el caso de estudio correspondiente:")
    
    col_n1, col_n2, col_n3 = st.columns(3)
    
    with col_n1:
        st.markdown("""
        <div class="node-card">
            <h4>⚡ Nodo 1: Ley de Ohm</h4>
            <p><small>Análisis de voltaje, corriente y resistencia en serie.</small></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Cargar Caso 1 en Consola"):
            st.session_state.prompt_cargado = "Tengo un circuito en serie con V=24V, R1=100 y R2=200 ohms. Calcula I total y V2."
            st.success("Caso cargado. Ve a la pestaña 'Consola Rocko NLP'.")

    with col_n2:
        st.markdown("""
        <div class="node-card">
            <h4>⚙️ Nodo 2: Velocidad CNC</h4>
            <p><small>Cálculo de velocidad de corte Vc y RPM del husillo.</small></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Cargar Caso 2 en Consola"):
            st.session_state.prompt_cargado = "Calcula la velocidad de corte Vc para un maquinado con diámetro D=50mm a N=1200 RPM."
            st.success("Caso cargado. Ve a la pestaña 'Consola Rocko NLP'.")

    with col_n3:
        st.markdown("""
        <div class="node-card">
            <h4>🤖 Nodo 3: Cinemática Robot</h4>
            <p><small>Torque en la articulación de un brazo robótico.</small></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Cargar Caso 3 en Consola"):
            st.session_state.prompt_cargado = "Un brazo robótico de 0.5m sostiene una masa de 2kg en el extremo. ¿Cuál es el torque en la articulación?"
            st.success("Caso cargado. Ve a la pestaña 'Consola Rocko NLP'.")

# PESTAÑA 2: CONSOLA ROCKO NLP
with tab_consola:
    if api_key:
        try:
            client = genai.Client(api_key=api_key)

            prompt_sistema = f"""
            Eres Rocko, el motor de inteligencia técnica para RML Academy.
            Módulo activo: **{modulo}**.

            Reglas de respuesta:
            1. Procesa la entrada del usuario como un problema de ingeniería mecatrónica.
            2. Responde estrictamente formateado en las 7 secciones del dossier:
               - 1. Contexto | 2. Datos | 3. Variables | 4. Modelo Matemático | 5. Procedimiento (Árbol de Decisión) | 6. Solución | 7. Interpretación Técnica
            3. Sé conciso, técnico y formal.
            """

            if "mensajes" not in st.session_state:
                st.session_state.mensajes = [
                    {"role": "assistant", "content": f"Consola lista para el **{modulo}**. Selecciona un nodo en la Ruta o escribe un problema directamente."}
                ]

            for msg in st.session_state.mensajes:
                avatar = "🤖" if msg["role"] == "assistant" else "👤"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.write(msg["content"])

            prompt_input = st.chat_input("Escribe o pega tu consulta técnica aquí...")
            prompt_final = prompt_input
            
            if "prompt_cargado" in st.session_state and st.session_state.prompt_cargado:
                prompt_final = st.session_state.prompt_cargado
                st.session_state.prompt_cargado = None  # Consumir prompt

            if prompt_final:
                st.session_state.mensajes.append({"role": "user", "content": prompt_final})
                with st.chat_message("user", avatar="👤"):
                    st.write(prompt_final)

                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Rocko evaluando modelo matemático y árbol de decisión..."):
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=prompt_final,
                            config=types.GenerateContentConfig(system_instruction=prompt_sistema),
                        )
                        st.write(response.text)
                        st.session_state.mensajes.append({"role": "assistant", "content": response.text})
                        
                        # Actualizar métricas y misiones
                        st.session_state.xp += 50
                        st.session_state.problemas_resueltos += 1
                        
                        if st.session_state.problemas_resueltos >= 1:
                            st.session_state.misiones[0]["completada"] = True
                        if st.session_state.xp >= 100:
                            st.session_state.misiones[1]["completada"] = True
                        if st.session_state.problemas_resueltos >= 3:
                            st.session_state.misiones[2]["completada"] = True
                            
                        st.toast("¡+50 Stones 🪨 ganadas!", icon="🪨")
                        if st.session_state.xp % 100 == 0:
                            st.balloons()

        except Exception as e:
            st.error(f"Error de API: {e}")
    else:
        st.warning("⚠️ Configura la `GEMINI_API_KEY` en los Secrets o barra lateral.")

# PESTAÑA 3: DIAGNÓSTICO TÉCNICO
with tab_reporte:
    st.subheader("📊 Diagnóstico del Aprendiz y Registro de Actividad")
    col_r1, col_r2 = st.columns(2)
    col_r1.metric("Casos Analizados", f"{st.session_state.problemas_resueltos}")
    col_r2.metric("Puntuación Total", f"{st.session_state.xp} pts")
    
    st.write("### Avance en Misiones")
    for m in st.session_state.misiones:
        estado = "Completada ✅" if m["completada"] else "Pendiente ⬜"
        st.info(f"**{m['titulo']}** — Estado: `{estado}` — Recompensa: `{m['recompensa']} Stones`")
