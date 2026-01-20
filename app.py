import streamlit as st
import random
import urllib.parse
from collections import defaultdict

# --- CONFIGURACIÓN ---
try: st.set_page_config(page_title="MacroLab", page_icon="🔬")
except: pass

ID_AFILIADO = "criptex02-21"

# --- DATOS ---
DB = [
    {"n": "Pollo", "t": "p", "m": {"p": 23, "c": 0, "f": 1}},
    {"n": "Ternera", "t": "p", "m": {"p": 20, "c": 0, "f": 5}},
    {"n": "Merluza", "t": "p", "m": {"p": 17, "c": 0, "f": 2}},
    {"n": "Huevos", "t": "p", "m": {"p": 13, "c": 1, "f": 11}},
    {"n": "Claras", "t": "p", "m": {"p": 11, "c": 0, "f": 0}},
    {"n": "Atún", "t": "p", "m": {"p": 24, "c": 0, "f": 1}},
    {"n": "Whey", "t": "p", "m": {"p": 80, "c": 5, "f": 2}},
    {"n": "Yogur", "t": "p", "m": {"p": 10, "c": 4, "f": 0}},
    {"n": "Arroz", "t": "c", "m": {"p": 2, "c": 28, "f": 0}},
    {"n": "Pasta", "t": "c", "m": {"p": 5, "c": 25, "f": 1}},
    {"n": "Patata", "t": "c", "m": {"p": 2, "c": 17, "f": 0}},
    {"n": "Avena", "t": "c", "m": {"p": 4, "c": 12, "f": 1}},
    {"n": "Pan", "t": "c", "m": {"p": 4, "c": 15, "f": 1}},
    {"n": "Fruta", "t": "c", "m": {"p": 0, "c": 12, "f": 0}},
    {"n": "Aceite", "t": "f", "m": {"p": 0, "c": 0, "f": 100}},
    {"n": "Aguacate", "t": "f", "m": {"p": 2, "c": 9, "f": 15}},
    {"n": "Nueces", "t": "f", "m": {"p": 5, "c": 5, "f": 25}}
]

# --- LÓGICA ---
def get_food(tipo, gr, ban=[]):
    opts = [x for x in DB if x['t'] == tipo[0] and x['n'] not in ban]
    if not opts: return None
    sel = random.choice(opts)
    if sel['m'][tipo[0]] == 0: return None
    peso = (gr * 100) / sel['m'][tipo[0]]
    return {"n": sel['n'], "g": int(peso)}

def make_menu(macros, ban=[]):
    menu = {}
    for k, v in macros['comidas'].items():
        plato = []
        for t, val in [('p', v['p']), ('c', v['c']), ('f', v['f'])]:
            if val > 0:
                f = get_food(t, val, ban)
                if f: plato.append(f)
        menu[k] = plato
    return menu

def calc(p):
    # Harris-Benedict simplificado
    tmb = (10*p['w']) + (6.25*p['h']) - (5*p['a']) + (5 if p['s']=='H' else -161)
    tdee = tmb * p['act']
    cal = tdee + (-400 if p['obj']=='Perder' else (350 if p['obj']=='Ganar' else 0))
    prot = 2.2 * p['w']
    fat = 0.9 * p['w']
    carb = (cal - (prot*4) - (fat*9)) / 4
    
    dist = {}
    for i in range(p['n_com']):
        dist[f"Comida {i+1}"] = {'p': int(prot/p['n_com']), 'c': int(carb/p['n_com']), 'f': int(fat/p['n_com'])}
    return {'cal': int(cal), 'p': int(prot), 'c': int(carb), 'f': int(fat), 'comidas': dist}

def calc_off(m):
    res = copy.deepcopy(m)
    res['cal'] = int(res['cal'] * 0.85)
    res['c'] = int(res['c'] * 0.6)
    for k in res['comidas']:
        res['comidas'][k]['c'] = int(res['comidas'][k]['c'] * 0.6)
    return res

