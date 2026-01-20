import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import copy
import os
import urllib.parse
from collections import defaultdict
from calculadora import calcular_macros
from generador import buscar_alimento_perfecto
from entrenador import generar_rutina

# --- (SECCIÓN GOOGLE ELIMINADA PARA OPTIMIZAR) ---

# --- 🔧 ARREGLO DE RUTA ---
try:
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    os.chdir(directorio_actual)
except:
    pass

# --- CONFIGURACIÓN DE MARCA ---
NOMBRE_APP = "MacroLab"

archivos = os.listdir()
RUTA_LOGO = None
for f in archivos:
    if f.lower().startswith("logo") and f.lower().endswith((".jpg", ".jpeg", ".png")):
        RUTA_LOGO = f
        break

ICONO_FALLBACK = "🔬" 

if RUTA_LOGO:
    st.set_page_config(page_title=NOMBRE_APP, page_icon=RUTA_LOGO, layout="wide")
else:
    st.set_page_config(page_title=NOMBRE_APP, page_icon=ICONO_FALLBACK, layout="wide")

# --- FUNCIONES AUXILIARES ---
def calcular_horas_sueno(hora_bed, hora_wake):
    try:
        t1 = datetime.datetime.strptime(str(hora_bed), "%H:%M:%S").time()
        t2 = datetime.datetime.strptime(str(hora_wake), "%H:%M:%S").time()
        dummy_date = datetime.date(2000, 1, 1)
        dt1 = datetime.datetime.combine(dummy_date, t1)
        dt2 = datetime.datetime.combine(dummy_date, t2)
        if dt2 < dt1: dt2 += datetime.timedelta(days=1)
        diff = dt2 - dt1
        return round(diff.total_seconds() / 3600, 1)
    except: return 0.0

def calcular_macros_descanso(res_entreno):
    if 'total' not in res_entreno: return res_entreno
    res_descanso = copy.deepcopy(res_entreno)
    target_kcal = res_entreno['total'] * 0.85
    res_descanso['total'] = target_kcal
    p = res_entreno['macros_totales']['p']
    f = res_entreno['macros_totales']['f']
    new_c = (target_kcal - (p*4) - (f*9)) / 4
    res_descanso['macros_totales']['c'] = int(max(new_c, 40))
    old_c_total = res_entreno['macros_totales']['c']
    factor = res_descanso['macros_totales']['c'] / old_c_total if old_c_total > 0 else 0
    for nombre, m in res_descanso['comidas'].items():
        m['carb'] = int(m['carb'] * factor)
    return res_descanso

def calcular_macros_lineal(macros_on, macros_off, dias_entreno):
    """Calcula el promedio ponderado semanal EXACTO para la dieta lineal"""
    dias_descanso = 7 - dias_entreno
    
    if dias_entreno == 7: return copy.deepcopy(macros_on)
    if dias_entreno == 0: return copy.deepcopy(macros_off)

    kcal_on = macros_on['total']
    kcal_off = macros_off['total']
    
    total_semanal = (kcal_on * dias_entreno) + (kcal_off * dias_descanso)
    diario_lineal = total_semanal / 7
    
    res_lineal = copy.deepcopy(macros_on)
    res_lineal['total'] = diario_lineal
    
    p_on, c_on, f_on = macros_on['macros_totales']['p'], macros_on['macros_totales']['c'], macros_on['macros_totales']['f']
    p_off, c_off, f_off = macros_off['macros_totales']['p'], macros_off['macros_totales']['c'], macros_off['macros_totales']['f']
    
    res_lineal['macros_totales']['p'] = int((p_on * dias_entreno + p_off * dias_descanso) / 7)
    res_lineal['macros_totales']['c'] = int((c_on * dias_entreno + c_off * dias_descanso) / 7)
    res_lineal['macros_totales']['f'] = int((f_on * dias_entreno + f_off * dias_descanso) / 7)
    
    ratio_c = res_lineal['macros_totales']['c'] / c_on if c_on > 0 else 1
    ratio_f = res_lineal['macros_totales']['f'] / f_on if f_on > 0 else 1
    
    for nombre, m in res_lineal['comidas'].items():
        m['carb'] = int(m['carb'] * ratio_c)
        m['fat'] = int(m['fat'] * ratio_f)
        
    return res_lineal

