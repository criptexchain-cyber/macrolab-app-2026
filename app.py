import streamlit as st
import datetime
import random
import copy
import urllib.parse
from collections import defaultdict

# --- 1. CONFIGURACIÓN ---
try:
    st.set_page_config(page_title="MacroLab", page_icon="🔬", layout="wide")
except:
    pass

ID_AFILIADO = "criptex02-21"

# --- 2. BASE DE DATOS (COMPLETA) ---
DB = [
    {"n": "Pechuga Pollo", "t": "prot", "perf": "salado", "m": {"p": 23, "c": 0, "f": 1}},
    {"n": "Ternera Magra", "t": "prot", "perf": "salado", "m": {"p": 20, "c": 0, "f": 5}},
    {"n": "Merluza", "t": "prot", "perf": "salado", "m": {"p": 17, "c": 0, "f": 2}},
    {"n": "Huevos L", "t": "prot", "perf": "salado", "m": {"p": 13, "c": 1, "f": 11}},
    {"n": "Claras Huevo", "t": "prot", "perf": "neutro", "m": {"p": 11, "c": 0, "f": 0}},
    {"n": "Atún Natural", "t": "prot", "perf": "salado", "m": {"p": 24, "c": 0, "f": 1}},
    {"n": "Whey Protein", "t": "prot", "perf": "dulce", "m": {"p": 80, "c": 5, "f": 2}},
    {"n": "Yogur Griego", "t": "prot", "perf": "dulce", "m": {"p": 10, "c": 4, "f": 0}},
    {"n": "Arroz Blanco", "t": "carb", "perf": "neutro", "m": {"p": 2, "c": 28, "f": 0}},
    {"n": "Pasta Integ.", "t": "carb", "perf": "salado", "m": {"p": 5, "c": 25, "f": 1}},
    {"n": "Patata", "t": "carb", "perf": "salado", "m": {"p": 2, "c": 17, "f": 0}},
    {"n": "Avena", "t": "carb", "perf": "dulce", "m": {"p": 4, "c": 12, "f": 1}},
    {"n": "Pan Integral", "t": "carb", "perf": "neutro", "m": {"p": 4, "c": 15, "f": 1}},
    {"n": "Fruta", "t": "carb", "perf": "dulce", "m": {"p": 0, "c": 12, "f": 0}},
    {"n": "Aceite Oliva", "t": "fat", "perf": "salado", "m": {"p": 0, "c": 0, "f": 100}},
    {"n": "Aguacate", "t": "fat", "perf": "salado", "m": {"p": 2, "c": 9, "f": 15}},
    {"n": "Frutos Secos", "t": "fat", "perf": "neutro", "m": {"p": 5, "c": 5, "f": 25}},
    {"n": "Crema Cacahuete", "t": "fat", "perf": "dulce", "m": {"p": 8, "c": 6, "f": 16}}
]

# --- 3. LÓGICA NUTRICIONAL ---
def get_alimento(tipo, gramos, perfil, ban=[]):
    # Filtro avanzado
    lista = [x for x in DB if x['t'] == tipo]
    if "leche" in ban: lista = [x for x in lista if "Yogur" not in x['n'] and "Whey" not in x['n']]
    if "huevo" in ban: lista = [x for x in lista if "Huevo" not in x['n'] and "Clara" not in x['n']]
    if "gluten" in ban: lista = [x for x in lista if x['n'] not in ["Pasta Integ.", "Pan Integral", "Avena"]]
    if "pescado" in ban: lista = [x for x in lista if x['n'] not in ["Merluza", "Atún Natural"]]
    
    # Filtro sabor
    if perfil != "neutro":
        lista = [x for x in lista if x['perf'] in [perfil, "neutro"]]
        
    if not lista: return None
    elegido = random.choice(lista)
    macro_base = elegido['m'][tipo[0]] # 'p', 'c' o 'f'
    if macro_base == 0: return None
    
    peso_final = (gramos * 100) / macro_base
    return {"n": elegido['n'], "g": int(peso_final)}

def generar_menu(macros, ban=[]):
    menu = {}
    nombres_comidas = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena", "Recena"]
    # Repartir macros entre comidas
    n = len(macros['comidas'])
    names = nombres_comidas[:n]
    
    for i, nombre in enumerate(names):
        target = macros['comidas'][f"c{i+1}"]
        items = []
        es_dulce = nombre in ["Desayuno", "Merienda", "Recena"]
        perf = "dulce" if es_dulce else "salado"
        
        # 1. Proteina
        p = get_alimento("prot", target['p'], perf, ban)
        if p: items.append(p)
        # 2. Carb
        c = get_alimento("carb", target['c'], perf, ban)
        if c: items.append(c)
        # 3. Grasa
        f = get_alimento("fat", target['f'], perf, ban)
        if f: items.append(f)
        
        menu[nombre] = items
    return menu

