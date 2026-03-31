import streamlit as st
from calculos import calcular_resultados
from analisis import analizar_negocio
from utils import guardar_analisis_csv, clase_estado_css
from styles import aplicar_estilos

st.set_page_config(page_title="VALORA", page_icon="📈", layout="centered")
aplicar_estilos()

# -------------------------
# FUNCIONES
# -------------------------
def clasificar_estado(utilidad, margen):
    if utilidad < 0:
        return "🔴 Crítico", "La operación está generando pérdidas."
    elif margen < 0.1:
        return "🟡 En riesgo", "Existe utilidad, pero el margen es bajo."
    else:
        return "🟢 Saludable", "La estructura es rentable."

def interpretar(utilidad, margen, equilibrio, cantidad):
    textos = []

    if utilidad < 0:
        textos.append("Estás perdiendo dinero en este escenario.")
    else:
        textos.append("El negocio genera utilidad.")

    if margen < 0.1:
        textos.append("El margen es bajo, la rentabilidad es frágil.")
    else:
        textos.append("El margen es saludable.")

    if equilibrio > cantidad:
        textos.append("No alcanzas el punto de equilibrio.")
    else:
        textos.append("Superas el punto de equilibrio.")

    return textos

def acciones(resultados, datos):
    acc = []

    if resultados["utilidad"] < 0:
        acc.append("Revisar precio o reducir costos.")
    if resultados["margen"] < 0.1:
        acc.append("Mejorar margen.")
    if resultados["punto_equilibrio"] > datos["cantidad"]:
        acc.append("Aumentar ventas.")

    if not acc:
        acc.append("Mantener seguimiento del desempeño.")

    return acc

# -------------------------
# SESSION STATE
# -------------------------
if "analisis_guardado" not in st.session_state:
    st.session_state.analisis_guardado = False

# -------------------------
# CABECERA PRO
# -------------------------
st.markdown('<div class="main-title">VALORA</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Herramienta de análisis económico para tomar decisiones inteligentes</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="soft-card">', unsafe_allow_html=True)

st.markdown("### ¿Qué hace VALORA?")
st.markdown("""
Evalúa si tu producto o negocio:

- genera utilidad real  
- tiene una estructura sana  
- necesita ajustes  

Obtienes:
- diagnóstico  
- interpretación  
- acciones  
""")

st.markdown("### Flujo recomendado")
st.markdown("""
1. Analiza  
2. Guarda  
3. Compara  
4. Revisa recomendaciones  
5. Consulta dashboard  
""")

st.info("¿Dudas? Usa la Guía económica.")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# FORMULARIO
# -------------------------
st.markdown("## 🔍 Análisis económico")

modo = st.radio(
    "Tipo de análisis",
    ["Producto", "Negocio"],
    horizontal=True
)

with st.form("form"):
    nombre = st.text_input("Nombre", placeholder="Ej. Producto A")

    st.markdown("### Ventas")
    precio = st.number_input("Precio", min_value=0.0)
    cantidad = st.number_input("Cantidad", min_value=0.0)

    st.markdown("### Costos")
    costos_fijos = st.number_input("Costos fijos", min_value=0.0)
    costo_variable = st.number_input("Costo variable por unidad", min_value=0.0)

    submit = st.form_submit_button("🔍 Analizar")

# -------------------------
# PROCESAMIENTO
# -------------------------
if submit:
    resultados = calcular_resultados(precio, cantidad, costo_variable, costos_fijos)
    mensajes = analizar_negocio(resultados)

    estado, descripcion = clasificar_estado(resultados["utilidad"], resultados["margen"])

    st.session_state.analisis_guardado = True
    st.session_state.resultados = resultados
    st.session_state.mensajes = mensajes
    st.session_state.estado = estado
    st.session_state.descripcion = descripcion
    st.session_state.datos = {
        "precio": precio,
        "cantidad": cantidad,
        "costos_fijos": costos_fijos,
        "costo_variable": costo_variable
    }

# -------------------------
# RESULTADOS PRO
# -------------------------
if st.session_state.analisis_guardado:
    r = st.session_state.resultados
    datos = st.session_state.datos

    st.markdown("## Resultado del análisis")
    st.caption("Resumen económico del escenario actual.")

    st.markdown(
        f'<div class="{clase_estado_css(st.session_state.estado)}">{st.session_state.estado} — {st.session_state.descripcion}</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Utilidad", round(r["utilidad"], 2))
    c2.metric("Margen", f"{round(r['margen']*100,2)}%")
    c3.metric("Equilibrio", round(r["punto_equilibrio"], 2))
    c4.metric("Ingresos", round(r["ingresos"], 2))

    st.markdown("### Interpretación")
    for t in interpretar(r["utilidad"], r["margen"], r["punto_equilibrio"], datos["cantidad"]):
        st.write("•", t)

    st.markdown("### Diagnóstico")
    for m in st.session_state.mensajes:
        st.write("•", m)

    st.markdown("### Acciones sugeridas")
    for a in acciones(r, datos):
        st.write("•", a)

    st.success("Análisis completado correctamente.")

    # -------------------------
    # SIMULACIÓN
    # -------------------------
    with st.expander("Simulación"):
        nuevo_precio = st.slider("Nuevo precio", 0.0, precio*2 if precio>0 else 10.0, precio)
        nueva_cantidad = st.slider("Nueva cantidad", 0.0, cantidad*2 if cantidad>0 else 10.0, cantidad)

        sim = calcular_resultados(nuevo_precio, nueva_cantidad, costo_variable, costos_fijos)

        s1, s2 = st.columns(2)
        s1.metric("Utilidad simulada", round(sim["utilidad"],2))
        s2.metric("Margen simulado", f"{round(sim['margen']*100,2)}%")

    # -------------------------
    # GUARDAR
    # -------------------------
    if st.button("💾 Guardar análisis"):
        guardar_analisis_csv(datos, r, modo, nombre)
        st.success("Guardado correctamente.")
