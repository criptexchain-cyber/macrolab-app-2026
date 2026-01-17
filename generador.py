import random

# ==============================================================================
# BASE DE DATOS INTELIGENTE (Macros en CRUDO + PERFIL DE SABOR)
# Perfiles: 'salado', 'dulce', 'neutro' (neutro pega con todo)
# ==============================================================================

DB_ALIMENTOS = {
    # --- PROTEÍNAS ---
    "pollo": {"nombre": "Pechuga de Pollo", "p": 23, "c": 0, "f": 1.2, "kcal": 110, "tipo": "protein", "perfil": "salado"},
    "ternera": {"nombre": "Ternera Magra", "p": 20, "c": 0, "f": 5, "kcal": 130, "tipo": "protein", "perfil": "salado"},
    "atun": {"nombre": "Atún al Natural (Lata)", "p": 24, "c": 0, "f": 1, "kcal": 105, "tipo": "protein", "perfil": "salado"},
    "merluza": {"nombre": "Pescado Blanco / Merluza", "p": 18, "c": 0, "f": 0.8, "kcal": 80, "tipo": "protein", "perfil": "salado"},
    "huevos": {"nombre": "Huevos Enteros", "p": 13, "c": 1, "f": 11, "kcal": 155, "tipo": "protein", "perfil": "neutro"},
    "claras": {"nombre": "Claras de Huevo", "p": 11, "c": 0, "f": 0, "kcal": 50, "tipo": "protein", "perfil": "neutro"},
    "salmon": {"nombre": "Salmón", "p": 20, "c": 0, "f": 13, "kcal": 200, "tipo": "protein", "perfil": "salado"},
    "tofu": {"nombre": "Tofu Firme", "p": 15, "c": 2, "f": 8, "kcal": 140, "tipo": "protein", "perfil": "neutro"},
    "lomo": {"nombre": "Lomo Embuchado", "p": 32, "c": 0, "f": 6, "kcal": 190, "tipo": "protein", "perfil": "salado"},
    "proteina_polvo": {"nombre": "Whey Protein (Cazo)", "p": 80, "c": 5, "f": 2, "kcal": 370, "tipo": "protein", "perfil": "dulce"},
    "yogur_griego": {"nombre": "Yogur Griego 0%", "p": 10, "c": 4, "f": 0, "kcal": 59, "tipo": "protein", "perfil": "dulce"},

    # --- CARBOHIDRATOS ---
    "arroz": {"nombre": "Arroz Blanco", "p": 7, "c": 80, "f": 1, "kcal": 360, "tipo": "carbohydrates", "perfil": "salado"},
    "pasta": {"nombre": "Pasta de Trigo", "p": 12, "c": 72, "f": 1.5, "kcal": 360, "tipo": "carbohydrates", "perfil": "salado"},
    "avena": {"nombre": "Copos de Avena", "p": 13, "c": 60, "f": 7, "kcal": 370, "tipo": "carbohydrates", "perfil": "dulce"},
    "patata": {"nombre": "Patata", "p": 2, "c": 17, "f": 0.1, "kcal": 77, "tipo": "carbohydrates", "perfil": "salado"},
    "batata": {"nombre": "Boniato / Batata", "p": 1.6, "c": 20, "f": 0.1, "kcal": 86, "tipo": "carbohydrates", "perfil": "salado"},
    "fruta_pl": {"nombre": "Plátano", "p": 1, "c": 23, "f": 0.3, "kcal": 90, "tipo": "carbohydrates", "perfil": "dulce"},
    "fruta_mz": {"nombre": "Manzana", "p": 0.3, "c": 14, "f": 0.2, "kcal": 52, "tipo": "carbohydrates", "perfil": "dulce"},
    "arandanos": {"nombre": "Arándanos/Frutos Rojos", "p": 0.7, "c": 14, "f": 0.3, "kcal": 57, "tipo": "carbohydrates", "perfil": "dulce"},
    "pan": {"nombre": "Pan Integral/Tostado", "p": 9, "c": 40, "f": 3, "kcal": 250, "tipo": "carbohydrates", "perfil": "neutro"},
    "tortitas": {"nombre": "Tortitas de Arroz/Maíz", "p": 7, "c": 80, "f": 2, "kcal": 380, "tipo": "carbohydrates", "perfil": "neutro"},

    # --- GRASAS ---
    "aceite": {"nombre": "Aceite de Oliva", "p": 0, "c": 0, "f": 100, "kcal": 884, "tipo": "fat", "perfil": "salado"},
    "aguacate": {"nombre": "Aguacate", "p": 2, "c": 9, "f": 15, "kcal": 160, "tipo": "fat", "perfil": "neutro"},
    "nueces": {"nombre": "Nueces", "p": 15, "c": 14, "f": 65, "kcal": 654, "tipo": "fat", "perfil": "neutro"},
    "almendras": {"nombre": "Almendras", "p": 21, "c": 22, "f": 49, "kcal": 575, "tipo": "fat", "perfil": "neutro"},
    "crema_cacahuete": {"nombre": "Crema de Cacahuete", "p": 25, "c": 20, "f": 50, "kcal": 590, "tipo": "fat", "perfil": "dulce"},
    "choco": {"nombre": "Chocolate Negro 85%", "p": 9, "c": 19, "f": 48, "kcal": 580, "tipo": "fat", "perfil": "dulce"}
}

