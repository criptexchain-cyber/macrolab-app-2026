import streamlit as st
import pandas as pd
import datetime
import random
import copy
import urllib.parse
from collections import defaultdict

# --- CONFIGURACIÓN SEO ---
TITULO_SEO = "MacroLab - Entrenador y Nutricionista Inteligente"
ICONO = "🔬"

try:
    st.set_page_config(page_title=TITULO_SEO, page_icon=ICONO, layout="wide")
except:
    pass

# ==========================================
# 1. BASE DE DATOS DE ALIMENTOS (INTERNA)
# ==========================================
DB_ALIMENTOS = [
    {"nombre": "Pechuga de Pollo", "tipo": "protein", "perfil": "salado", "macros": {"p": 23, "c": 0, "f": 1}},
    {"nombre": "Ternera Magra", "tipo": "protein", "perfil": "salado", "macros": {"p": 20, "c": 0, "f": 5}},
    {"nombre": "Merluza", "tipo": "protein", "perfil": "salado", "macros": {"p": 17, "c": 0, "f": 2}},
    {"nombre": "Huevos L", "tipo": "protein", "perfil": "salado", "macros": {"p": 13, "c": 1, "f": 11}},
    {"nombre": "Claras de Huevo", "tipo": "protein", "perfil": "neutro", "macros": {"p": 11, "c": 0, "f": 0}},
    {"nombre": "Atún al Natural", "tipo": "protein", "perfil": "salado", "macros": {"p": 24, "c": 0, "f": 1}},
    {"nombre": "Proteína Whey", "tipo": "protein", "perfil": "dulce", "macros": {"p": 80, "c": 5, "f": 2}},
    {"nombre": "Yogur Griego 0%", "tipo": "protein", "perfil": "dulce", "macros": {"p": 10, "c": 4, "f": 0}},
    {"nombre": "Arroz Blanco", "tipo": "carbohydrates", "perfil": "neutro", "macros": {"p": 2, "c": 28, "f": 0}},
    {"nombre": "Pasta Integral", "tipo": "carbohydrates", "perfil": "salado", "macros": {"p": 5, "c": 25, "f": 1}},
    {"nombre": "Patata", "tipo": "carbohydrates", "perfil": "salado", "macros": {"p": 2, "c": 17, "f": 0}},
    {"nombre": "Avena", "tipo": "carbohydrates", "perfil": "dulce", "macros": {"p": 4, "c": 12, "f": 1}},
    {"nombre": "Pan Integral", "tipo": "carbohydrates", "perfil": "neutro", "macros": {"p": 4, "c": 15, "f": 1}},
    {"nombre": "Fruta (Manzana/Pera)", "tipo": "carbohydrates", "perfil": "dulce", "macros": {"p": 0, "c": 12, "f": 0}},
    {"nombre": "Aceite de Oliva", "tipo": "fat", "perfil": "salado", "macros": {"p": 0, "c": 0, "f": 100}},
    {"nombre": "Aguacate", "tipo": "fat", "perfil": "salado", "macros": {"p": 2, "c": 9, "f": 15}},
    {"nombre": "Frutos Secos", "tipo": "fat", "perfil": "neutro", "macros": {"p": 5, "c": 5, "f": 25}},
    {"nombre": "Crema de Cacahuete", "tipo": "fat", "perfil": "dulce", "macros": {"p": 8, "c": 6, "f": 16}}
]

def buscar_alimento(tipo, gramos_macro, perfil_plato, prohibidos=[]):
    candidatos = [a for a in DB_ALIMENTOS if a['tipo'] == tipo]
    
    if prohibidos:
        for p in prohibidos:
            if p == "leche": candidatos = [x for x in candidatos if x['nombre'] not in ["Yogur Griego 0%", "Proteína Whey"]]
            elif p == "huevo": candidatos = [x for x in candidatos if "Huevo" not in x['nombre']]
            elif p == "gluten": candidatos = [x for x in candidatos if x['nombre'] not in ["Pasta Integral", "Pan Integral", "Avena"]]
            elif p == "pescado": candidatos = [x for x in candidatos if x['nombre'] not in ["Merluza", "Atún al Natural"]]
            elif p == "cacahuete": candidatos = [x for x in candidatos if x['nombre'] not in ["Frutos Secos", "Crema de Cacahuete"]]
            
    if perfil_plato != "neutro":
        candidatos = [a for a in candidatos if a['perfil'] in [perfil_plato, "neutro"]]
    
    if not candidatos: return None
    
    elegido = random.choice(candidatos)
    macro_por_100 = elegido['macros'][tipo[0]]
    if macro_por_100 == 0: return None
    
    peso_necesario = (gramos_macro * 100) / macro_por_100
    
    macros_finales = {
        'p': (elegido['macros']['p'] * peso_necesario) / 100,
        'c': (elegido['macros']['c'] * peso_necesario) / 100,
        'f': (elegido['macros']['f'] * peso_necesario) / 100
    }
    
    return {
        "nombre": elegido['nombre'],
        "gramos_peso": int(peso_necesario),
        "macros_reales": macros_finales,
        "perfil": elegido['perfil']
    }

