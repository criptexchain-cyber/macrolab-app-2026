import random

# --- BASE DE DATOS DE EJERCICIOS (INTEGRADA) ---
DB_EJERCICIOS = {
    "pecho": [
        {"nombre": "Press Banca con Barra", "tipo": "compuesto", "nivel": 1, "tips": "Barra al esternón, codos a 45º."},
        {"nombre": "Press Inclinado Mancuernas", "tipo": "compuesto", "nivel": 1, "tips": "Banco a 30º, controla la bajada."},
        {"nombre": "Fondos en Paralelas", "tipo": "compuesto", "nivel": 2, "tips": "Inclínate adelante para enfatizar pecho."},
        {"nombre": "Aperturas con Mancuernas", "tipo": "aislamiento", "nivel": 1, "tips": "Imagina abrazar un árbol, estira bien."},
        {"nombre": "Cruce de Poleas", "tipo": "aislamiento", "nivel": 2, "tips": "Aprieta un segundo en el punto de máxima contracción."},
        {"nombre": "Flexiones (Push-ups)", "tipo": "compuesto", "nivel": 1, "tips": "Cuerpo en tabla, pecho al suelo."}
    ],
    "espalda": [
        {"nombre": "Dominadas", "tipo": "compuesto", "nivel": 2, "tips": "Rango completo, pecho a la barra."},
        {"nombre": "Remo con Barra", "tipo": "compuesto", "nivel": 2, "tips": "Espalda recta, tira hacia la cadera."},
        {"nombre": "Jalón al Pecho", "tipo": "compuesto", "nivel": 1, "tips": "No te balancees, codos hacia abajo."},
        {"nombre": "Remo Gironda (Polea Baja)", "tipo": "compuesto", "nivel": 1, "tips": "Saca pecho, aprieta escápulas atrás."},
        {"nombre": "Pull Over en Polea", "tipo": "aislamiento", "nivel": 2, "tips": "Brazos semirrígidos, siente el dorsal."},
        {"nombre": "Remo Unilateral con Mancuerna", "tipo": "compuesto", "nivel": 1, "tips": "Apóyate en banco, espalda paralela al suelo."}
    ],
    "pierna_quad": [
        {"nombre": "Sentadilla con Barra", "tipo": "compuesto", "nivel": 2, "tips": "Rompe el paralelo, peso en talones."},
        {"nombre": "Prensa de Piernas", "tipo": "compuesto", "nivel": 1, "tips": "No bloquees rodillas al extender."},
        {"nombre": "Zancadas (Lunges)", "tipo": "compuesto", "nivel": 1, "tips": "Rodilla trasera casi toca el suelo."},
        {"nombre": "Sentadilla Búlgara", "tipo": "compuesto", "nivel": 3, "tips": "Inclínate un poco, infierno para glúteo/quad."},
        {"nombre": "Extensiones de Cuádriceps", "tipo": "aislamiento", "nivel": 1, "tips": "Aguanta 1 segundo arriba."}
    ],
    "pierna_femoral": [
        {"nombre": "Peso Muerto Rumano", "tipo": "compuesto", "nivel": 2, "tips": "Cadera atrás, siente el estiramiento."},
        {"nombre": "Curl Femoral Tumbado", "tipo": "aislamiento", "nivel": 1, "tips": "No levantes la cadera del banco."},
        {"nombre": "Hip Thrust", "tipo": "compuesto", "nivel": 2, "tips": "Mentón al pecho, empuja con talones."},
        {"nombre": "Peso Muerto Piernas Rígidas", "tipo": "compuesto", "nivel": 2, "tips": "Enfoque total en isquios."}
    ],
    "hombro": [
        {"nombre": "Press Militar (Barra/Mancuerna)", "tipo": "compuesto", "nivel": 2, "tips": "Core apretado, no arquees espalda excesivamente."},
        {"nombre": "Elevaciones Laterales", "tipo": "aislamiento", "nivel": 1, "tips": "Codos lideran el movimiento, no muñecas."},
        {"nombre": "Pájaros (Deltoides Posterior)", "tipo": "aislamiento", "nivel": 1, "tips": "Torso paralelo al suelo o en máquina."},
        {"nombre": "Face Pull", "tipo": "funcional", "nivel": 1, "tips": "Tira hacia la frente, rotación externa."}
    ],
    "biceps": [
        {"nombre": "Curl con Barra Z", "tipo": "aislamiento", "nivel": 1, "tips": "Codos pegados al cuerpo."},
        {"nombre": "Curl Martillo", "tipo": "aislamiento", "nivel": 1, "tips": "Agarre neutro, enfoca braquial."},
        {"nombre": "Curl Inclinado Mancuernas", "tipo": "aislamiento", "nivel": 2, "tips": "Estiramiento máximo del bíceps."}
    ],
    "triceps": [
        {"nombre": "Press Francés", "tipo": "aislamiento", "nivel": 2, "tips": "Codos cerrados, barra a la frente."},
        {"nombre": "Extensiones Polea Alta", "tipo": "aislamiento", "nivel": 1, "tips": "Hombros fijos, solo mueve antebrazo."},
        {"nombre": "Fondos entre Bancos", "tipo": "aislamiento", "nivel": 1, "tips": "Baja controlado."}
    ],
    "abs": [
        {"nombre": "Plancha Abdominal (Plank)", "tipo": "funcional", "nivel": 1, "tips": "Cuerpo recto, aprieta glúteo y abdomen."},
        {"nombre": "Elevación de Piernas Colgado", "tipo": "funcional", "nivel": 2, "tips": "No te balancees, controla la bajada."},
        {"nombre": "Crunch en Polea", "tipo": "aislamiento", "nivel": 1, "tips": "No tires con los brazos, enrolla el tronco."},
        {"nombre": "Rueda Abdominal", "tipo": "funcional", "nivel": 3, "tips": "Solo baja hasta donde puedas volver con abs."}
    ]
}

