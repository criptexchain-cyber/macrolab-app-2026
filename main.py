from calculadora import calcular_macros
from generador import buscar_alimento_perfecto
from entrenador import generar_rutina
import datetime

def calcular_horas_sueno(hora_dormir, hora_despertar):
    # Formato esperado: "23:00" o "07:30"
    try:
        t1 = datetime.datetime.strptime(hora_dormir, "%H:%M")
        t2 = datetime.datetime.strptime(hora_despertar, "%H:%M")
        
        # Si la hora de despertar es menor que la de dormir, asumimos día siguiente
        if t2 < t1:
            t2 += datetime.timedelta(days=1)
            
        diff = t2 - t1
        horas = diff.total_seconds() / 3600
        return round(horas, 1)
    except:
        return 0

def solicitar_entero(mensaje, min_val=None, max_val=None):
    """Función auxiliar para pedir números sin que el programa se rompa"""
    while True:
        try:
            dato = int(input(mensaje))
            if min_val is not None and dato < min_val:
                print(f"⚠️ Por favor, introduce un número mayor o igual a {min_val}.")
                continue
            if max_val is not None and dato > max_val:
                print(f"⚠️ Por favor, introduce un número menor o igual a {max_val}.")
                continue
            return dato
        except ValueError:
            print("⚠️ Error: Debes introducir un número entero (ej: 4).")

def solicitar_flotante(mensaje):
    """Función auxiliar para pedir peso/altura con decimales"""
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("⚠️ Error: Introduce un número válido (ej: 80.5).")

