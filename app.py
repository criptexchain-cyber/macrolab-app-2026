import streamlit as st
import pandas as pd
import datetime
import random
import copy
import urllib.parse
from collections import defaultdict

# --- CONFIGURACIÓN ---
try:
    st.set_page_config(page_title="MacroLab", page_icon="🔬", layout="wide")
except:
    pass

ID_AFILIADO = "criptex02-21"

# ==========================================
# 1. BASE DE DATOS
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

# ==========================================
# 2. FUNCIONES LÓGICAS
# ==========================================
def buscar_alimento(tipo, gramos_macro, perfil_plato, prohibidos=[]):
    candidatos = [a for a in DB_ALIMENTOS if a['tipo'] == tipo]
    
    # Filtros
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
        
        # Selección de alimentos
        sug_p = buscar_alimento('protein', m['prot'], perfil, prohibidos)
        if sug_p:
            items_plato.append(sug_p)
            for k in ['p','c','f']: llevamos[k] += sug_p['macros_reales'].get(k,0)
            
        rest_c = m['carb'] - llevamos['c']
        if rest_c > 5:
            sug_c = buscar_alimento('carbohydrates', rest_c, perfil, prohibidos)
            if sug_c:
                items_plato.append(sug_c)
                for k in ['p','c','f']: llevamos[k] += sug_c['macros_reales'].get(k,0)

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
    
    if menu_on:
        for comida in menu_on.values():
            for item in comida['items']: 
                compra[item['nombre']] += item['gramos_peso'] * dias_entreno
    if menu_off:
        for comida in menu_off.values():
            for item in comida['items']: 
                compra[item['nombre']] += item['gramos_peso'] * dias_descanso
            
    return dict(compra)

def mostrar_encabezado_macros(m, etiqueta_kcal):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(etiqueta_kcal, int(m['total']))
    c2.metric("🥩 PROT", f"{m['macros_totales']['p']}g")
    c3.metric("🍚 CARB", f"{m['macros_totales']['c']}g")
    c4.metric("🥑 GRAS", f"{m['macros_totales']['f']}g")
    st.divider()

# ==========================================
# 3. LÓGICA DE CÁLCULO
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
        distribucion[c] = {'prot': int(prot_g / n_comidas), 'carb': int(carb_g / n_comidas), 'fat': int(fat_g / n_comidas)}
    
    return {'total': target_kcal, 'macros_totales': {'p': int(prot_g), 'c': int(carb_g), 'f': int(fat_g)}, 'comidas': distribucion}

def calcular_macros_descanso(res_entreno):
    res = copy.deepcopy(res_entreno)
    res['total'] = res['total'] * 0.85 
    res['macros_totales']['c'] = int(res['macros_totales']['c'] * 0.6) 
    for c in res['comidas']:
        res['comidas'][c]['carb'] = int(res['comidas'][c]['carb'] * 0.6)
    return res

def calcular_promedio_lineal(m_on, m_off, dias_gym):
    dias_off = 7 - dias_gym
    # Media ponderada para dieta lineal
    kcal_avg = ((m_on['total'] * dias_gym) + (m_off['total'] * dias_off)) / 7
    p_avg = ((m_on['macros_totales']['p'] * dias_gym) + (m_off['macros_totales']['p'] * dias_off)) / 7
    c_avg = ((m_on['macros_totales']['c'] * dias_gym) + (m_off['macros_totales']['c'] * dias_off)) / 7
    f_avg = ((m_on['macros_totales']['f'] * dias_gym) + (m_off['macros_totales']['f'] * dias_off)) / 7
    
    res = copy.deepcopy(m_on)
    res['total'] = int(kcal_avg)
    res['macros_totales'] = {'p': int(p_avg), 'c': int(c_avg), 'f': int(f_avg)}
    
    n_comidas = len(res['comidas'])
    for c in res['comidas']:
        res['comidas'][c] = {'prot': int(p_avg/n_comidas), 'carb': int(c_avg/n_comidas), 'fat': int(f_avg/n_comidas)}
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
            detalles_dia.append({
                "Ejercicio": ej,
                "Sets": str(series),
                "Reps": "8-12",
                "RIR": cfg['rir'],
                "Tempo": cfg['tempo']
            })
        rutina_final['sesiones'][f"Día {i+1} ({nombre_dia})"] = detalles_dia
    return rutina_final

def generar_texto_plano(rutina, menu_on, menu_off, perfil):
    estrategia = perfil.get('estrategia', '')
    txt = "*🧬 PLAN MACROLAB*\n\n"
    txt += "*🏋️ RUTINA SEMANAL*\n"
    for dia, ejercicios in rutina.get('sesiones', {}).items():
        txt += f"\n📌 *{dia.upper()}*\n"
        for ej in ejercicios:
            txt += f"- {ej['Ejercicio']} | {ej['Sets']}x{ej['Reps']} | RIR:{ej['RIR']}\n"
    
    txt += "\n*🔥 DIETA ON (Entreno)*\n"
    if menu_on:
        for comida, datos in menu_on.items():
            txt += f"_{comida}_: "
            items = [f"{i['nombre']} ({i['gramos_peso']}g)" for i in datos['items']]
            txt += ", ".join(items) + "\n"
    
    txt += "\n*💤 DIETA OFF (Descanso)*\n"
    if menu_off:
        for comida, datos in menu_off.items():
            txt += f"_{comida}_: "
            items = [f"{i['nombre']} ({i['gramos_peso']}g)" for i in datos['items']]
            txt += ", ".join(items) + "\n"
            
    return txt

# ==========================================
# 4. INTERFAZ GRÁFICA (FRONTEND)
# ==========================================
if 'generado' not in st.session_state: st.session_state.generado = False
if 'rutina' not in st.session_state: st.session_state.rutina = {}
if 'menu_on' not in st.session_state: st.session_state.menu_on = {}
if 'menu_off' not in st.session_state: st.session_state.menu_off = {}
if 'macros_on' not in st.session_state: st.session_state.macros_on = {}
if 'macros_off' not in st.session_state: st.session_state.macros_off = {}
if 'lista_compra' not in st.session_state: st.session_state.lista_compra = {}

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
    
    st.markdown("---")
    st.caption("🍽️ Configuración Dieta")
    # ✅ SELECTOR DE ESTRATEGIA (LINEAL vs CICLADO)
    estrategia = st.radio("Estrategia Nutricional", ["🌊 Ciclado (Días ON/OFF)", "📏 Lineal (Estable)"])
    n_comidas = st.number_input("Comidas/día", 2, 6, 4)
    prohibidos = st.multiselect("🚫 Alergias", ["leche", "huevo", "gluten", "pescado", "cacahuete"])
    
    if st.button("🚀 INICIAR LABORATORIO", use_container_width=True):
        st.session_state.generado = True
        perfil = {
            "weight": peso, "height": altura, "age": int(edad), 
            "gender": "male" if genero=="Hombre" else "
