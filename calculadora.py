import datetime

def determinar_nombre_comidas(n_comidas, hora_entreno_str=None, hora_despertar_str=None):
    """
    Define los nombres de las comidas basándose en la hora de entrenamiento.
    """
    nombres_base = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena", "Recena"]
    
    # Si no hay horario, devolvemos básicos
    if not hora_entreno_str:
        return {f"comida_{i+1}": nombres_base[i] if i < len(nombres_base) else f"Comida {i+1}" for i in range(n_comidas)}

    # Intentamos parsear las horas
    try:
        # Formato esperado "HH:MM"
        h_entreno = int(hora_entreno_str.split(":")[0])
        h_despertar = int(hora_despertar_str.split(":")[0]) if hora_despertar_str else 8
    except:
        h_entreno = 18
        h_despertar = 8

    comidas = {}
    # Estimamos que comes cada 3.5 horas desde que despiertas
    horas_comidas = [h_despertar + (i * 3.5) for i in range(n_comidas)]
    
    idx_pre = -1
    
    # Buscamos la comida justo antes del entreno
    for i, h_comida in enumerate(horas_comidas):
        if h_comida < h_entreno:
            idx_pre = i
        else:
            break
            
    # Asignamos nombres con etiquetas
    for i in range(n_comidas):
        clave = f"comida_{i+1}"
        base = nombres_base[i] if i < len(nombres_base) else f"Comida {i+1}"
        
        if i == idx_pre:
            base += " (PRE-ENTRENO ⚡)"
        elif i == idx_pre + 1:
            base += " (POST-ENTRENO 💪)"
            
        comidas[clave] = base
        
    return comidas

def calcular_macros(perfil):
    # 1. TMB (Mifflin-St Jeor)
    if perfil['gender'] == 'male':
        tmb = (10 * perfil['weight']) + (6.25 * perfil['height']) - (5 * perfil['age']) + 5
    else:
        tmb = (10 * perfil['weight']) + (6.25 * perfil['height']) - (5 * perfil['age']) - 161

    # 2. Gasto Calórico Total
    gcd = tmb * perfil['activity']

    # 3. Ajuste según Objetivo
    objetivo_kcal = gcd
    if perfil['goal'] == '1': # Perder
        deficit = 250 if perfil['intensity'] == '1' else (350 if perfil['intensity'] == '2' else 500)
        objetivo_kcal -= deficit
    elif perfil['goal'] == '2': # Ganar
        superavit = 200 if perfil['intensity'] == '1' else (300 if perfil['intensity'] == '2' else 500)
        objetivo_kcal += superavit

    # 4. Reparto de Macros
    proteina_g = perfil['weight'] * 2.0
    grasas_g = perfil['weight'] * 0.9
    
    kcal_prot = proteina_g * 4
    kcal_fat = grasas_g * 9
    
    kcal_restantes = objetivo_kcal - (kcal_prot + kcal_fat)
    carbos_g = kcal_restantes / 4
    
    if carbos_g < 50: 
        carbos_g = 50
        objetivo_kcal = kcal_prot + kcal_fat + (carbos_g * 4)

    # 5. Distribución (Timing)
    n_comidas = perfil['num_comidas']
    # Pasamos las horas al generador de nombres
    nombres = determinar_nombre_comidas(n_comidas, perfil.get('hora_entreno'), perfil.get('hora_despertar'))
    
    plan_comidas = {}
    
    p_meal = proteina_g / n_comidas
    c_meal = carbos_g / n_comidas
    f_meal = grasas_g / n_comidas

    for key, nombre_real in nombres.items():
        mod_c = 1.0
        mod_f = 1.0
        
        if "POST-ENTRENO" in nombre_real:
            mod_c = 1.4 
            mod_f = 0.6 
        elif "PRE-ENTRENO" in nombre_real:
            mod_c = 1.2
            mod_f = 0.8
        
        plan_comidas[nombre_real] = {
            "prot": int(p_meal),
            "carb": int(c_meal * mod_c),
            "fat": int(f_meal * mod_f)
        }

    return {
        "tmb": int(tmb),
        "gcd": int(gcd),
        "total": int(objetivo_kcal), # AQUÍ ESTABA EL FALLO ANTERIOR
        "macros_totales": {"p": int(proteina_g), "c": int(carbos_g), "f": int(grasas_g)},
        "comidas": plan_comidas
    }