def crear_menu_diario(datos_macros, prohibidos=[]):
    menu = {}
    for nombre_comida, m in datos_macros['comidas'].items():
        items_plato = []
        if "Desayuno" in nombre_comida or "Merienda" in nombre_comida or "Recena" in nombre_comida:
            perfil = random.choice(['dulce', 'dulce', 'neutro'])
        else:
            perfil = random.choice(['salado', 'salado', 'neutro'])
            
        llevamos = {'p':0, 'c':0, 'f':0, 'kcal':0}
        
        # Proteína
        sug_p = buscar_alimento('protein', m['prot'], perfil, prohibidos)
        if sug_p:
            items_plato.append(sug_p)
            for k in ['p','c','f']: llevamos[k] += sug_p['macros_reales'].get(k,0)
            
        # Carbohidratos
        rest_c = m['carb'] - llevamos['c']
        if rest_c > 5:
            sug_c = buscar_alimento('carbohydrates', rest_c, perfil, prohibidos)
            if sug_c:
                items_plato.append(sug_c)
                for k in ['p','c','f']: llevamos[k] += sug_c['macros_reales'].get(k,0)

        # Grasas
        rest_f = m['fat'] - llevamos['f']
        if rest_f > 3:
            sug_f = buscar_alimento('fat', rest_f, perfil, prohibidos)
            if sug_f:
                items_plato.append(sug_f)
                for k in ['p','c','f']: llevamos[k] += sug_f['macros_reales'].get(k,0)
                
        llevamos['kcal'] = (llevamos['p']*4) + (llevamos['c']*4) + (llevamos['f']*9)
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

# ==========================================
# 2. LÓGICA DE CÁLCULO
# ==========================================

def calcular_macros(perfil):
    peso, altura, edad = perfil['weight'], perfil['height'], perfil['age']
    genero, actividad = perfil['gender'], perfil['activity']
    
    if genero == 'male': tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
    else: tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161
        
    tdee = tmb * actividad
    
    goal = perfil['goal']
    intensity = perfil['intensity']
    ajuste_kcal = 0
    
    if goal == '1': # Perder
        if "Lento" in intensity: ajuste_kcal = -250
        elif "Rápido" in intensity: ajuste_kcal = -600
        else: ajuste_kcal = -400
    elif goal == '2': # Ganar
        if "Lento" in intensity: ajuste_kcal = +200
        elif "Rápido" in intensity: ajuste_kcal = +500
        else: ajuste_kcal = +350
    
    target_kcal = tdee + ajuste_kcal
    
    factor_prot = 2.2 if goal == '1' else 2.0
    prot_g = factor_prot * peso
    fat_g = 0.9 * peso
    kcal_p, kcal_f = prot_g * 4, fat_g * 9
    rem_kcal = max(0, target_kcal - kcal_p - kcal_f)
    carb_g = rem_kcal / 4
    
    n_comidas = perfil['num_comidas']
    distribucion = {}
    nombres = ["Desayuno", "Almuerzo", "Merienda", "Cena", "Post-Entreno", "Recena"]
    mis_comidas = nombres[:n_comidas]
    
    for c in mis_comidas:
        distribucion[c] = {
            'prot': int(prot_g / n_comidas),
            'carb': int(carb_g / n_comidas),
            'fat': int(fat_g / n_comidas)
        }
    
    return {
        'total': target_kcal,
        'macros_totales': {'p': int(prot_g), 'c': int(carb_g), 'f': int(fat_g)},
        'comidas': distribucion
    }