# --- APP ---
if 'ok' not in st.session_state: st.session_state.ok = False

with st.sidebar:
    st.header("👤 Datos")
    w = st.number_input("Peso", 40, 150, 75)
    h = st.number_input("Altura", 120, 220, 175)
    a = st.number_input("Edad", 15, 80, 25)
    s = st.selectbox("Sexo", ["H", "M"])
    act = st.selectbox("Actividad", [1.2, 1.375, 1.55, 1.725])
    obj = st.selectbox("Objetivo", ["Perder", "Ganar", "Mantener"])
    st.divider()
    mode = st.radio("Modo", ["Lineal", "Ciclado"])
    n_com = st.number_input("Comidas", 2, 6, 4)
    if st.button("🚀 CALCULAR"):
        st.session_state.ok = True
        base = calc({'w':w, 'h':h, 'a':a, 's':s, 'act':act, 'obj':obj, 'n_com':n_com})
        st.session_state.m_on = base
        st.session_state.m_off = base if mode == "Lineal" else calc_off(base)
        st.session_state.d_on = make_menu(st.session_state.m_on)
        st.session_state.d_off = make_menu(st.session_state.m_off)

    with st.expander("🏪 TIENDA"):
        # Enlaces seguros
        url = "https://www.amazon.es/s?k="
        tag = f"&tag={ID_AFILIADO}"
        st.link_button("🥛 Proteína", url + "proteina+whey" + tag)
        st.link_button("⚡ Creatina", url + "creatina" + tag)
        st.link_button("🐟 Omega 3", url + "omega+3" + tag)
        st.link_button("💊 Multivitamin", url + "multivitaminas" + tag)

if st.session_state.ok:
    st.title("🔬 Panel de Control")
    t1, t2, t3, t4, t5 = st.tabs(["RUTINA", "DÍA ON", "DÍA OFF", "LISTA", "SHARE"])
    
    with t1:
        st.info("Rutina Generada (Ejemplo):")
        st.write("- Sentadilla: 4x10\n- Press Banca: 4x10\n- Remo: 4x12\n- Militar: 3x12")
        
    with t2:
        m = st.session_state.m_on
        st.metric("🔥 CALORÍAS", m['cal'])
        st.write(f"P: {m['p']}g | C: {m['c']}g | F: {m['f']}g")
        for k, v in st.session_state.d_on.items():
            with st.expander(k):
                for x in v: st.write(f"- {x['n']}: {x['g']}g")
                
    with t3:
        m = st.session_state.m_off
        st.metric("💤 CALORÍAS", m['cal'])
        st.write(f"P: {m['p']}g | C: {m['c']}g | F: {m['f']}g")
        for k, v in st.session_state.d_off.items():
            with st.expander(k):
                for x in v: st.write(f"- {x['n']}: {x['g']}g")

    with t4:
        st.header("🛒 Compra")
        lista = defaultdict(int)
        for d in [st.session_state.d_on, st.session_state.d_off]:
            for k, v in d.items():
                for x in v: lista[x['n']] += x['g']
        for k, v in lista.items(): st.checkbox(f"{k}: {v}g")

    with t5:
        txt = "MI PLAN MACROLAB\n"
        txt += f"ON: {st.session_state.m_on['cal']} kcal\n"
        txt += f"OFF: {st.session_state.m_off['cal']} kcal"
        
        # Lógica de enlaces segura (dividida para no dar error)
        safe = urllib.parse.quote(txt)
        w_url = "https://api.whatsapp.com/send?text=" + safe
        m_url = "mailto:?subject=Plan&body=" + safe
        
        c1, c2 = st.columns(2)
        c1.link_button("WhatsApp", w_url)
        c2.link_button("Email", m_url)
        st.text_area("Texto", txt)
else:
    st.info("👈 Pulsa Calcular")