def crear_menu_diario(datos_macros, prohibidos):
    menu = {}
    for nombre_comida, m in datos_macros['comidas'].items():
        items_plato = []
        if "Desayuno" in nombre_comida or "Merienda" in nombre_comida:
            perfil = random.choice(['dulce', 'dulce', 'salado'])
        else:
            perfil = random.choice(['salado', 'salado', 'dulce'])
        llevamos = {'p':0, 'c':0, 'f':0, 'kcal':0}
        sug_p = buscar_alimento_perfecto('protein', m['prot'], prohibidos, perfil)
        if sug_p:
            items_plato.append(sug_p)
            for k in llevamos: llevamos[k] += sug_p['macros_reales'].get(k,0)
            if sug_p.get('perfil') != 'neutro': perfil = sug_p['perfil']
        rest_c = m['carb'] - llevamos['c']
        if rest_c > 10:
            sug_c = buscar_alimento_perfecto('carbohydrates', rest_c, prohibidos, perfil)
            if sug_c:
                items_plato.append(sug_c)
                for k in llevamos: llevamos[k] += sug_c['macros_reales'].get(k,0)
        rest_f = m['fat'] - llevamos['f']
        if rest_f > 5:
            sug_f = buscar_alimento_perfecto('fat', rest_f, prohibidos, perfil)
            if sug_f:
                items_plato.append(sug_f)
                for k in llevamos: llevamos[k] += sug_f['macros_reales'].get(k,0)
        menu[nombre_comida] = {"items": items_plato, "totales": llevamos}
    return menu

def generar_lista_compra_inteligente(menu_on, menu_off, dias_entreno):
    dias_descanso = 7 - dias_entreno
    compra = defaultdict(float)
    
    for comida in menu_on.values():
        for item in comida['items']: 
            compra[item['nombre']] += item['gramos_peso'] * dias_entreno
            
    for comida in menu_off.values():
        for item in comida['items']: 
            compra[item['nombre']] += item['gramos_peso'] * dias_descanso
            
    return dict(compra)

def mostrar_dashboard_macros(datos_macros, titulo):
    m = datos_macros['macros_totales']
    st.markdown(f"#### 📊 Objetivos: {titulo}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kcal", f"{int(datos_macros['total'])}")
    c2.metric("Proteína", f"{m['p']}g")
    c3.metric("Carbos", f"{m['c']}g")
    c4.metric("Grasas", f"{m['f']}g")
    st.progress(m['p']/(m['p']+m['c']+m['f']), text="Distribución de Energía")
    st.markdown("---")

def generar_texto_plano(rutina, menu_on, menu_off, dias_entreno):
    """Genera un texto limpio para copiar y pegar"""
    txt = f"*PLAN MACROLAB - SEMANAL*\n"
    txt += f"========================\n\n"
    
    txt += f"*🔥 DIETA ENTRENAMIENTO*\n"
    for nombre, datos in menu_on.items():
        txt += f"_{nombre.upper()}_\n"
        for item in datos['items']:
            txt += f"- {item['nombre']}: {item['gramos_peso']}g\n"
        txt += "\n"
        
    txt += f"*💤 DIETA DESCANSO*\n"
    for nombre, datos in menu_off.items():
        txt += f"_{nombre.upper()}_\n"
        for item in datos['items']:
            txt += f"- {item['nombre']}: {item['gramos_peso']}g\n"
        txt += "\n"
    
    if rutina and 'info' in rutina:
        txt += f"*🏋️ RUTINA*\n"
        txt += f"Estrategia: {rutina['info'].get('estrategia', 'General')}\n"
        for dia, ejercicios in rutina.get('sesiones', {}).items():
            txt += f"\n*{dia.upper()}*\n"
            for ej in ejercicios:
                txt += f"{ej['nombre']} | {ej['series_num']}x{ej['repes']}\n"
        
    return txt