def calcular_plan(p):
    # Formulas Harris-Benedict
    if p['sexo'] == 'Hombre': 
        tmb = (10*p['peso']) + (6.25*p['altura']) - (5*p['edad']) + 5
    else: 
        tmb = (10*p['peso']) + (6.25*p['altura']) - (5*p['edad']) - 161
        
    tdee = tmb * p['actividad']
    
    # Ajuste objetivo
    adj = 0
    if "Perder" in p['obj']: adj = -400
    elif "Ganar" in p['obj']: adj = 350
    
    kcal_base = tdee + adj
    prot = 2.2 * p['peso']
    fat = 0.9 * p['peso']
    carb = (kcal_base - (prot*4) - (fat*9)) / 4
    
    # Distribucion comidas
    dist = {}
    for i in range(p['n_comidas']):
        dist[f"c{i+1}"] = {
            'p': int(prot / p['n_comidas']),
            'c': int(carb / p['n_comidas']),
            'f': int(fat / p['n_comidas'])
        }
        
    return {
        'total': int(kcal_base),
        'macros': {'p': int(prot), 'c': int(carb), 'f': int(fat)},
        'comidas': dist
    }

def calcular_off(plan_on):
    # Reducción para dias de descanso
    res = copy.deepcopy(plan_on)
    res['total'] = int(res['total'] * 0.85) # -15% kcal
    res['macros']['c'] = int(res['macros']['c'] * 0.6) # -40% carbs
    
    # Ajustar en cada comida
    for k in res['comidas']:
        res['comidas'][k]['c'] = int(res['comidas'][k]['c'] * 0.6)
        
    return res

def generar_rutina(dias, nivel):
    # Lógica de ejercicios simple
    rutina = {}
    ejercicios = {
        "A": ["Sentadilla", "Press Banca", "Remo Barra", "Press Militar"],
        "B": ["Peso Muerto", "Prensa", "Jalón Pecho", "Elev. Laterales"],
        "C": ["Zancadas", "Fondos", "Curl Bíceps", "Extensión Tríceps"]
    }
    series = "3" if nivel == "Principiante" else "4"
    
    letras = ["A", "B", "C", "A", "B", "C"]
    for i in range(dias):
        letra = letras[i % 3]
        lista = []
        for ej in ejercicios[letra]:
            lista.append({
                "Ejercicio": ej, 
                "Series": series, 
                "Reps": "8-12", 
                "RIR": "2"
            })
        rutina[f"Día {i+1} (Sesión {letra})"] = lista
    return rutina

# --- 4. INTERFAZ ---
if 'state' not in st.session_state: 
    st.session_state.state = False

# SIDEBAR
with st.sidebar:
    st.header("👤 Datos")
    c1, c2 = st.columns(2)
    peso = c1.number_input("Peso", 40, 150, 75)
    altura = c2.number_input("Altura", 120, 220, 175)
    edad = c1.number_input("Edad", 15, 80, 25)
    sexo = c2.selectbox("Sexo", ["Hombre", "Mujer"])
    
    act_opts = {"Sedentario": 1.2, "Ligero": 1.375, "Moderado": 1.55, "Activo": 1.725}
    act = st.selectbox("Actividad", list(act_opts.keys()))
    obj = st.selectbox("Objetivo", ["Perder Grasa", "Ganar Músculo", "Mantener"])
    
    st.markdown("---")
    st.caption("⚙️ Configuración")
    dias = st.slider("Días Gym", 1, 6, 4)
    nivel = st.selectbox("Nivel", ["Principiante", "Intermedio", "Avanzado"])
    estra = st.radio("Estrategia", ["Lineal (Estable)", "Ciclado (ON/OFF)"])
    n_com = st.number_input("Comidas", 2, 6, 4)
    ban = st.multiselect("No comer", ["leche", "gluten", "pescado", "huevo"])
    
    if st.button("🚀 GENERAR PLAN", use_container_width=True):
        st.session_state.state = True
        
        # 1. Cálculos
        datos = {'peso':peso, 'altura':altura, 'edad':edad, 'sexo':sexo, 
                 'actividad':act_opts[act], 'obj':obj, 'n_comidas':n_com}
        
        plan_base = calcular_plan(datos)
        
        if "Lineal" in estra:
            st.session_state.m_on = plan_base
            st.session_state.m_off = plan_base # Iguales
        else:
            st.session_state.m_on = plan_base
            st.session_state.m_off = calcular_off(plan_base) # Diferentes
            
        # 2. Generar Menus
        st.session_state.d_on = generar_menu(st.session_state.m_on, ban)
        st.session_state.d_off = generar_menu(st.session_state.m_off, ban)
        
        # 3. Rutina
        st.session_state.rut = generar_rutina(dias, nivel)
        st.session_state.dias_entreno = dias # Guardar para lista compra

    st.write("")
    with st.expander("🏪 TIENDA FITNESS"):
        # Enlaces seguros por partes
        base = "https://www.amazon.es/s?k="
        tag = "&tag=" + ID_AFILIADO
        
        st.link_button("🥛 Proteína Whey", base + "proteina+whey" + tag)
        st.link_button("💎 Proteína ISO", base + "proteina+iso" + tag)
        st.link_button("⚡ Creatina", base + "creatina" + tag)
        st.link_button("🐟 Omega 3", base + "omega+3" + tag)
        st.link_button("💊 Multivitaminas", base + "multivitaminas" + tag)
        st.link_button("🏋️ Mancuernas", base + "mancuernas" + tag)