# --- LÓGICA DEL ENTRENADOR ---

def seleccionar_ejercicios(grupo, n, nivel_usuario):
    pool = DB_EJERCICIOS.get(grupo, [])
    # Filtrar por complejidad si es novato (nivel 1)
    if nivel_usuario == "1":
        pool = [e for e in pool if e['nivel'] <= 2]
    
    random.shuffle(pool)
    return pool[:n]

def generar_rutina(perfil):
    dias = perfil['dias_entreno']
    nivel = perfil['nivel_entreno']
    rutina = {"info": {}, "sesiones": {}}
    
    # ESTRATEGIA SEGÚN DÍAS
    if dias == 3:
        rutina['info']['estrategia'] = "Full Body (Cuerpo Completo)"
        esquema = ["Full Body A", "Full Body B", "Full Body C"]
        for dia_nombre in esquema:
            sesion = []
            sesion.extend(seleccionar_ejercicios("pierna_quad", 1, nivel))
            sesion.extend(seleccionar_ejercicios("pecho", 1, nivel))
            sesion.extend(seleccionar_ejercicios("espalda", 1, nivel))
            sesion.extend(seleccionar_ejercicios("hombro", 1, nivel))
            sesion.extend(seleccionar_ejercicios("pierna_femoral", 1, nivel))
            sesion.extend(seleccionar_ejercicios("abs", 1, nivel))
            
            # Asignar series y repes
            for ej in sesion:
                ej['series_num'] = 3
                ej['repes'] = "8-12" if ej['tipo'] == 'compuesto' else "12-15"
            
            rutina['sesiones'][dia_nombre] = sesion

    elif dias == 4:
        rutina['info']['estrategia'] = "Torso / Pierna (Frecuencia 2)"
        esquema = {"Torso A": ["pecho", "espalda", "hombro", "biceps", "triceps"],
                   "Pierna A": ["pierna_quad", "pierna_femoral", "pierna_quad", "abs"],
                   "Torso B": ["espalda", "pecho", "hombro", "triceps", "biceps"],
                   "Pierna B": ["pierna_femoral", "pierna_quad", "pierna_femoral", "abs"]}
        
        for nombre_sesion, grupos in esquema.items():
            sesion = []
            for g in grupos:
                cant = 2 if g in ["pecho", "espalda"] else 1
                sesion.extend(seleccionar_ejercicios(g, cant, nivel))
            
            for ej in sesion:
                ej['series_num'] = 3 if ej['tipo'] == 'compuesto' else 2
                ej['repes'] = "6-10" if ej['tipo'] == 'compuesto' else "10-15"
                
            rutina['sesiones'][nombre_sesion] = sesion

    elif dias >= 5:
        rutina['info']['estrategia'] = "PPL (Empuje / Tirón / Pierna)"
        esquema = {"Push (Empuje)": ["pecho", "pecho", "hombro", "triceps", "triceps"],
                   "Pull (Tirón)": ["espalda", "espalda", "biceps", "biceps", "hombro"],
                   "Legs (Pierna)": ["pierna_quad", "pierna_femoral", "pierna_quad", "pierna_femoral", "abs"],
                   "Upper (Torso)": ["pecho", "espalda", "hombro", "biceps"],
                   "Lower (Pierna)": ["pierna_quad", "pierna_femoral", "abs"]}
        
        # Ajustar si son 6 días (repetir PPL)
        claves = list(esquema.keys())
        if dias == 6: claves = ["Push A", "Pull A", "Legs A", "Push B", "Pull B", "Legs B"]
        
        count = 0
        for nombre_dia in claves:
            if dias == 5 and count >= 5: break
            
            # Mapeo simple para PPL repetido
            base_dia = nombre_dia.split()[0] # "Push" de "Push A"
            if base_dia == "Upper": grupos = esquema["Upper (Torso)"]
            elif base_dia == "Lower": grupos = esquema["Lower (Pierna)"]
            elif "Push" in nombre_dia: grupos = esquema["Push (Empuje)"]
            elif "Pull" in nombre_dia: grupos = esquema["Pull (Tirón)"]
            elif "Legs" in nombre_dia: grupos = esquema["Legs (Pierna)"]
            else: grupos = []

            sesion = []
            for g in grupos:
                sesion.extend(seleccionar_ejercicios(g, 1, nivel))
            
            for ej in sesion:
                ej['series_num'] = 4 if ej['tipo'] == 'compuesto' else 3
                ej['repes'] = "8-12"
            
            rutina['sesiones'][nombre_dia] = sesion
            count += 1
            
    return rutina