def calcular_macros_descanso(res_entreno):
    res = copy.deepcopy(res_entreno)
    res['total'] = res['total'] * 0.85 
    res['macros_totales']['c'] = int(res['macros_totales']['c'] * 0.6) 
    for c in res['comidas']:
        res['comidas'][c]['carb'] = int(res['comidas'][c]['carb'] * 0.6)
    return res

def generar_rutina_inteligente(perfil):
    dias = perfil['dias_entreno']
    nivel = perfil['nivel']
    
    config_nivel = {
        "Principiante": {"rir": "3-4", "tempo": "2-0-2-0"},
        "Intermedio":   {"rir": "2-3", "tempo": "3-0-1-0"},
        "Avanzado":     {"rir": "1-2", "tempo": "3-1-X-0"}
    }
    cfg = config_nivel.get(nivel, config_nivel["Intermedio"])
    
    db_ejercicios = {
        "Sentadilla": "Cuádriceps", "Prensa": "Cuádriceps", "Peso Muerto": "Isquios",
        "Press Banca": "Pectoral", "Press Militar": "Hombro", "Remo Barra": "Espalda",
        "Jalón Pecho": "Espalda", "Elev. Laterales": "Hombro", "Curl Bíceps": "Bíceps",
        "Extensión Tríceps": "Tríceps", "Plancha": "Core"
    }
    
    estructura = {
        "Día A": ["Sentadilla", "Press Banca", "Remo Barra", "Press Militar"],
        "Día B": ["Peso Muerto", "Prensa", "Jalón Pecho", "Elev. Laterales"],
        "Día C": ["Sentadilla", "Press Banca", "Remo Barra", "Plancha"],
        "Día D": ["Prensa", "Peso Muerto", "Press Militar", "Curl Bíceps"]
    }
    
    rutina_final = {'sesiones': {}, 'volumen_total': defaultdict(int)}
    dias_nombres = list(estructura.keys())
    while len(dias_nombres) < dias:
        dias_nombres.append(f"Día Extra {len(dias_nombres)+1}")
        
    for i in range(dias):
        nombre_dia = dias_nombres[i % len(dias_nombres)]
        ejercicios_base = estructura.get(nombre_dia, ["Sentadilla", "Press Militar", "Remo Barra"])
        
        detalles_dia = []
        for ej in ejercicios_base:
            grupo = db_ejercicios.get(ej, "General")
            series = 3 if nivel == "Principiante" else (5 if nivel == "Avanzado" else 4)
            rutina_final['volumen_total'][grupo] += series
            
            # --- CORRECCIÓN: Estructura plana para DataFrame ---
            detalles_dia.append({
                "Ejercicio": ej,
                "Sets": str(series),
                "Reps": "8-12",
                "RIR": cfg['rir'],
                "Tempo": cfg['tempo']
            })
            
        rutina_final['sesiones'][f"Día {i+1} ({nombre_dia})"] = detalles_dia

    return rutina_final

def generar_texto_plano(rutina, menu_on, menu_off):
    txt = "*🧬 PLAN MACROLAB*\n\n"
    txt += "*🏋️ RUTINA SEMANAL*\n"
    for dia, ejercicios in rutina.get('sesiones', {}).items():
        txt += f"\n📌 *{dia.upper()}*\n"
        for ej in ejercicios:
            txt += f"- {ej['Ejercicio']} | {ej['Sets']}x{ej['Reps']} | RIR:{ej['RIR']}\n"
    txt += "\n*🔥 DIETA ON (Entreno)*\n"
    for comida, datos in menu_on.items():
        txt += f"_{comida}_: "
        items = [f"{i['nombre']} ({i['gramos_peso']}g)" for i in datos['items']]
        txt += ", ".join(items) + "\n"
    txt += "\n*💤 DIETA OFF (Descanso)*\n"
    for comida, datos in menu_off.items():
        txt += f"_{comida}_: "
        items = [f"{i['nombre']} ({i['gramos_peso']}g)" for i in datos['items']]
        txt += ", ".join(items) + "\n"
    return txt

# ==========================================
# 3. INTERFAZ (FRONTEND)
# ==========================================