# PANEL PRINCIPAL
if not st.session_state.state:
    st.title("🔬 MacroLab")
    st.info("👈 Rellena tus datos en el menú lateral para empezar.")
else:
    st.title("🔬 Panel de Control")
    
    # PESTAÑAS (Siempre visibles para evitar errores)
    tabs = st.tabs(["🏋️ RUTINA", "🔥 DÍA ON", "💤 DÍA OFF", "🛒 LISTA", "📤 EXPORTAR"])
    
    # 1. RUTINA
    with tabs[0]:
        for dia, ejer in st.session_state.rut.items():
            with st.expander(dia):
                st.dataframe(ejer, hide_index=True, use_container_width=True)
                
    # 2. DIA ON
    with tabs[1]:
        m = st.session_state.m_on
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("KCAL", m['total'])
        c2.metric("PROT", f"{m['macros']['p']}g")
        c3.metric("CARB", f"{m['macros']['c']}g")
        c4.metric("GRAS", f"{m['macros']['f']}g")
        st.divider()
        
        if st.button("🔄 Nuevo Menú ON"):
            st.session_state.d_on = generar_menu(st.session_state.m_on, ban)
            st.rerun()
            
        for nom, items in st.session_state.d_on.items():
            with st.expander(f"🍽️ {nom}"):
                for i in items: st.write(f"• **{i['n']}**: {i['g']}g")

    # 3. DIA OFF
    with tabs[2]:
        m = st.session_state.m_off
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("KCAL", m['total'])
        c2.metric("PROT", f"{m['macros']['p']}g")
        c3.metric("CARB", f"{m['macros']['c']}g")
        c4.metric("GRAS", f"{m['macros']['f']}g")
        st.divider()
        
        if st.button("🔄 Nuevo Menú OFF"):
            st.session_state.d_off = generar_menu(st.session_state.m_off, ban)
            st.rerun()
            
        for nom, items in st.session_state.d_off.items():
            with st.expander(f"🍽️ {nom}"):
                for i in items: st.write(f"• **{i['n']}**: {i['g']}g")

    # 4. LISTA
    with tabs[3]:
        st.header("🛒 Lista de la Compra")
        compra = defaultdict(int)
        dias_gym = st.session_state.dias_entreno
        dias_rest = 7 - dias_gym
        
        # Sumar ON
        for plato in st.session_state.d_on.values():
            for ing in plato: compra[ing['n']] += (ing['g'] * dias_gym)
            
        # Sumar OFF
        for plato in st.session_state.d_off.values():
            for ing in plato: compra[ing['n']] += (ing['g'] * dias_rest)
            
        for k, v in sorted(compra.items()):
            st.checkbox(f"**{k}**: {v}g")

    # 5. EXPORTAR
    with tabs[4]:
        st.header("📤 Compartir Plan")
        
        # Generar texto plano
        txt = "*🧬 PLAN MACROLAB*\n\n"
        txt += "*🏋️ RUTINA SEMANAL*\n"
        for d, e in st.session_state.rut.items():
            txt += f"\n📌 {d}\n"
            for x in e: txt += f"- {x['Ejercicio']} ({x['Series']}x{x['Reps']})\n"
            
        txt += "\n*🔥 DIETA ON*\n"
        for k, v in st.session_state.d_on.items():
            txt += f"_{k}_: " + ", ".join([f"{x['n']} {x['g']}g" for x in v]) + "\n"
            
        txt += "\n*💤 DIETA OFF*\n"
        for k, v in st.session_state.d_off.items():
            txt += f"_{k}_: " + ", ".join([f"{x['n']} {x['g']}g" for x in v]) + "\n"
            
        st.text_area("Texto para copiar", txt, height=250)
        
        # Botones seguros
        safe_txt = urllib.parse.quote(txt)
        link_w = "https://api.whatsapp.com/send?text=" + safe_txt
        link_m = "mailto:?subject=Plan%20MacroLab&body=" + safe_txt
        
        c1, c2 = st.columns(2)
        c1.link_button("📱 WhatsApp", link_w, use_container_width=True)
        c2.link_button("📧 Email", link_m, use_container_width=True)