# --- ESTADO DE SESIÓN ---
if 'generado' not in st.session_state: st.session_state.generado = False
if 'menu_on' not in st.session_state: st.session_state.menu_on = {}
if 'menu_off' not in st.session_state: st.session_state.menu_off = {}
if 'macros_lineal' not in st.session_state: st.session_state.macros_lineal = {}
if 'menu_lineal' not in st.session_state: st.session_state.menu_lineal = {}
if 'rutina' not in st.session_state: st.session_state.rutina = {}
if 'lista_compra' not in st.session_state: st.session_state.lista_compra = {}

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("👤 Tus Datos")
    
    col1, col2 = st.columns(2)
    peso = col1.number_input("Peso (kg)", 40.0, 160.0, 75.0, 0.1)
    edad = col1.number_input("Edad", 12, 90, 25) 
    altura = col2.number_input("Altura (cm)", 120.0, 230.0, 175.0)
    genero = "male" if col2.selectbox("Género", ["Hombre", "Mujer"]) == "Hombre" else "female"

    st.subheader("🔥 Actividad")
    act_map = {
        "1. Sedentario (x1.2)": 1.2,
        "2. Ligero (x1.375)": 1.375,
        "3. Moderado (x1.55)": 1.55,
        "4. Fuerte (x1.725)": 1.725,
        "5. Muy Fuerte (x1.9)": 1.9
    }
    op_act = st.selectbox("Nivel", list(act_map.keys()))
    actividad = act_map[op_act]

    st.subheader("🎯 Meta")
    obj_txt = st.selectbox("Objetivo", ["1. Perder Grasa", "2. Ganar Músculo", "3. Mantener"])
    
    dias_entreno = st.slider("Días Gym/Semana", 0, 7, 4)
    hora_entreno = st.time_input("Hora Entreno", datetime.time(18, 00))
    
    st.subheader("🍽️ Dieta")
    n_comidas = st.number_input("Comidas/día", 2, 6, 4)
    prohibidos = st.multiselect("🚫 Alergias:", ["leche", "huevo", "pescado", "marisco", "cacahuete", "gluten", "cerdo", "ternera", "queso"])
    
    hora_bed = st.time_input("Hora Dormir", datetime.time(23, 0))
    hora_wake = st.time_input("Hora Despertar", datetime.time(7, 30))
    horas_sueno = calcular_horas_sueno(hora_bed, hora_wake)
    
    # BOTÓN DE GENERAR
    if st.button("🚀 INICIAR LABORATORIO", use_container_width=True):
        st.session_state.generado = True
        st.session_state.lista_compra = {} 
        
        perfil = {
            "weight": peso, "height": altura, "age": int(edad), "gender": genero, 
            "goal": obj_txt[0], "intensity": "2", "activity": actividad, 
            "num_comidas": n_comidas, "nivel_entreno": "2", 
            "dias_entreno": dias_entreno, "horas_sueno": horas_sueno,
            "hora_entreno": hora_entreno.strftime("%H:%M")
        }
        
        st.session_state.macros_on = calcular_macros(perfil)
        st.session_state.macros_off = calcular_macros_descanso(st.session_state.macros_on)
        st.session_state.macros_lineal = calcular_macros_lineal(
            st.session_state.macros_on, 
            st.session_state.macros_off, 
            dias_entreno
        )
        
        st.session_state.menu_on = crear_menu_diario(st.session_state.macros_on, prohibidos)
        st.session_state.menu_off = crear_menu_diario(st.session_state.macros_off, prohibidos)
        st.session_state.menu_lineal = crear_menu_diario(st.session_state.macros_lineal, prohibidos)
        
        if dias_entreno > 0:
            try:
                st.session_state.rutina = generar_rutina(perfil)
            except:
                st.session_state.rutina = {'info': {'estrategia': 'Error calculando rutina'}, 'sesiones': {}}
        else:
            st.session_state.rutina = {
                'info': {'estrategia': 'Descanso Total / Recuperación'},
                'sesiones': {}
            }

        st.session_state.lista_compra = generar_lista_compra_inteligente(st.session_state.menu_on, st.session_state.menu_off, dias_entreno)

    # --- TIENDA FITNESS (Todo Enlaces de Búsqueda) ---
    st.markdown("---")
    with st.expander("🏪 TIENDA FITNESS (Clic aquí)"):
        st.caption("Equipamiento recomendado por MacroLab")
        
        # 1. SUPLEMENTOS
        st.markdown("**💊 Suplementación**")
        # Proteína
        link_prot = "https://www.amazon.es/s?k=proteina+whey&tag=criptex02-21" 
        st.link_button("🥛 Proteína Whey", link_prot, use_container_width=True)
        
        col_s1, col_s2 = st.columns(2)
        # Creatina (Búsqueda)
        link_creatina = "https://www.amazon.es/s?k=creatina+monohidrato&tag=criptex02-21"
        with col_s1: st.link_button("⚡ Creatina", link_creatina, use_container_width=True)
        
        # Pre-entreno (Búsqueda)
        link_pre = "https://www.amazon.es/s?k=pre+workout&tag=criptex02-21"
        with col_s2: st.link_button("🚀 Pre-Entreno", link_pre, use_container_width=True)

        st.markdown("---")
        
        # 2. GYM EN CASA
        st.markdown("**🏠 Gym en Casa**")
        # Mancuernas (Búsqueda)
        link_mancuernas = "https://www.amazon.es/s?k=juego+mancuernas&tag=criptex02-21"
        st.link_button("🏋️ Juego Mancuernas", link_mancuernas, use_container_width=True)
        
        col_h1, col_h2 = st.columns(2)
        # Esterilla (Búsqueda)
        link_esterilla = "https://www.amazon.es/s?k=esterilla+yoga&tag=criptex02-21"
        with col_h1: st.link_button("🧘 Esterilla", link_esterilla, use_container_width=True)
        
        # Gomas (Búsqueda)
        link_gomas = "https://www.amazon.es/s?k=bandas+elasticas+fitness&tag=criptex02-21"
        with col_h2: st.link_button("🧶 Gomas", link_gomas, use_container_width=True)
        
        st.markdown("---")

        # 3. ACCESORIOS
        st.markdown("**🎒 Accesorios Básicos**")
        col_a1, col_a2 = st.columns(2)
        
        # Báscula (Búsqueda)
        link_bascula = "https://www.amazon.es/s?k=bascula+cocina+digital&tag=criptex02-21"
        with col_a1: st.link_button("⚖️ Báscula", link_bascula, use_container_width=True)
        
        # Cinta (Búsqueda)
        link_cinta = "https://www.amazon.es/s?k=cinta+metrica+costura&tag=criptex02-21"
        with col_a2: st.link_button("📏 Cinta", link_cinta, use_container_width=True)


