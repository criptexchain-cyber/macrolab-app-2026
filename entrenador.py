import random
from database_ejercicios import DB_EJERCICIOS

def obtener_parametros_objetivo(objetivo, nivel):
    if objetivo == '1': return "6-10", "RIR 2", "90-120 seg", "INTENSIDAD"
    elif objetivo == '2': return "8-12", "RIR 1-2", "90 seg", "VOLUMEN"
    else: return "4-6", "RIR 3", "3 min", "FUERZA"

def calcular_volumen(nivel, tipo_ejercicio):
    base = 3
    if nivel == '2': base = 4 
    elif nivel == '3': base = 5 
    if tipo_ejercicio == 'aislamiento': return base
    return base

def asignar_tempo(tipo_ejercicio):
    if tipo_ejercicio == 'multiarticular': return "3-0-1-0" 
    elif tipo_ejercicio == 'aislamiento': return "2-1-1-1" 
    return "2-0-2-0"

def buscar_y_seleccionar(filtro_patron, filtro_tipo, usados):
    candidatos = []
    for key, datos in DB_EJERCICIOS.items():
        if filtro_patron and datos['patron'] != filtro_patron: continue
        if filtro_tipo and datos['tipo'] != filtro_tipo: continue
        if key not in usados: candidatos.append(key)
    
    if not candidatos: return None, None 
    elegido_key = random.choice(candidatos)
    return elegido_key, DB_EJERCICIOS[elegido_key]

def generar_rutina(perfil):
    dias = perfil['dias_entreno']
    objetivo = perfil['goal']
    nivel = perfil['nivel_entreno']
    
    repes_obj, rir_obj, descanso_obj, enfoque = obtener_parametros_objetivo(objetivo, nivel)
    
    rutina_data = {
        "info": {
            "estrategia": enfoque, "dias": dias,
            "pauta_progresion": ["Sube peso cuando llegues al tope de repes.", "Descarga cada 6 semanas."]
        },
        "sesiones": {}
    }

    estructura_nombres = []
    if dias == 3: estructura_nombres = ["FULL BODY A", "FULL BODY B", "FULL BODY C"]
    elif dias == 4: estructura_nombres = ["TORSO (Fuerza)", "PIERNA (Fuerza)", "TORSO (Hipertrofia)", "PIERNA (Hipertrofia)"]
    elif dias == 5: estructura_nombres = ["EMPUJE", "TRACCIÓN", "PIERNA", "TORSO SUPERIOR", "BRAZOS"]
    else: estructura_nombres = ["PUSH A", "PULL A", "LEGS A", "PUSH B", "PULL B", "LEGS B"]

    for dia_nombre in estructura_nombres:
        rutina_data["sesiones"][dia_nombre] = []
        
        # PLANTILLA SIMPLIFICADA PARA EL EJEMPLO
        plantilla = []
        if "FULL BODY" in dia_nombre:
            plantilla = [("sentadilla", "multiarticular"), ("empuje_horizontal", "multiarticular"), ("traccion_vertical", "multiarticular"), ("bisagra_cadera", "accesorio"), ("empuje_vertical", "accesorio"), ("flexion_codo", "aislamiento")]
        elif "TORSO" in dia_nombre or "SUPERIOR" in dia_nombre:
            plantilla = [("empuje_horizontal", "multiarticular"), ("traccion_vertical", "multiarticular"), ("empuje_vertical", "multiarticular"), ("traccion_horizontal", "accesorio"), ("abduccion", "aislamiento"), ("extension_codo", "aislamiento")]
        elif "PIERNA" in dia_nombre or "LEGS" in dia_nombre:
            plantilla = [("sentadilla", "multiarticular"), ("bisagra_cadera", "multiarticular"), ("empuje_pierna", "multiarticular"), ("extension_rodilla", "aislamiento"), ("flexion_rodilla", "aislamiento"), ("extension_cadera", "aislamiento")]
        elif "PUSH" in dia_nombre or "EMPUJE" in dia_nombre:
            plantilla = [("empuje_horizontal", "multiarticular"), ("empuje_vertical", "multiarticular"), ("empuje_inclinado", "accesorio"), ("abduccion", "aislamiento"), ("extension_codo", "aislamiento")]
        elif "PULL" in dia_nombre or "TRACCIÓN" in dia_nombre:
            plantilla = [("traccion_vertical", "multiarticular"), ("traccion_horizontal", "multiarticular"), ("traccion_horizontal", "accesorio"), ("rotacion_externa", "aislamiento"), ("flexion_codo", "aislamiento")]
        elif "BRAZOS" in dia_nombre:
            plantilla = [("flexion_codo", "accesorio"), ("extension_codo", "accesorio"), ("flexion_codo_neutra", "aislamiento"), ("extension_codo", "aislamiento"), ("abduccion", "aislamiento")]

        usados_sesion = [] 
        for patron, tipo_preferido in plantilla:
            key, datos = buscar_y_seleccionar(patron, tipo_preferido, usados_sesion)
            if not key: key, datos = buscar_y_seleccionar(patron, None, usados_sesion)
            
            if key and datos:
                usados_sesion.append(key)
                series_num = calcular_volumen(nivel, datos['tipo'])
                
                # CREAMOS LA INSTRUCCIÓN DE SERIES EN TEXTO CLARO
                instruccion_series = f"Realiza {series_num} series efectivas."
                if datos['tipo'] == 'multiarticular':
                    instruccion_series = f"Haz 3 series de calentamiento (subiendo peso) y luego {series_num} series efectivas."
                
                ejercicio_dict = {
                    "nombre": datos['nombre'],
                    "series_num": series_num, # Guardamos el número limpio
                    "instruccion_series": instruccion_series, # Texto explicativo
                    "repes": repes_obj,
                    "rir": "RIR 0" if datos['tipo'] == 'aislamiento' else rir_obj,
                    "tempo": asignar_tempo(datos['tipo']),
                    "descanso": descanso_obj,
                    "tipo": datos['tipo'],
                    "tips": datos.get('tips', "Realiza el movimiento con control.") # Recuperamos el tip
                }
                rutina_data["sesiones"][dia_nombre].append(ejercicio_dict)

    return rutina_data