def iniciar_app():
    print("\n--- 💪 SISTEMA INTEGRAL FITNESS PRO (V3.4 - FLUJO CORREGIDO) ---")
    
    # 1. DATOS FISIOLÓGICOS
    print("\n--- DATOS PERSONALES ---")
    peso = solicitar_flotante("1. Peso (kg): ")
    altura = solicitar_flotante("2. Altura (cm): ")
    edad = solicitar_entero("3. Edad: ", 10, 100)
    
    while True:
        genero = input("4. Género (male/female): ").lower().strip()
        if genero in ['male', 'female']: break
        print("⚠️ Escribe 'male' o 'female'.")
    
    # 2. BIOFEEDBACK (SUEÑO)
    print("\n--- BIOFEEDBACK Y RECUPERACIÓN ---")
    print("Formato de hora 24h (ej: 23:00, 07:30)")
    hora_bed = input("¿A qué hora sueles irte a dormir?: ")
    hora_wake = input("¿A qué hora te despiertas?: ")
    horas_sueno = calcular_horas_sueno(hora_bed, hora_wake)
    
    # 3. NIVEL DE ACTIVIDAD
    print("\n--- NIVEL DE ACTIVIDAD (Factor TMB) ---")
    print("1. Poco o ningún ejercicio (x 1.2)")
    print("2. Ejercicio ligero (1-3 días a la semana) (x 1.375)")
    print("3. Ejercicio moderado (3-5 días a la semana) (x 1.55)")
    print("4. Ejercicio fuerte (6-7 días a la semana) (x 1.725)")
    print("5. Ejercicio muy fuerte (dos veces al día, muy duro) (x 1.9)")
    op_act = solicitar_entero("👉 Elige (1-5): ", 1, 5)
    
    actividad = 1.2 
    if op_act == 2: actividad = 1.375
    elif op_act == 3: actividad = 1.55
    elif op_act == 4: actividad = 1.725
    elif op_act == 5: actividad = 1.9

    # 4. OBJETIVOS
    print("\n--- OBJETIVOS ---")
    print("1. Perder grasa")
    print("2. Ganar músculo")
    print("3. Mantener")
    objetivo = str(solicitar_entero("👉 Elige (1-3): ", 1, 3))
    
    intensidad = "0"
    if objetivo == '1':
        print("\nVelocidad de pérdida:")
        print("1. Lenta (-250 kcal)")
        print("2. Moderada (-350 kcal)")
        print("3. Rápida (-500 kcal)")
        intensidad = str(solicitar_entero("👉 Elige: ", 1, 3))
    elif objetivo == '2':
        print("\nVelocidad de ganancia:")
        print("1. Lenta (+200 kcal)")
        print("2. Moderada (+300 kcal)")
        print("3. Rápida (+500 kcal)")
        intensidad = str(solicitar_entero("👉 Elige: ", 1, 3))

    # 5. ENTRENAMIENTO Y PREFERENCIAS
    print("\n--- CONFIGURACIÓN ENTRENADOR ---")
    print("Experiencia: 1.Principiante | 2.Intermedio | 3.Avanzado")
    nivel_entreno = str(solicitar_entero("👉 Elige (1-3): ", 1, 3))
    
    dias_entreno = solicitar_entero("¿Días disponibles para entrenar? (3-6): ", 3, 6)
    n_comidas = solicitar_entero("¿Cuántas comidas harás al día?: ", 1, 8)

    # --- AQUÍ ESTÁ EL CAMBIO: AL FINAL DEL TODO ---
    print("\n--- PREFERENCIAS ALIMENTARIAS ---")
    print("Escribe los alimentos que NO quieres comer (o alergias) separados por comas.")
    print("Ejemplo: leche, nueces, pescado")
    print("(Si comes de todo, pulsa ENTER vacío)")
    prohibidos_input = input("👉 Alimentos a evitar: ")
    
    # Procesamos la lista
    lista_prohibidos = []
    if prohibidos_input.strip():
        lista_prohibidos = [x.strip().lower() for x in prohibidos_input.split(",")]
    
    # EMPAQUETADO DE PERFIL
    perfil = {
        "weight": peso, "height": altura, "age": edad,
        "gender": genero, "goal": objetivo, 
        "intensity": intensidad, "activity": actividad,
        "num_comidas": n_comidas,
        "nivel_entreno": nivel_entreno,
        "dias_entreno": dias_entreno,
        "horas_sueno": horas_sueno
    }

    # CÁLCULOS INICIALES
    res_dieta = calcular_macros(perfil)
    rutina_texto = generar_rutina(perfil)

    # BUCLE PRINCIPAL DE RESULTADOS
    while True:
        informe = ""
        informe += "\n" + "="*60 + "\n"
        informe += f"PLAN INTEGRAL - {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
        informe += f"Factor Actividad: {actividad} | Sueño promedio: {horas_sueno}h\n"
        if lista_prohibidos:
            informe += f"🚫 Evitando: {', '.join(lista_prohibidos)}\n"
        informe += "="*60 + "\n"
        
        # --- SECCIÓN NUTRICIÓN ---
        informe += f"\nDIETA OBJETIVO ({int(res_dieta['total'])} kcal)\n"
        informe += f"MACROS: P:{res_dieta['macros_totales']['p']}g | C:{res_dieta['macros_totales']['c']}g | F:{res_dieta['macros_totales']['f']}g\n"
        informe += "-"*60 + "\n"
        
        for nombre, m in res_dieta['comidas'].items():
            informe += f"\n🍽️  {nombre.upper()}\n"
            
            llevamos_kcal = 0
            llevamos_p = 0; llevamos_c = 0; llevamos_f = 0
            
            # 1. Proteína
            sug_prot = buscar_alimento_perfecto('protein', m['prot'], lista_prohibidos)
            if sug_prot:
                informe += f" - {sug_prot['gramos_peso']}g de {sug_prot['nombre']}\n"
                llevamos_kcal += sug_prot['macros_reales']['kcal']
                llevamos_c += sug_prot['macros_reales']['c']
                llevamos_f += sug_prot['macros_reales']['f']
            
            # 2. Carbos
            restante_c = m['carb'] - llevamos_c
            if restante_c > 5:
                sug_carb = buscar_alimento_perfecto('carbohydrates', restante_c, lista_prohibidos)
                if sug_carb:
                    informe += f" - {sug_carb['gramos_peso']}g de {sug_carb['nombre']}\n"
                    llevamos_kcal += sug_carb['macros_reales']['kcal']
                    llevamos_f += sug_carb['macros_reales']['f']
            
            # 3. Grasas
            restante_f = m['fat'] - llevamos_f
            if restante_f > 3:
                sug_fat = buscar_alimento_perfecto('fat', restante_f, lista_prohibidos)
                if sug_fat:
                    informe += f" - {sug_fat['gramos_peso']}g de {sug_fat['nombre']}\n"
                    llevamos_kcal += sug_fat['macros_reales']['kcal']
            
            informe += f"   ✅ TOTAL PLATO: {int(llevamos_kcal)} kcal\n"

        # --- SECCIÓN ENTRENAMIENTO ---
        informe += "\n" + "="*60 + "\n"
        informe += "RUTINA DE ENTRENAMIENTO (Optimizada)\n"
        informe += "="*60 + "\n"
        informe += rutina_texto

        print(informe)

        # --- MENÚ ---
        print("\nOPCIONES:")
        print("[ENTER] -> 🔄 Regenerar Comidas")
        print("[R]     -> 🔄 Regenerar Rutina (Cambiar ejercicios)")
        print("[G]     -> 💾 Guardar Plan (.txt)")
        print("[S]     -> 👋 Salir")
        
        opcion = input("👉 Acción: ").lower().strip()
        
        if opcion == 'g':
            with open("plan_completo.txt", "w", encoding="utf-8") as f:
                f.write(informe)
            print("\n✅ Guardado en 'plan_completo.txt'")
            input("Pulsa Enter...")
        elif opcion == 'r':
            rutina_texto = generar_rutina(perfil)
        elif opcion == 's':
            break

if __name__ == "__main__":
    iniciar_app()