if 'generado' not in st.session_state: st.session_state.generado = False
if 'rutina' not in st.session_state: st.session_state.rutina = {}
if 'menu_on' not in st.session_state: st.session_state.menu_on = {}

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("👤 Tus Datos")
    c1, c2 = st.columns(2)
    peso = c1.number_input("Peso (kg)", 40.0, 160.0, 75.0)
    altura = c2.number_input("Altura", 120, 230, 175)
    edad = c1.number_input("Edad", 14, 90, 25)
    genero = c2.selectbox("Sexo", ["Hombre", "Mujer"])
    
    act_map = {
        "1. Sedentario (x1.2)": 1.2,
        "2. Ligero (x1.375)": 1.375,
        "3. Moderado (x1.55)": 1.55,
        "4. Activo (x1.725)": 1.725,
        "5. Muy Activo (x1.9)": 1.9
    }
    actividad = act_map[st.selectbox("Actividad", list(act_map.keys()))]
    
    obj_txt = st.selectbox("Objetivo", ["1. Perder Grasa", "2. Ganar Músculo", "3. Mantener"])
    intensidad = st.select_slider("Ritmo", options=["Lento (Conservador)", "Estándar", "Rápido (Agresivo)"], value="Estándar")
    
    st.markdown("---")
    st.caption("🏋️ Configuración Entreno")
    dias_entreno = st.slider("Días Gym/Semana", 0, 7, 4)
    nivel_exp = st.selectbox("Nivel de Experiencia", ["Principiante", "Intermedio", "Avanzado"])
    hora_entreno = st.time_input("Hora Entreno", datetime.time(18, 00))
    
    st.markdown("---")
    st.caption("🍽️ Configuración Dieta")
    # --- ¡AQUÍ ESTÁ LA RECUPERACIÓN! ---
    estrategia = st.radio("Estrategia", ["🌊 Ciclado (ON/OFF)", "📏 Lineal (Estable)"])
    # -----------------------------------
    n_comidas = st.number_input("Comidas/día", 2, 6, 4)
    prohibidos = st.multiselect("🚫 Alergias", ["leche", "huevo", "gluten", "pescado", "cacahuete"])
    hora_bed = st.time_input("Hora Dormir", datetime.time(23, 0))
    hora_wake = st.time_input("Hora Despertar", datetime.time(7, 30))
    
    if st.button("🚀 INICIAR LABORATORIO", use_container_width=True):
        st.session_state.generado = True
        perfil = {
            "weight": peso, "height": altura, "age": int(edad), 
            "gender": "male" if genero=="Hombre" else "female",
            "activity": actividad, "goal": obj_txt[0], "intensity": intensidad,
            "num_comidas": n_comidas, "dias_entreno": dias_entreno, 
            "nivel": nivel_exp,
            "estrategia": estrategia # Guardamos la estrategia
        }
        st.session_state.perfil = perfil
        
        # --- LÓGICA RECUPERADA ---
        macros_base = calcular_macros(perfil)
        if "Lineal" in estrategia:
            # Si es lineal, ON y OFF son iguales
            st.session_state.macros_on = macros_base
            st.session_state.macros_off = macros_base
        else:
            # Si es ciclado, OFF es reducido
            st.session_state.macros_on = macros_base
            st.session_state.macros_off = calcular_macros_descanso(macros_base)
        # -------------------------

        st.session_state.menu_on = crear_menu_diario(st.session_state.macros_on, prohibidos)
        st.session_state.menu_off = crear_menu_diario(st.session_state.macros_off, prohibidos)
        st.session_state.lista_compra = generar_lista_compra_inteligente(st.session_state.menu_on, st.session_state.menu_off, dias_entreno)
        
        if dias_entreno > 0:
            st.session_state.rutina = generar_rutina_inteligente(perfil)
        else:
            st.session_state.rutina = {'sesiones':{}, 'volumen_total':{}}

    st.write("")
    with st.expander("🏪 TIENDA FITNESS"):
        st.link_button("🥛 Proteína", "https://www.amazon.es/s?k=proteina+whey&tag=criptex02-21", use_container_width=True)
        st.link_button("⚡ Creatina", "https://www.amazon.es/s?k=creatina+monohidrato&tag=criptex02-21", use_container_width=True)
        st.link_button("🏋️ Mancuernas", "https://www.amazon.es/s?k=juego+mancuernas&tag=criptex02-21", use_container_width=True)

# --- PANTALLA PRINCIPAL ---
if not st.session_state.generado:
    # LOGO RECUPERADO (SOLO TEXTO GRANDE PARA EVITAR ERRORES DE IMAGEN)
    st.title("🔬 MacroLab")
    st.markdown("### Sistema de Entrenamiento y Nutrición de Precisión")
    st.info("👈 Configura tus datos en el menú izquierdo.")
    st.divider()
    with st.expander("🔍 ¿Cómo funciona?"):
        st.write("Calculadora científica de macros y generador de rutinas.")
