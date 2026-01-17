from sqlalchemy.orm import Session
from models import engine, BedcaFood, init_db

# --- BASE DE DATOS AMPLIADA (BEDCA) ---
# Valores por 100g: Calorías, Proteínas, Carbohidratos, Grasas, Fibra

BEDCA_DATA = [
    # CARNES Y AVES
    {"name": "Pechuga de pollo (sin piel)", "cal": 113, "prot": 20.6, "carb": 0.0, "fat": 3.4, "fiber": 0.0},
    {"name": "Muslo de pollo (con piel)", "cal": 183, "prot": 18.0, "carb": 0.0, "fat": 12.0, "fiber": 0.0},
    {"name": "Ternera magra (filete)", "cal": 130, "prot": 21.0, "carb": 0.0, "fat": 5.0, "fiber": 0.0},
    {"name": "Ternera grasa (chuleta)", "cal": 240, "prot": 17.0, "carb": 0.0, "fat": 19.0, "fiber": 0.0},
    {"name": "Lomo de cerdo", "cal": 150, "prot": 20.0, "carb": 0.0, "fat": 7.0, "fiber": 0.0},
    {"name": "Pavo (pechuga)", "cal": 105, "prot": 24.0, "carb": 0.0, "fat": 1.0, "fiber": 0.0},
    {"name": "Jamón Serrano (sin grasa)", "cal": 190, "prot": 30.0, "carb": 0.0, "fat": 8.0, "fiber": 0.0},
    {"name": "Conejo", "cal": 133, "prot": 21.0, "carb": 0.0, "fat": 5.0, "fiber": 0.0},
    
    # PESCADOS Y MARISCOS
    {"name": "Atún en agua (lata)", "cal": 99, "prot": 23.0, "carb": 0.0, "fat": 0.8, "fiber": 0.0},
    {"name": "Atún en aceite (escurrido)", "cal": 190, "prot": 24.0, "carb": 0.0, "fat": 10.0, "fiber": 0.0},
    {"name": "Salmón crudo", "cal": 182, "prot": 18.4, "carb": 0.0, "fat": 12.0, "fiber": 0.0},
    {"name": "Merluza", "cal": 64, "prot": 11.8, "carb": 0.0, "fat": 1.8, "fiber": 0.0},
    {"name": "Bacalao fresco", "cal": 74, "prot": 17.0, "carb": 0.0, "fat": 0.6, "fiber": 0.0},
    {"name": "Gambas / Langostinos", "cal": 95, "prot": 20.0, "carb": 1.0, "fat": 1.0, "fiber": 0.0},
    {"name": "Sepia / Calamar", "cal": 80, "prot": 16.0, "carb": 1.0, "fat": 1.4, "fiber": 0.0},
    {"name": "Sardinas (lata)", "cal": 208, "prot": 24.0, "carb": 0.0, "fat": 12.0, "fiber": 0.0},

    # HUEVOS Y LÁCTEOS
    {"name": "Huevo de gallina entero", "cal": 150, "prot": 12.5, "carb": 0.0, "fat": 11.1, "fiber": 0.0},
    {"name": "Clara de huevo", "cal": 52, "prot": 11.0, "carb": 0.7, "fat": 0.2, "fiber": 0.0},
    {"name": "Leche entera", "cal": 63, "prot": 3.1, "carb": 4.6, "fat": 3.5, "fiber": 0.0},
    {"name": "Leche semidesnatada", "cal": 45, "prot": 3.3, "carb": 4.8, "fat": 1.6, "fiber": 0.0},
    {"name": "Leche desnatada", "cal": 34, "prot": 3.4, "carb": 4.9, "fat": 0.1, "fiber": 0.0},
    {"name": "Yogur natural", "cal": 61, "prot": 3.7, "carb": 4.3, "fat": 3.2, "fiber": 0.0},
    {"name": "Queso fresco batido 0%", "cal": 46, "prot": 8.0, "carb": 3.5, "fat": 0.1, "fiber": 0.0},
    {"name": "Queso Mozzarella", "cal": 280, "prot": 28.0, "carb": 3.1, "fat": 17.0, "fiber": 0.0},
    {"name": "Queso Curado", "cal": 420, "prot": 25.0, "carb": 1.0, "fat": 35.0, "fiber": 0.0},
    {"name": "Requesón", "cal": 109, "prot": 13.0, "carb": 3.0, "fat": 4.0, "fiber": 0.0},

    # CEREALES Y TUBÉRCULOS
    {"name": "Arroz blanco crudo", "cal": 381, "prot": 7.0, "carb": 86.0, "fat": 0.9, "fiber": 0.2},
    {"name": "Arroz integral crudo", "cal": 350, "prot": 8.0, "carb": 74.0, "fat": 2.2, "fiber": 2.2},
    {"name": "Avena en copos", "cal": 375, "prot": 13.5, "carb": 58.7, "fat": 7.0, "fiber": 10.0},
    {"name": "Pasta de trigo", "cal": 359, "prot": 12.8, "carb": 70.9, "fat": 1.5, "fiber": 5.0},
    {"name": "Pan blanco", "cal": 260, "prot": 8.0, "carb": 50.0, "fat": 2.0, "fiber": 2.0},
    {"name": "Pan integral", "cal": 258, "prot": 9.0, "carb": 44.0, "fat": 3.0, "fiber": 7.0},
    {"name": "Patata cruda", "cal": 73, "prot": 2.3, "carb": 14.8, "fat": 0.1, "fiber": 2.1},
    {"name": "Boniato / Batata", "cal": 86, "prot": 1.6, "carb": 20.1, "fat": 0.1, "fiber": 3.0},
    {"name": "Quinoa cruda", "cal": 368, "prot": 14.0, "carb": 64.0, "fat": 6.0, "fiber": 7.0},

    # LEGUMBRES
    {"name": "Lentejas secas", "cal": 310, "prot": 24.0, "carb": 48.0, "fat": 1.2, "fiber": 11.0},
    {"name": "Garbanzos secos", "cal": 330, "prot": 19.0, "carb": 45.0, "fat": 6.0, "fiber": 15.0},
    {"name": "Alubias blancas secas", "cal": 300, "prot": 21.0, "carb": 40.0, "fat": 1.5, "fiber": 20.0},
    {"name": "Soja texturizada", "cal": 330, "prot": 50.0, "carb": 20.0, "fat": 1.0, "fiber": 15.0},

    # FRUTAS
    {"name": "Plátano", "cal": 94, "prot": 1.2, "carb": 20.0, "fat": 0.3, "fiber": 3.4},
    {"name": "Manzana (con piel)", "cal": 52, "prot": 0.3, "carb": 14.0, "fat": 0.2, "fiber": 2.4},
    {"name": "Naranja", "cal": 47, "prot": 0.9, "carb": 12.0, "fat": 0.1, "fiber": 2.4},
    {"name": "Fresas", "cal": 33, "prot": 0.7, "carb": 7.0, "fat": 0.3, "fiber": 2.0},
    {"name": "Kiwi", "cal": 61, "prot": 1.1, "carb": 15.0, "fat": 0.5, "fiber": 3.0},
    {"name": "Arándanos", "cal": 57, "prot": 0.7, "carb": 14.0, "fat": 0.3, "fiber": 2.4},
    {"name": "Pera", "cal": 57, "prot": 0.4, "carb": 15.0, "fat": 0.1, "fiber": 3.1},
    {"name": "Sandía", "cal": 30, "prot": 0.6, "carb": 7.6, "fat": 0.2, "fiber": 0.4},
    {"name": "Melón", "cal": 34, "prot": 0.9, "carb": 8.0, "fat": 0.2, "fiber": 0.9},
    {"name": "Aguacate", "cal": 160, "prot": 2.0, "carb": 8.5, "fat": 15.0, "fiber": 6.7},

    # VERDURAS
    {"name": "Brócoli", "cal": 34, "prot": 2.8, "carb": 7.0, "fat": 0.4, "fiber": 2.6},
    {"name": "Espinacas", "cal": 23, "prot": 2.9, "carb": 3.6, "fat": 0.4, "fiber": 2.2},
    {"name": "Lechuga", "cal": 15, "prot": 1.4, "carb": 2.9, "fat": 0.2, "fiber": 1.3},
    {"name": "Tomate", "cal": 18, "prot": 0.9, "carb": 3.9, "fat": 0.2, "fiber": 1.2},
    {"name": "Zanahoria", "cal": 41, "prot": 0.9, "carb": 9.6, "fat": 0.2, "fiber": 2.8},
    {"name": "Calabacín", "cal": 17, "prot": 1.2, "carb": 3.1, "fat": 0.3, "fiber": 1.0},
    {"name": "Pimiento Rojo", "cal": 31, "prot": 1.0, "carb": 6.0, "fat": 0.3, "fiber": 2.1},
    {"name": "Champiñones", "cal": 22, "prot": 3.1, "carb": 3.3, "fat": 0.3, "fiber": 1.0},
    {"name": "Judías verdes", "cal": 31, "prot": 1.8, "carb": 7.0, "fat": 0.2, "fiber": 3.4},
    {"name": "Pepino", "cal": 16, "prot": 0.7, "carb": 3.6, "fat": 0.1, "fiber": 0.5},

    # GRASAS Y FRUTOS SECOS
    {"name": "Aceite de oliva virgen", "cal": 899, "prot": 0.0, "carb": 0.0, "fat": 99.9, "fiber": 0.0},
    {"name": "Almendras", "cal": 604, "prot": 20.0, "carb": 5.7, "fat": 53.5, "fiber": 11.4},
    {"name": "Nueces", "cal": 654, "prot": 15.0, "carb": 13.7, "fat": 65.0, "fiber": 6.7},
    {"name": "Cacahuetes (Maní)", "cal": 567, "prot": 26.0, "carb": 16.0, "fat": 49.0, "fiber": 8.5},
    {"name": "Mantequilla", "cal": 717, "prot": 0.9, "carb": 0.1, "fat": 81.0, "fiber": 0.0},
    
    # EXTRAS
    {"name": "Miel", "cal": 304, "prot": 0.3, "carb": 82.0, "fat": 0.0, "fiber": 0.2},
    {"name": "Azúcar blanco", "cal": 387, "prot": 0.0, "carb": 100.0, "fat": 0.0, "fiber": 0.0},
    {"name": "Chocolate negro 85%", "cal": 570, "prot": 9.0, "carb": 20.0, "fat": 48.0, "fiber": 12.0},
]

def cargar_datos():
    with Session(engine) as session:
        # Nota: Borramos lo anterior para no tener duplicados al recargar
        # Esto es O(N) pero seguro para desarrollo
        existing = session.query(BedcaFood).count()
        if existing > 0:
            print(f"🧹 Limpiando base de datos antigua ({existing} alimentos)...")
            session.query(BedcaFood).delete()
            session.commit()

        print(f"⏳ Insertando {len(BEDCA_DATA)} alimentos de la Base de Datos Ampliada...")
        
        for item in BEDCA_DATA:
            # Creamos un ID único simple basado en el nombre
            simple_id = item["name"].lower().replace(" ", "-").replace("(", "").replace(")", "")[:20]
            
            food = BedcaFood(
                bedca_id=simple_id,
                name=item["name"],
                calories=item["cal"],
                protein=item["prot"],
                carbohydrates=item["carb"],
                fat=item["fat"],
                fiber=item["fiber"]
            )
            session.add(food)
        
        session.commit()
        print("✅ ¡Éxito! Base de datos actualizada con el catálogo completo.")

if __name__ == "__main__":
    init_db()
    cargar_datos()