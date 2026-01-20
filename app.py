col1.info(f"Nivel: {st.session_state.perfil['nivel']}")
            col2.info(f"Ritmo: {st.session_state.perfil['intensity']}")
            
            for dia, ejercicios in rut['sesiones'].items():
                with st.expander(f"📌 {dia}", expanded=True):
                    c1, c2, c3, c4, c5 = st.columns([3,1,1,1,1])
                    c1.markdown("Ejercicio"); c2.markdown("Sets"); c3.markdown("Reps")
                    c4.markdown("RIR"); c5.markdown("Tempo")
                    st.divider()
                    for ej in ejercicios:
                        c1, c2, c3, c4, c5 = st.columns([3,1,1,1,1])
                        c1.write(ej['nombre'])
                        c2.write(f"{ej['series']}")
                        c3.write(ej['repes'])
                        c4.write(ej['rir'])
                        c5.write(ej['tempo'])
            
            st.markdown("### 📊 Volumen Semanal")
            st.dataframe([{"Grupo": k, "Series": v} for k,v in rut['volumen_total'].items()], use_container_width=True)

    with tabs[1]:
        st.metric("Kcal Entrenamiento", int(st.session_state.macros_on['total']))
        if st.button("🔄 Nuevo Menú ON"):
            st.session_state.menu_on = crear_menu_diario(st.session_state.macros_on, prohibidos)
            st.rerun()
            
        for comida, datos in st.session_state.menu_on.items():
            with st.expander(f"🍽️ {comida}"):
                for item in datos['items']:
                    st.write(f"• {item['nombre']}: {item['gramos_peso']}g")
                st.caption(f"Kcal: {int(datos['totales']['kcal'])} | P:{int(datos['totales']['p'])} C:{int(datos['totales']['c'])} F:{int(datos['totales']['f'])}")

    with tabs[2]:
        st.metric("Kcal Descanso", int(st.session_state.macros_off['total']))
        if st.button("🔄 Nuevo Menú OFF"):
            st.session_state.menu_off = crear_menu_diario(st.session_state.macros_off, prohibidos)
            st.rerun()
            
        for comida, datos in st.session_state.menu_off.items():
            with st.expander(f"🍽️ {comida}"):
                for item in datos['items']:
                    st.write(f"• {item['nombre']}: {item['gramos_peso']}g")
                st.caption(f"Kcal: {int(datos['totales']['kcal'])} | P:{int(datos['totales']['p'])} C:{int(datos['totales']['c'])} F:{int(datos['totales']['f'])}")

    with tabs[3]:
        st.header("🛒 Lista Semanal")
        lista = st.session_state.lista_compra
        if lista:
            for item, cantidad in sorted(lista.items()):
                if cantidad > 0: st.checkbox(f"{item}: {int(cantidad)}g")
        else:
            st.warning("Genera la dieta primero.")

    with tabs[4]:
        st.header("📤 Exportar Plan")
        texto_final = generar_texto_plano(st.session_state.rutina, st.session_state.menu_on, st.session_state.menu_off)
        c1, c2 = st.columns(2)
        url_w = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_final)}"
        c1.link_button("📱 Enviar WhatsApp", url_w, use_container_width=True)
        mailto = f"mailto:?subject=Plan MacroLab&body={urllib.parse.quote(texto_final)}"
        c2.link_button("📧 Enviar Email", mailto, use_container_width=True)
        st.text_area("Copia manual", texto_final, height=300)