def buscar_alimento_perfecto(tipo_macro, gramos_objetivo, prohibidos=[], perfil_plato=None):
    """
    Busca alimento respetando:
    1. Tipo de Macro
    2. Lista de prohibidos
    3. COHERENCIA: Si perfil_plato es 'dulce', solo busca 'dulce' o 'neutro'.
    """
    candidatos = []
    
    for key, val in DB_ALIMENTOS.items():
        # 1. Filtro Tipo
        if val['tipo'] != tipo_macro: continue
        
        # 2. Filtro Prohibidos
        es_prohibido = False
        nombre_lower = val['nombre'].lower()
        lista_clean = [p.strip().lower() for p in prohibidos]
        for p in lista_clean:
            if p in nombre_lower:
                es_prohibido = True
                break
        if es_prohibido: continue

        # 3. Filtro COHERENCIA (NUEVO)
        if perfil_plato:
            # Si el alimento no coincide con el plato Y no es neutro, lo saltamos
            if val['perfil'] != perfil_plato and val['perfil'] != 'neutro':
                continue

        candidatos.append(val)
    
    # Si no hay candidatos (ej. no hay grasas dulces disponibles), 
    # intentamos buscar neutros o relajamos el filtro para no dejar el plato vacío.
    if not candidatos and perfil_plato:
        # Reintentar sin filtro de sabor por seguridad
        return buscar_alimento_perfecto(tipo_macro, gramos_objetivo, prohibidos, perfil_plato=None)

    if not candidatos: return None

    elegido = random.choice(candidatos)
    
    macro_ref = elegido['p'] if tipo_macro == 'protein' else (elegido['c'] if tipo_macro == 'carbohydrates' else elegido['f'])
    
    if macro_ref == 0: return None
    
    # Cálculo de cantidad
    cantidad_necesaria = (gramos_objetivo * 100) / macro_ref
    
    # Si la cantidad es ridícula (ej. 2g de arroz), devolvemos None para no ensuciar la dieta
    if cantidad_necesaria < 5: return None

    aporte_real = {
        "p": (elegido['p'] * cantidad_necesaria) / 100,
        "c": (elegido['c'] * cantidad_necesaria) / 100,
        "f": (elegido['f'] * cantidad_necesaria) / 100,
        "kcal": (elegido['kcal'] * cantidad_necesaria) / 100
    }
    
    return {
        "nombre": elegido['nombre'],
        "gramos_peso": int(cantidad_necesaria),
        "macros_reales": aporte_real,
        "perfil": elegido['perfil'] # Devolvemos el perfil para marcar el tono del plato
    }