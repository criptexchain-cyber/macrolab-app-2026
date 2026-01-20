import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import copy
import os
import urllib.parse
from collections import defaultdict

# --- CONFIGURACIÓN DE PÁGINA Y SEO ---
TITULO_SEO = "MacroLab - Entrenador y Nutricionista Inteligente"
ICONO = "🔬"

try:
    st.set_page_config(page_title=TITULO_SEO, page_icon=ICONO, layout="wide")
except:
    pass

# --- 1. MOTORES DE LÓGICA (CEREBRO) ---

def calcular_macros(perfil):
    # Mifflin-St Jeor
    peso, altura, edad = perfil['weight'], perfil['height'], perfil['age']
    genero, actividad = perfil['gender'], perfil['activity']
    
    if genero == 'male':
        tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
    else:
        tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161
        
    tdee = tmb * actividad
    
    # Ajuste por objetivo
    goal = perfil['goal']
    if goal == '1': target_kcal = tdee - 400  # Perder
    elif goal == '2': target_kcal = tdee + 300 # Ganar
    else: target_kcal = tdee # Mantener
    
    # Reparto de Macros Estándar
    prot_g = 2.0 * peso # 2g por kg
    fat_g = 0.9 * peso  # 0.9g por kg
    
    kcal_p = prot_g * 4
    kcal_f = fat_g * 9
    rem_kcal = target_kcal - kcal_p - kcal_f
    carb_g = rem_kcal / 4
    
    # Estructura de comidas
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

def generar_rutina_inteligente(perfil):
    dias = perfil['dias_entreno']
    nivel = perfil['nivel'] # Principiante, Intermedio, Avanzado
    
    # Configuración por Nivel
    config_nivel = {
        "Principiante": {"rir": "3-4", "volumen_factor": 0.7, "tempo_base": "2-0-2-0"},
        "Intermedio":   {"rir": "2-3", "volumen_factor": 1.0, "tempo_base": "3-0-1-0"},
        "Avanzado":     {"rir": "1-2", "volumen_factor": 1.3, "tempo_base": "3-1-X-0"}
    }
    
    cfg = config_nivel.get(nivel, config_nivel["Intermedio"])
    
    # Base de Datos de Ejercicios con Grupo Muscular
    db_ejercicios = {
        "Sentadilla": {"grupo": "Cuádriceps", "tipo": "Multiarticular"},
        "Prensa Inclinada": {"grupo": "Cuádriceps", "tipo": "Máquina"},
        "Peso Muerto Rumano": {"grupo": "Isquios", "tipo": "Multiarticular"},
        "Curl Femoral": {"grupo": "Isquios", "tipo": "Aislamiento"},
        "Press Banca": {"grupo": "Pectoral", "tipo": "Multiarticular"},
        "Press Inclinado Mancuernas": {"grupo": "Pectoral", "tipo": "Multiarticular"},
        "Remo con Barra": {"grupo": "Espalda", "tipo": "Multiarticular"},
        "Jalón al Pecho": {"grupo": "Espalda", "tipo": "Máquina"},
        "Press Militar": {"grupo": "Hombro", "tipo": "Multiarticular"},
        "Elevaciones Laterales": {"grupo": "Hombro", "tipo": "Aislamiento"},
        "Curl de Bíceps": {"grupo": "Bíceps", "tipo": "Aislamiento"},
        "Extensiones Tríceps": {"grupo": "Tríceps", "tipo": "Aislamiento"},
        "Plancha Abdominal": {"grupo": "Core", "tipo": "Isométrico"},
        "Face Pull": {"grupo": "Hombro Post.", "tipo": "Accesorio"}
    }

    # Estructuras de Rutina (Full Body o Torso/Pierna según días)
    estructura = {}
    
    if dias <= 3:
        estructura = {
            "Día A (Full Body)": ["Sentadilla", "Press Banca", "Remo con Barra", "Press Militar", "Curl de Bíceps"],
            "Día B (Full Body)": ["Peso Muerto Rumano", "Prensa Inclinada", "Jalón al Pecho", "Elevaciones Laterales", "Extensiones Tríceps"],
            "Día C (Full Body)": ["Sentadilla", "Press Inclinado Mancuernas", "Remo con Barra", "Face Pull", "Plancha Abdominal"]
        }
    else:
        estructura = {
            "Día A (Torso Fuerza)": ["Press Banca", "Remo con Barra", "Press Militar", "Elevaciones Laterales", "Extensiones Tríceps"],
            "Día B (Pierna Fuerza)": ["Sentadilla", "Peso Muerto Rumano", "Prensa Inclinada", "Curl Femoral", "Plancha Abdominal"],
            "Día C (Torso Hipertrofia)": ["Press Inclinado Mancuernas", "Jalón al Pecho", "Elevaciones Laterales", "Curl de Bíceps", "Face Pull"],
            "Día D (Pierna Hipertrofia)": ["Prensa Inclinada", "Sentadilla", "Curl Femoral", "Peso Muerto Rumano", "Plancha Abdominal"]
        }
        if dias >= 5: estructura["Día E (Brazo/Hombro)"] = ["Press Militar", "Elevaciones Laterales", "Curl de Bíceps", "Extensiones Tríceps", "Face Pull"]
        if dias == 6: estructura["Día F (Recordatorios)"] = ["Sentadilla", "Press Banca", "Jalón al Pecho", "Plancha Abdominal"]

    # Generación de la Rutina Detallada
    rutina_final = {'sesiones': {}, 'volumen_total': defaultdict(int)}
    
    # Seleccionamos solo los días necesarios
    dias_activos = list(estructura.keys())[:dias]
    
    for nombre_dia in dias_activos:
        lista_ejercicios = estructura[nombre_dia]
        detalles_dia = []
        
        for ej_nombre in lista_ejercicios:
            datos_ej = db_ejercicios.get(ej_nombre, {"grupo": "General", "tipo": "Accesorio"})
            
            # Lógica de Series y Repes según Nivel y Tipo
            if datos_ej['tipo'] == "Multiarticular":
                series = 3 if nivel == "Principiante" else 4
                repes = "6-8"
            elif datos_ej['tipo'] == "Máquina":
                series = 3
                repes = "10-12"
            else: # Aislamiento
                series = 2 if nivel == "Principiante" else 3
                repes = "12-15"
            
            # Contabilizar Volumen Efectivo
            rutina_final['volumen_total'][datos_ej['grupo']] += series
            
            detalles_dia.append({
                'nombre': ej_nombre,
                'grupo': datos_ej['grupo'],
                'series': series,
                'repes': repes,
                'rir': cfg['rir'],
                'tempo': cfg['tempo_base'],
                'tips': f"Enfoca en {datos_ej['grupo']}"
            })
            
        rutina_final['sesiones'][nombre_dia] = detalles_dia
        
    return rutina_final

