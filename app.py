import streamlit as st
import random
import time
from google import genai
from google.genai import types

ROCKO_IMAGE_URL = "https://i.postimg.cc/yxGVScWZ/imagen.png"

# 1. Configuración de la página
st.set_page_config(
    page_title="RML Academy - Rocko", 
    page_icon="🤖", 
    layout="wide"
)

# 2. Estilos CSS Personalizados
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
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
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 20px;
        z-index: 99;
    }
</style>
""", unsafe_allow_html=True)

# 3. BANCO DE MENSAJES LOCALES (0 TOKENS)
BIENVENIDAS_ROCKO = [
    "¡Cascos puestos y multímetros listos! ⚡ Bienvenido al laboratorio. ¿En qué circuito o mecanismo trabajaremos hoy?",
    "¡Hola, colega! ⚙️ Listo el motor de cálculo algebraico. Revisa tus misiones activas o escribe tu problema.",
    "¡Atención en el taller! 🤖 Soy Rocko. Vamos a traducir tus consultas de ingeniería a modelos matemáticos paso a paso.",
    "¡Excelente día para calcular! 🪨 Recuerda que cada misión completada te otorga Stones para subir de rango."
]

MENSAJES_REINTENTO_RED = [
    "📡 **Interferencia en la señal:** La red del laboratorio está experimentando un micro-corte. Reintentando enlace en breve...",
    "⚡ **Carga de procesamiento elevada:** Los servidores de cálculo están saturados momentáneamente. Reintentando solicitud...",
    "🔧 **Ajuste de frecuencia:** Ocurrió un retraso en el enlace del motor NLP. Reintentando conexión..."
]

MENSAJES_TOAST_EXITO = [
    "¡Cálculo preciso! +50 Stones a tu expediente 🪨",
    "¡Demostración impecable! Avanzas en la racha 🪨",
    "¡Ecuaciones validadas con éxito! 🪨",
    "¡Modelo algebraico resuelto sin fallas! 🪨"
]

# 4. INICIALIZACIÓN DE SISTEMA DE MISIONES 2.0 EN MEMORIA
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "racha" not in st.session_state:
    st.session_state.racha = 1
if "problemas_resueltos" not in st.session_state:
    st.session_state.problemas_resueltos = 0

# Estructura enriquecida de misiones (con categoría y palabras clave de validación)
if "misiones" not in st.session_state:
    st.session_state.misiones = [
        {
            "id": 1, 
            "titulo": "Análisis de Ley de Ohm", 
            "desc": "Resuelve un problema de voltaje, corriente o resistencia.",
            "recompensa": 50, 
            "completada": False,
            "keywords": ["ohm", "resistencia", "voltaje", "corriente", "circuito", "v=", "i=", "r="]
        },
        {
            "id": 2, 
            "titulo": "Maquinado CNC o Cinemática", 
            "desc": "Calcula velocidad de corte Vc, RPM o torque en brazo robótico.",
            "recompensa": 75, 
            "completada": False,
            "keywords": ["cnc", "velocidad", "corte", "rpm", "torque", "robot", "brazo", "cinematica"]
        },
        {
            "id": 3, 
            "titulo": "Maestría de Laboratorio (150 Stones)", 
            "desc": "Acumula 150 Stones en tu expediente de laboratorio.",
            "recompensa": 100, 
            "completada": False,
            "keywords": [] # Se valida por puntaje
        }
    ]

# 5. BARRA LATERAL (SIDEBAR) CON FOTO DE ROCKO
col_logo_side, col_title_side = st.sidebar.columns([1, 2])
with col_logo_side:
    st.image(ROCKO_IMAGE_URL, width=65)
with col_title_side:
    st.sidebar.title("RML Academy")

col_xp, col_racha = st.sidebar.columns(2)
col_xp.metric("🪨 Stones", f"{st.session_state.xp} pts")
col_racha.metric("🔥 Racha", f"{st.session_state.racha} días")

nivel = (st.session_state.xp // 100) + 1
st.sidebar.caption(f"🏆 Rango Académico: **Ingeniero Nivel {nivel}**")
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

# Modalidad de respuesta pedagógica
modo_tutoria = st.sidebar.radio(
    "Estilo de Tutoría:",
    ["Explicación Completa (7 Secciones)", "Guía Paso a Paso (Modo Socrático)"]
)

# VISUALIZACIÓN MEJORADA DE MISIONES 2.0
with st.sidebar.expander("🎯 MISIONES Y DESAFÍOS ACTIVOS", expanded=True):
    for m in st.session_state.misiones:
        if m["completada"]:
            st.markdown(f"✅ **{m['titulo']}**  \n<small>🎉 Completada (+{m['recompensa']} 🪨)</small>", unsafe_allow_html=True)
        else:
            st.markdown(f"⬜ **{m['titulo']}** (+{m['recompensa']} 🪨)  \n<small>{m['desc']}</small>", unsafe_allow_html=True)
        st.write("---")

st.sidebar.divider()

# Panel Admin
modo_admin = st.sidebar.checkbox("🔒 Panel Admin")
es_admin = False
if modo_admin:
    clave = st.sidebar.text_input("Clave Admin:", type="password")
    if clave == "8323052011":
        st.sidebar.success("🔑 Autenticado como ADMIN")
        es_admin = True
    elif clave != "":
        st.sidebar.warning("⚠️ Clave no reconocida.")

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("API Key Gemini:", type="password")

# 6. ENCABEZADO PRINCIPAL
col_head_img, col_head_txt = st.columns([1, 5])

with col_head_img:
    st.image(ROCKO_IMAGE_URL, width=100)

with col_head_txt:
    st.title("🤖 Rocko | RML Academy")
    st.caption("Sistema experto de tutoría mecatrónica con motor de misiones contextuales.")

# 7. PANEL DE CONTROL ADMIN (GESTOR AVANZADO DE MISIONES)
if modo_admin and es_admin:
    with st.expander("⚙️ GESTOR DE MISIONES Y EVALUACIÓN ADMIN", expanded=True):
        st.subheader("🛠️ Inyectar Nueva Misión al Estudiante")
        
        with st.form("nueva_mision_form"):
            col_m1, col_m2 = st.columns([2, 1])
            nueva_m_titulo = col_m1.text_input("Título de la Misión:")
            nueva_m_desc = col_m1.text_input("Descripción / Objetivo:")
            nueva_m_pts = col_m2.number_input("Recompensa 🪨:", value=100, step=25)
            nueva_m_kw = col_m2.text_input("Palabras Clave (sep por comas):", value="examen,reto")
            btn_crear_mision = st.form_submit_button("➕ Asignar Misión a la Clase")
            
            if btn_crear_mision and nueva_m_titulo:
                kw_list = [k.strip().lower() for k in nueva_m_kw.split(",") if k.strip()]
                st.session_state.misiones.append({
                    "id": len(st.session_state.misiones) + 1,
                    "titulo": nueva_m_titulo,
                    "desc": nueva_m_desc if nueva_m_desc else "Desafío especial asignado por el profesor.",
                    "recompensa": nueva_m_pts,
                    "completada": False,
                    "keywords": kw_list
                })
                st.toast("¡Nueva Misión asignada con éxito al estudiante!", icon="🎯")
                st.rerun()

        st.subheader("📋 Validación Manual por el Profesor")
        col_m_val1, col_m_val2 = st.columns(2)
        m_seleccionada = col_m_val1.selectbox("Seleccionar misión para aprobar:", [m["titulo"] for m in st.session_state.misiones if not m["completada"]])
        if col_m_val2.button("✅ Validar y Otorgar Puntos"):
            for m in st.session_state.misiones:
                if m["titulo"] == m_seleccionada:
                    m["completada"] = True
                    st.session_state.xp += m["recompensa"]
                    st.toast(f"¡Misión '{m['titulo']}' aprobada manualmente!", icon="🏆")
                    st.balloons()
                    st.rerun()
    st.divider()

# 8. ESTRUCTURA EN PESTAÑAS
tab_ruta, tab_consola, tab_reporte = st.tabs(["🎮 MODO PRÁCTICA (GENERADOR DE DESAFÍOS)", "CONSOLA ROCKO NLP", "DIAGNÓSTICO Y MISIONES"])

# PESTAÑA 1: MODO PRÁCTICA
with tab_ruta:
    st.subheader(f"🎯 Generador de Desafíos Adaptativos: {modulo}")
    st.write("Configura el tema para generar un escenario de taller real:")
    
    col_p1, col_p2 = st.columns(2)
    dificultad = col_p1.select_slider("Nivel de Dificultad:", options=["Básico", "Intermedio", "Desafío de Examen"])
    tipo_caso = col_p2.selectbox("Tema del Desafío:", ["Circuitos y Ley de Ohm", "Velocidad de Corte CNC", "Torque y Cinemática Robótica"])
    
    if st.button("⚡ Generar Nuevo Desafío Personalizado", type="primary"):
        v_rand = random.choice([12, 24, 48, 110, 220])
        r1_rand = random.randint(50, 500)
        r2_rand = random.randint(50, 500)
        d_rand = random.choice([25, 50, 75, 100])
        rpm_rand = random.choice([800, 1200, 1800, 2400])
        l_rand = round(random.uniform(0.3, 1.2), 2)
        m_rand = round(random.uniform(1.0, 5.0), 1)

        if "Circuitos" in tipo_caso:
            if dificultad == "Básico":
                prompt_gen = f"En un panel industrial alimentado con {v_rand}V se conecta una resistencia R1 de {r1_rand} ohms. Modela el sistema y calcula la corriente I."
            elif dificultad == "Intermedio":
                prompt_gen = f"Un circuito mixto de tablero tiene dos resistencias en paralelo de {r1_rand} ohms conectadas en serie con una de {r2_rand} ohms. Con una fuente de {v_rand}V, calcula la corriente total y la potencia disipada."
            else:
                prompt_gen = f"En una línea de producción, un circuito con fuente de {v_rand}V presenta una caída de tensión por tres resistencias R1={r1_rand}Ω, R2={r2_rand}Ω y R3=100Ω. Evalúa el modelo algebraico y determina si supera el límite de seguridad de 2 Amperes."

        elif "CNC" in tipo_caso:
            prompt_gen = f"Se requiere mecanizar una pieza de acero con diámetro D={d_rand}mm en un torno CNC girando a N={rpm_rand} RPM. Dificultad: {dificultad}. Calcula la velocidad de corte Vc y determina si cumple los parámetros del fabricante."

        else: # Robótica
            prompt_gen = f"Un brazo robótico articulado con una longitud de eslabón L={l_rand}m sostiene una carga útil de m={m_rand}kg en su extremo. Dificultad: {dificultad}. Calcula el torque en la articulación considerando g=9.81 m/s²."

        st.session_state.prompt_cargado = prompt_gen
        st.success(f"¡Desafío ({dificultad}) generado con éxito! Pasa a la 'CONSOLA ROCKO NLP' para resolverlo.")

# PESTAÑA 2: CONSOLA NLP (CON VALIDADOR AUTOMÁTICO DE MISIONES 2.0)
with tab_consola:
    if api_key:
        try:
            client = genai.Client(api_key=api_key)

            regla_modo = (
                "Desglosa el problema directamente completando las 7 secciones del dossier RML." 
                if modo_tutoria == "Explicación Completa (7 Secciones)" 
                else "Aplica el Método Socrático: Identifica los datos en la sección 1 y 2, pero en lugar de dar el cálculo final de inmediato, hazle una pregunta guía al alumno sobre el primer paso necesario."
            )

            prompt_sistema = f"""
            Eres Rocko, un tutor experto en Mecatrónica de RML Academy.
            Módulo actualmente activo: **{modulo}**.
            Modalidad seleccionada: **{modo_tutoria}**.

            INSTRUCCIONES DE RESPUESTA:
            1. Actúa como mentor de laboratorio. NUNCA uses respuestas genéricas de IA ("Como modelo de lenguaje").
            2. VALIDA EL MÓDULO Y EL CONTEXTO:
               - Si la consulta no es de ingeniería/mecatrónica, recházala amablemente.
               - Si pertenece a OTRO módulo diferente a **{modulo}**, indica que debe cambiar el módulo en la barra lateral.
            3. {regla_modo}
            4. Si el usuario no dio un dato esencial, indícalo amablemente para que lo proporcione.
            """

            if "mensajes" not in st.session_state:
                bienvenida = random.choice(BIENVENIDAS_ROCKO)
                st.session_state.mensajes = [
                    {"role": "assistant", "content": f"{bienvenida}\n\n*Módulo activo:* **{modulo}**."}
                ]

            for msg in st.session_state.mensajes:
                avatar = "🤖" if msg["role"] == "assistant" else "👤"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.write(msg["content"])

            prompt_input = st.chat_input("Escribe tu planteamiento técnico o procedimiento aquí...")
            prompt_final = prompt_input
            
            if "prompt_cargado" in st.session_state and st.session_state.prompt_cargado:
                prompt_final = st.session_state.prompt_cargado
                st.session_state.prompt_cargado = None

            if prompt_final:
                st.session_state.mensajes.append({"role": "user", "content": prompt_final})
                with st.chat_message("user", avatar="👤"):
                    st.write(prompt_final)

                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Rocko analizando variables y evaluando árbol de decisión..."):
                        
                        max_reintentos = 3
                        exito = False
                        
                        for intento in range(max_reintentos):
                            try:
                                response = client.models.generate_content(
                                    model='gemini-3.8-flash',
                                    contents=prompt_final,
                                    config=types.GenerateContentConfig(system_instruction=prompt_sistema),
                                )
                                st.write(response.text)
                                st.session_state.mensajes.append({"role": "assistant", "content": response.text})
                                exito = True
                                break
                            except Exception as err_api:
                                str_err = str(err_api)
                                if "503" in str_err or "UNAVAILABLE" in str_err or "resource exhausted" in str_err.lower():
                                    if intento < max_reintentos - 1:
                                        time.sleep(2)
                                        continue
                                    else:
                                        st.warning(random.choice(MENSAJES_REINTENTO_RED))
                                else:
                                    st.info("💡 **Aviso del Sistema:** Consulta en proceso de análisis.")
                                    break
                        
                        # --- MOTOR EVALUADOR DE MISIONES 2.0 ---
                        if exito:
                            st.session_state.xp += 50
                            st.session_state.problemas_resueltos += 1
                            prompt_low = prompt_final.lower()
                            
                            mision_completada_ahora = False
                            
                            # Recorrer misiones activas y comprobar palabras clave
                            for m in st.session_state.misiones:
                                if not m["completada"]:
                                    # Caso 1: Validación por palabras clave específicas
                                    if m["keywords"] and any(kw in prompt_low for kw in m["keywords"]):
                                        m["completada"] = True
                                        st.session_state.xp += m["recompensa"]
                                        st.toast(f"🎯 ¡Misión Cumplida: {m['titulo']}! (+{m['recompensa']} 🪨)", icon="🏆")
                                        mision_completada_ahora = True
                                    
                                    # Caso 2: Validación especial por Stones acumuladas (Misión 3)
                                    elif m["id"] == 3 and st.session_state.xp >= 150:
                                        m["completada"] = True
                                        st.session_state.xp += m["recompensa"]
                                        st.toast(f"🏆 ¡Misión de Maestría Desbloqueada! (+{m['recompensa']} 🪨)", icon="👑")
                                        mision_completada_ahora = True
                            
                            if mision_completada_ahora:
                                st.balloons()
                            else:
                                st.toast(random.choice(MENSAJES_TOAST_EXITO), icon="🪨")
                            
                            st.rerun()

        except Exception as e:
            st.warning("⚡ Ocurrió un ajuste de conexión en el laboratorio.")
    else:
        st.info("ℹ️ Ingresa la clave de acceso a la API en el menú lateral.")

# PESTAÑA 3: DIAGNÓSTICO Y EXPEDIENTE DE MISIONES
with tab_reporte:
    st.subheader("📊 Diagnóstico del Aprendiz y Expediente Técnico")
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Casos Resueltos", f"{st.session_state.problemas_resueltos}")
    col_r2.metric("Puntuación Total", f"{st.session_state.xp} pts")
    col_r3.metric("Nivel Mecatrónico", f"Nivel {(st.session_state.xp // 100) + 1}")
    
    st.write("### 📜 Historial Completo de Misiones")
    for m in st.session_state.misiones:
        estado = "COMPLETADA ✅" if m["completada"] else "EN PROGRESO ⬜"
        color = "green" if m["completada"] else "orange"
        st.markdown(f"""
        > **{m['titulo']}**  
        > *Estado:* `{estado}` | *Recompensa:* `{m['recompensa']} Stones`  
        > *Objetivo:* {m['desc']}
        """)