else:
    # LOGO RECUPERADO EN EL PANEL
    st.title("🔬 Panel de Control")
    
    tabs = st.tabs(["🏋️ RUTINA", "🔥 DÍA ON", "💤 DÍA OFF", "📝 LISTA", "📤 COMPARTIR"])
    
    # 1. RUTINA ARREGLADA (SOLUCIÓN MÓVIL)
    with tabs[0]:
        rut = st.session_state.rutina
        if not rut.get('sesiones'):
            st.warning("Sin entrenamiento.")
        else:
            c1, c2 = st.columns(2)
            c1.info(f"**Nivel:** {st.session_state.perfil['nivel']}")
            c2.info(f"**Ritmo:** {st.session_state.perfil['intensity']}")
            
            for dia, ejercicios in rut['sesiones'].items():
                with st.expander(f"📌 {dia}", expanded=True):
                    # AQUÍ ESTÁ LA SOLUCIÓN: Dataframe puro sin columnas que se rompan
                    df_rutina = pd.DataFrame(ejercicios)
                    st.dataframe(
                        df_rutina, 
                        hide_index=True, 
                        use_container_width=True
                    )
            
            st.markdown("### 📊 Volumen Semanal")
            st.dataframe([{"Grupo": k, "Series": v} for k,v in rut['volumen_total'].items()], use_container_width=True, hide_index=True)

    # 2. DÍA ON (MACROS ARREGLADOS)
    with tabs[1]:
        m = st.session_state.macros_on
        # BLOQUE DE MACROS VISIBLE ARRIBA
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔥 KCAL", int(m['total']))
        col2.metric("🥩 PROT", f"{m['macros_totales']['p']}g")
        col3.metric("🍚 CARB", f"{m['macros_totales']['c']}g")
        col4.metric("🥑 GRAS", f"{m['macros_totales']['f']}g")
        st.divider()

        if st.button("🔄 Nuevo Menú ON"):
            st.session_state.menu_on = crear_menu_diario(st.session_state.macros_on, prohibidos)
            st.session_state.lista_compra = generar_lista_compra_inteligente(st.session_state.menu_on, st.session_state.menu_off, dias_entreno)
            st.rerun()
            
        for comida, datos in st.session_state.menu_on.items():
            with st.expander(f"🍽️ {comida}"):
                for item in datos['items']:
                    st.write(f"• **{item['nombre']}**: {item['gramos_peso']}g")
                st.caption(f"Kcal: {int(datos['totales']['kcal'])} | P:{int(datos['totales']['p'])} C:{int(datos['totales']['c'])} F:{int(datos['totales']['f'])}")

    # 3. DÍA OFF (MACROS ARREGLADOS)
    with tabs[2]:
        m = st.session_state.macros_off
        # BLOQUE DE MACROS VISIBLE ARRIBA
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💤 KCAL", int(m['total']))
        col2.metric("🥩 PROT", f"{m['macros_totales']['p']}g")
        col3.metric("🥦 CARB", f"{m['macros_totales']['c']}g")
        col4.metric("🥑 GRAS", f"{m['macros_totales']['f']}g")
        st.divider()

        if st.button("🔄 Nuevo Menú OFF"):
            st.session_state.menu_off = crear_menu_diario(st.session_state.macros_off, prohibidos)
            st.session_state.lista_compra = generar_lista_compra_inteligente(st.session_state.menu_on, st.session_state.menu_off, dias_entreno)
            st.rerun()
            
        for comida, datos in st.session_state.menu_off.items():
            with st.expander(f"🍽️ {comida}"):
                for item in datos['items']:
                    st.write(f"• **{item['nombre']}**: {item['gramos_peso']}g")
                st.caption(f"Kcal: {int(datos['totales']['kcal'])} | P:{int(datos['totales']['p'])} C:{int(datos['totales']['c'])} F:{int(datos['totales']['f'])}")

    with tabs[3]:
        st.header("🛒 Lista Semanal")
        lista = st.session_state.lista_compra
        if lista:
            for item, cantidad in sorted(lista.items()):
                if cantidad > 0: st.checkbox(f"**{item}**: {int(cantidad)}g")
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