# --- 2. FUNCIONES AUXILIARES (Texto, Cálculo, Etc) ---
def calcular_horas_sueno(hora_bed, hora_wake):
    try:
        t1 = datetime.datetime.strptime(str(hora_bed), "%H:%M:%S").time()
        t2 = datetime.datetime.strptime(str(hora_wake), "%H:%M:%S").time()
        dummy_date = datetime.date(2000, 1, 1)
        dt1 = datetime.datetime.combine(dummy_date, t1)
        dt2 = datetime.datetime.combine(dummy_date, t2)
        if dt2 < dt1: dt2 += datetime.timedelta(days=1)
        return round((dt2 - dt1).total_seconds() / 3600, 1)
    except: return 0.0

def calcular_macros_descanso(res_entreno):
    res = copy.deepcopy(res_entreno)
    res['total'] = res['total'] * 0.85 # 15% menos kcal
    res['macros_totales']['c'] = int(res['macros_totales']['c'] * 0.6) # Bajada de carbos
    return res

def generar_texto_copiable(rutina, menu_on, menu_off):
    txt = "*🧬 PLAN MACROLAB*\n\n"
    txt += "*🏋️ RUTINA SEMANAL*\n"
    for dia, ejercicios in rutina.get('sesiones', {}).items():
        txt += f"\n📌 *{dia.upper()}*\n"
        for ej in ejercicios:
            txt += f"- {ej['nombre']} | {ej['series']}x{ej['repes']} | RIR: {ej['rir']} | Tempo: {ej['tempo']}\n"
    
    txt += "\n*📊 VOLUMEN SEMANAL (Series Efectivas)*\n"
    for grupo, series in rutina.get('volumen_total', {}).items():
        txt += f"- {grupo}: {series} series\n"
            
    return txt

# --- 3. INTERFAZ (FRONTEND) ---

# Estado de sesión
if 'generado' not in st.session_state: st.session_state.generado = False
if 'rutina' not in st.session_state: st.session_state.rutina = {}
if 'perfil' not in st.session_state: st.session_state.perfil = {}

