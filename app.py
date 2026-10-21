if api_key:
    try:
        genai.configure(api_key=api_key)

        # Listar todos los modelos que soportan generación de texto
        modelos = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]

        st.sidebar.write("### Modelos disponibles:")
        for m in modelos:
            st.sidebar.code(m)

    except Exception as e:
        st.sidebar.error(f"Error al listar modelos: {e}")