# --- VISTA PRINCIPAL ---

if not st.session_state.generado:
    st.write("")
    st.write("") 
    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        if RUTA_LOGO: st.image(RUTA_LOGO, use_container_width=True)
        else: st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{ICONO_FALLBACK}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center;'>{NOMBRE_APP}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 20px; color: gray;'>Sistema de Precisión Nutricional y Entrenamiento</p>", unsafe_allow_html=True)
        st.info("👈 Configura tus datos en el menú izquierdo para generar tu plan.")
        
        st.markdown("---")
        st.caption("👇 ¿Buscas equipamiento? Abre la TIENDA en la barra lateral izquierda.")

else:
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        if RUTA_LOGO: st.image(RUTA_LOGO, width=100)
        else: st.title(ICONO_FALLBACK)
    with col_titulo:
        st.title(NOMBRE_APP)
        st.caption("Panel de Control Activo")
    st.markdown("---")

    t_rutina, t_lineal, t_on, t_off, t_lista, t_share = st.tabs(["🏋️ RUTINA", "⚖️ LINEAL", "🔥 DÍA ON", "💤 DÍA OFF", "📝 LISTA", "📤 COMPARTIR"])
    
    with t_rutina:
        rut = st.session_state.rutina
        if rut and 'info' in rut:
            st.info(f"Estrategia: **{rut['info'].get('estrategia', 'Estándar')}**")
            if not rut.get('sesiones'):
                st.write("🎉 ¡Disfruta de tu descanso total! No hay sesiones de pesas programadas.")
            for dia, ejes in rut.get('sesiones', {}).items():
                with st.expander(f"📌 {dia}"):
                    for ej in ejes: 
                        st.write(f"**{ej['nombre']}** | {ej['series_num']} series")
                        st.caption(f"Técnica: {ej['tips']}")
        else:
            st.warning("⚠️ Pulsa 'INICIAR LABORATORIO' de nuevo.")

    with t_lineal:
        mostrar_dashboard_macros(st.session_state.macros_lineal, "Dieta Lineal (Promedio Semanal Constante)")
        st.caption("💡 Esta dieta mantiene el equilibrio calórico semanal comiendo lo mismo todos los días (Media entre ON y OFF).")
        if st.button("🔄 Generar Nuevo Menú Lineal"):
            st.session_state.menu_lineal = crear_menu_diario(st.session_state.macros_lineal, prohibidos)
            st.rerun()
        for nombre, datos in st.session_state.menu_lineal.items():
            with st.expander(f"🍽️ {nombre.upper()}"):
                for item in datos['items']: st.write(f"• **{item['nombre']}**: {item['gramos_peso']}g")
                st.caption(f"Kcal: {int(datos['totales']['kcal'])} | P:{int(datos['totales']['p'])} C:{int(datos['totales']['c'])} F:{int(datos['totales']['f'])}")

    with t_on:
        mostrar_dashboard_macros(st.session_state.macros_on, "Día de Entrenamiento (High Carb)")
        st.caption("💡 Usa este menú los días que vayas al gimnasio.")
        if st.button("🔄 Cambiar Comidas (ON)"):
            st.session_state.menu_on = crear_menu_diario(st.session_state.macros_on, prohibidos)
            st.rerun()
        for nombre, datos in st.session_state.menu_on.items():
            with st.expander(f"🍽️ {nombre.upper()}"):
                for item in datos['items']: st.write(f"• **{item['nombre']}**: {item['gramos_peso']}g")
                st.caption(f"Kcal: {int(datos['totales']['kcal'])} | P:{int(datos['totales']['p'])} C:{int(datos['totales']['c'])} F:{int(datos['totales']['f'])}")

    with t_off:
        mostrar_dashboard_macros(st.session_state.macros_off, "Día de Descanso (Low Carb)")
        st.caption("💡 Usa este menú los días que NO entrenes.")
        if st.button("🔄 Cambiar Comidas (OFF)"):
            st.session_state.menu_off = crear_menu_diario(st.session_state.macros_off, prohibidos)
            st.rerun()
        for nombre, datos in st.session_state.menu_off.items():
            with st.expander(f"🍽️ {nombre.upper()}"):
                for item in datos['items']: st.write(f"• **{item['nombre']}**: {item['gramos_peso']}g")
                st.caption(f"Kcal: {int(datos['totales']['kcal'])} | P:{int(datos['totales']['p'])} C:{int(datos['totales']['c'])} F:{int(datos['totales']['f'])}")

    with t_lista:
        st.header("📋 Lista de la Compra")
        st.caption(f"Basada en tu planificación de {dias_entreno} días de entreno (Dieta Cíclica ON/OFF).")
        
        if st.session_state.lista_compra:
            st.info("Marca las casillas mientras compras:")
            for item, cantidad in sorted(st.session_state.lista_compra.items()):
                if int(cantidad) > 0:
                    st.checkbox(f"**{item.title()}**: {int(cantidad)} g")
            
            if st.button("🗑️ Borrar lista"):
                st.session_state.lista_compra = {}
                st.rerun()
        else:
            st.warning("👈 Tu lista está vacía. Genera una dieta primero.")

    with t_share:
        st.markdown("### 📤 Enviar Plan")
        texto_plan = generar_texto_plano(st.session_state.rutina, st.session_state.menu_on, st.session_state.menu_off, dias_entreno)
        
        c1, c2 = st.columns(2)
        
        with c1:
            whatsapp_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_plan)}"
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #25D366; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold;">📱 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.caption("Nota: Si el plan es muy largo, el botón de WhatsApp podría no abrirse. En ese caso, usa el botón de copiar de abajo.")

        with c2:
            subject = urllib.parse.quote("Plan Semanal MacroLab")
            body = urllib.parse.quote(texto_plan)
            link_email = f"mailto:?subject={subject}&body={body}"
            st.markdown(f'<a href="{link_email}" target="_blank" style="text-decoration: none;"><button style="background-color: #0078D4; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold;">📧 Enviar por Email</button></a>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("#### 📋 Copia Manual (Opción Segura)")
        st.code(texto_plan, language=None)

    st.divider()
    st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa. Consulta a un profesional antes de empezar.")