# BARRA LATERAL
with st.sidebar:
    st.header("👤 Tus Datos")
    
    col1, col2 = st.columns(2)
    peso = col1.number_input("Peso (kg)", 40.0, 160.0, 75.0, 0.1)
    altura = col2.number_input("Altura (cm)", 120.0, 230.0, 175.0)
    edad = col1.number_input("Edad", 12, 90, 25)
    genero = col2.selectbox("Género", ["Hombre", "Mujer"])
    genero_val = "male" if genero == "Hombre" else "female"

    st.subheader("🔥 Nivel y Actividad")
    act_map = {"Sedentario": 1.2, "Ligero": 1.375, "Moderado": 1.55, "Activo": 1.725}
    actividad = act_map[st.selectbox("Actividad Diaria", list(act_map.keys()))]
    
    obj_txt = st.selectbox("Objetivo", ["1. Perder Grasa", "2. Ganar Músculo", "3. Mantener"])
    
    # --- NUEVO: SELECTOR DE NIVEL ---
    st.markdown("---")
    st.caption("🏋️ Configuración Gym")
    dias_entreno = st.slider("Días Gym/Semana", 0, 6, 4)
    nivel_exp = st.selectbox("Nivel de Experiencia", ["Principiante", "Intermedio", "Avanzado"])
    hora_entreno = st.time_input("Hora Entreno", datetime.time(18, 00))
    st.markdown("---")
    
    st.subheader("🍽️ Dieta")
    n_comidas = st.number_input("Comidas/día", 2, 6, 4)
    hora_bed = st.time_input("Hora Dormir", datetime.time(23, 0))
    hora_wake = st.time_input("Hora Despertar", datetime.time(7, 30))

    if st.button("🚀 INICIAR LABORATORIO", use_container_width=True):
        st.session_state.generado = True
        perfil = {
            "weight": peso, "height": altura, "age": int(edad), "gender": genero_val,
            "goal": obj_txt[0], "activity": actividad, "num_comidas": n_comidas,
            "dias_entreno": dias_entreno, "nivel": nivel_exp
        }
        st.session_state.perfil = perfil
        st.session_state.macros_on = calcular_macros(perfil)
        st.session_state.macros_off = calcular_macros_descanso(st.session_state.macros_on)
        
        if dias_entreno > 0:
            st.session_state.rutina = generar_rutina_inteligente(perfil)
        else:
            st.session_state.rutina = {'sesiones': {}, 'volumen_total': {}}

# PANTALLA PRINCIPAL
if not st.session_state.generado:
    st.title("🔬 MacroLab")
    st.markdown("### Sistema de Entrenamiento y Nutrición de Precisión")
    st.info("👈 Configura tu perfil en la izquierda para empezar.")
    
    # Footer SEO
    st.divider()
    with st.expander("🔍 ¿Cómo funciona MacroLab?"):
        st.write("Calculadora científica de macros y generador de rutinas con periodización.")

else:
    # Header
    st.title("🔬 Panel de Control")
    st.markdown("---")
    
    t_rutina, t_dieta, t_share = st.tabs(["🏋️ RUTINA INTELIGENTE", "🍽️ DIETA", "📤 EXPORTAR"])
    
    with t_rutina:
        rut = st.session_state.rutina
        
        if not rut['sesiones']:
            st.warning("Selecciona al menos 1 día de entreno para ver rutinas.")
        else:
            col_info1, col_info2 = st.columns(2)
            col_info1.info(f"**Nivel:** {st.session_state.perfil['nivel']}")
            col_info2.info(f"**Objetivo:** {obj_txt.split('.')[1]}")
            
            for dia, ejercicios in rut['sesiones'].items():
                with st.expander(f"📌 {dia}", expanded=True):
                    # CABECERA DE LA TABLA
                    cols = st.columns([3, 1, 1, 1, 1])
                    cols[0].markdown("**Ejercicio**")
                    cols[1].markdown("**Series**")
                    cols[2].markdown("**Repes**")
                    cols[3].markdown("**RIR**")
                    cols[4].markdown("**Tempo**")
                    st.divider()
                    
                    # EJERCICIOS
                    for ej in ejercicios:
                        c = st.columns([3, 1, 1, 1, 1])
                        c[0].write(ej['nombre'])
                        c[1].write(f"{ej['series']}")
                        c[2].write(ej['repes'])
                        c[3].write(ej['rir'])
                        c[4].write(ej['tempo'])
            
            # --- TABLA DE VOLUMEN SEMANAL ---
            st.markdown("### 📊 Volumen Semanal (Series Efectivas)")
            st.caption("Esta tabla te muestra si estás entrenando equilibrado.")
            
            volumen = rut['volumen_total']
            # Convertimos a lista para mostrar bonito
            datos_vol = [{"Grupo Muscular": k, "Series Totales": v} for k, v in volumen.items()]
            st.dataframe(datos_vol, use_container_width=True)

    with t_dieta:
        m_on = st.session_state.macros_on
        st.subheader("🔥 Día de Entrenamiento")
        c1, c2, c3 = st.columns(3)
        c1.metric("Proteína", f"{m_on['macros_totales']['p']} g")
        c2.metric("Carbos", f"{m_on['macros_totales']['c']} g")
        c3.metric("Grasas", f"{m_on['macros_totales']['f']} g")
        st.metric("Kcal Totales", int(m_on['total']))

    with t_share:
        st.subheader("📋 Texto para Copiar")
        txt_final = generar_texto_copiable(st.session_state.rutina, {}, {})
        st.code(txt_final)

# --- TIENDA (FINAL) ---
st.divider()
with st.expander("🏪 TIENDA FITNESS"):
    st.write("Equipamiento recomendado: Proteína, Creatina, Mancuernas...")
    st.link_button("Ir a Amazon", "https://www.amazon.es/s?k=proteina&tag=criptex02-21")
