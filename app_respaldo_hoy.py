import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

from calculos import calcular_resultados
from analisis import analizar_negocio

st.set_page_config(page_title="VALORA", page_icon="📈", layout="centered")


# -------------------------
# ESTILOS VISUALES
# -------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1050px;
}

.main-title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 1.05rem;
    margin-bottom: 1.6rem;
}

.soft-card {
    background-color: #f8fafc;
    padding: 1.2rem;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 1rem;
}

.result-card {
    background-color: #ffffff;
    padding: 1.1rem;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

.state-good {
    background-color: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #065f46;
    padding: 0.9rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    font-weight: 600;
}

.state-risk {
    background-color: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
    padding: 0.9rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    font-weight: 600;
}

.state-bad {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
    padding: 0.9rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    font-weight: 600;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 0.4rem;
    margin-bottom: 0.8rem;
}

.small-muted {
    color: #6b7280;
    font-size: 0.95rem;
}

.metric-card {
    background-color: #ffffff;
    padding: 0.9rem;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 5px rgba(0,0,0,0.04);
    margin-bottom: 0.6rem;
}

hr {
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# FUNCIONES AUXILIARES
# -------------------------
def clasificar_estado(utilidad, margen):
    if utilidad < 0:
        return "🔴 Crítico", "La operación actual está generando pérdidas."
    elif margen < 0.1:
        return "🟡 En riesgo", "La operación genera utilidad, pero con un margen muy bajo."
    else:
        return "🟢 Saludable", "La estructura actual muestra rentabilidad razonable."


def recomendacion_producto(utilidad, margen, punto_equilibrio, cantidad):
    if utilidad < 0:
        return "Este producto no está siendo rentable. Revisa su precio, su costo variable o la cantidad vendida."
    elif punto_equilibrio > cantidad:
        return "Este producto todavía no alcanza su punto de equilibrio. Necesitas vender más unidades o mejorar su margen."
    elif margen < 0.1:
        return "Este producto deja poca ganancia por venta. Evalúa subir precio o reducir costos variables."
    else:
        return "Este producto tiene una estructura sana. Puede ser una buena línea para impulsar."


def recomendacion_negocio(utilidad, margen, punto_equilibrio, cantidad):
    if utilidad < 0:
        return "Tu negocio completo no está siendo sostenible. Debes actuar sobre costos, ventas o precios."
    elif punto_equilibrio > cantidad:
        return "Tu operación general todavía no cubre bien su estructura de costos. Necesitas aumentar ventas o mejorar rentabilidad."
    elif margen < 0.1:
        return "Tu empresa genera utilidad, pero con muy poca holgura. Un cambio pequeño en costos podría afectarte."
    else:
        return "Tu negocio tiene una base saludable. El siguiente paso es optimizar y crecer."


def guardar_analisis_csv(datos, resultados, modo, nombre_producto):
    archivo = "historial.csv"

    fila = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_analisis": modo,
        "producto": nombre_producto if nombre_producto else "N/A",
        "ingresos": resultados["ingresos"],
        "costos_fijos": datos["costos_fijos"],
        "costos_variables_totales": resultados["costos_variables_totales"],
        "costos_totales": resultados["costos_totales"],
        "utilidad": resultados["utilidad"],
        "margen": resultados["margen"],
        "punto_equilibrio": resultados["punto_equilibrio"]
    }

    df_nuevo = pd.DataFrame([fila])

    if os.path.exists(archivo):
        df_nuevo.to_csv(archivo, mode="a", header=False, index=False)
    else:
        df_nuevo.to_csv(archivo, index=False)


def guardar_historial_df(df):
    archivo = "historial.csv"
    if df.empty:
        if os.path.exists(archivo):
            os.remove(archivo)
    else:
        df.to_csv(archivo, index=False)


def clase_estado_css(estado_texto):
    if "Saludable" in estado_texto:
        return "state-good"
    elif "riesgo" in estado_texto.lower():
        return "state-risk"
    return "state-bad"


def resumen_productos(historial_df: pd.DataFrame) -> pd.DataFrame:
    df = historial_df.copy()
    df = df[df["producto"].astype(str) != "N/A"].copy()
    if df.empty:
        return pd.DataFrame()

    resumen = (
        df.groupby("producto", as_index=False)
        .agg(
            analisis=("producto", "count"),
            utilidad_promedio=("utilidad", "mean"),
            mejor_utilidad=("utilidad", "max"),
            peor_utilidad=("utilidad", "min"),
            margen_promedio=("margen_pct", "mean"),
            ingresos_promedio=("ingresos", "mean"),
        )
    )
    return resumen.sort_values("utilidad_promedio", ascending=False)


# -------------------------
# SESSION STATE
# -------------------------
if "analisis_guardado" not in st.session_state:
    st.session_state.analisis_guardado = False

if "modo_analisis" not in st.session_state:
    st.session_state.modo_analisis = "Producto individual"

if "nombre_producto" not in st.session_state:
    st.session_state.nombre_producto = ""

if "datos_base" not in st.session_state:
    st.session_state.datos_base = {}

if "resultados_base" not in st.session_state:
    st.session_state.resultados_base = {}

if "mensajes_base" not in st.session_state:
    st.session_state.mensajes_base = []

if "descripcion_estado" not in st.session_state:
    st.session_state.descripcion_estado = ""

if "estado_texto" not in st.session_state:
    st.session_state.estado_texto = ""

if "recomendacion_base" not in st.session_state:
    st.session_state.recomendacion_base = ""


# -------------------------
# UI PRINCIPAL
# -------------------------
st.markdown('<div class="main-title">VALORA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Asesor económico para decisiones de negocio</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="soft-card">', unsafe_allow_html=True)
st.markdown("### ¿Cómo funciona este análisis?")
st.markdown(
    """
VALORA analiza la rentabilidad separando la estructura del negocio en ventas, costos y resultado.

Con los datos que ingresas, el sistema calcula:

- ingresos
- costos totales
- utilidad
- margen de ganancia
- punto de equilibrio

Y luego te devuelve una interpretación económica automática para ayudarte a tomar decisiones.
"""
)
st.markdown('</div>', unsafe_allow_html=True)

modo = st.radio(
    "Selecciona el tipo de análisis",
    ["Producto individual", "Negocio completo"],
    horizontal=True,
    index=0 if st.session_state.modo_analisis == "Producto individual" else 1
)

st.session_state.modo_analisis = modo

st.divider()


# -------------------------
# FORMULARIO: PRODUCTO
# -------------------------
if modo == "Producto individual":
    st.markdown('<div class="section-title">Análisis por producto</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-muted">Evalúa si un producto específico realmente conviene.</div>', unsafe_allow_html=True)

    with st.form("form_producto"):
        st.markdown("## Paso 1: Identifica tu producto")
        nombre_producto = st.text_input(
            "Nombre del producto",
            value=st.session_state.nombre_producto,
            placeholder="Ej. Mermelada de arándano"
        )

        st.markdown("## Paso 2: Ingresa tus ventas")
        st.caption("Completa los datos y luego presiona Analizar producto.")

        precio = st.number_input(
            "Precio de venta por unidad",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        cantidad = st.number_input(
            "Cantidad vendida del producto",
            min_value=0.0,
            step=1.0,
            value=0.0
        )

        st.markdown("## Paso 3: Calcula tus costos fijos asignados")
        st.info(
            """
Los **costos fijos** son gastos que no cambian aunque vendas más o menos en el corto plazo.

Ejemplos:
- alquiler
- sueldos administrativos
- servicios básicos
- marketing fijo
- licencias o suscripciones

Aquí debes ingresar **la parte de estos costos que corresponde a este producto**.
"""
        )

        alquiler_asignado = st.number_input("Alquiler asignado al producto", min_value=0.0, step=1.0, value=0.0)
        sueldos_asignados = st.number_input("Sueldos administrativos asignados", min_value=0.0, step=1.0, value=0.0)
        servicios_asignados = st.number_input("Servicios asignados al producto", min_value=0.0, step=1.0, value=0.0)
        marketing_fijo = st.number_input("Marketing fijo asignado", min_value=0.0, step=1.0, value=0.0)
        licencias_fijas = st.number_input("Licencias / suscripciones asignadas", min_value=0.0, step=1.0, value=0.0)
        otros_fijos = st.number_input("Otros costos fijos asignados", min_value=0.0, step=1.0, value=0.0)

        costos_fijos = (
            alquiler_asignado
            + sueldos_asignados
            + servicios_asignados
            + marketing_fijo
            + licencias_fijas
            + otros_fijos
        )

        st.caption(
            "El costo fijo total asignado es la suma de todos los costos fijos que este producto debe cubrir, aunque no cambien directamente con cada unidad vendida."
        )

        st.markdown("## Paso 4: Calcula tus costos variables por unidad")
        st.info(
            """
Los **costos variables** cambian directamente con la cantidad producida o vendida.

Ejemplos:
- materia prima
- empaque
- transporte
- comisiones
- mano de obra variable
- otros insumos por unidad

Cada unidad vendida genera estos costos.
"""
        )

        materia = st.number_input("Materia prima por unidad", min_value=0.0, step=1.0, value=0.0)
        empaque = st.number_input("Empaque por unidad", min_value=0.0, step=1.0, value=0.0)
        transporte = st.number_input("Transporte por unidad", min_value=0.0, step=1.0, value=0.0)
        comision = st.number_input("Comisión por unidad", min_value=0.0, step=1.0, value=0.0)
        mano_obra_variable = st.number_input("Mano de obra variable por unidad", min_value=0.0, step=1.0, value=0.0)
        otros_var = st.number_input("Otros costos variables por unidad", min_value=0.0, step=1.0, value=0.0)

        costo_variable = materia + empaque + transporte + comision + mano_obra_variable + otros_var

        st.caption(
            "El costo variable por unidad es la suma de todos los costos que aparecen cada vez que produces o vendes una unidad adicional."
        )

        st.markdown("### Resumen de costos")
        r1, r2 = st.columns(2)
        r1.metric("Costo fijo total asignado", round(costos_fijos, 2))
        r2.metric("Costo variable por unidad", round(costo_variable, 2))

        submit_producto = st.form_submit_button("Analizar producto")

    if submit_producto:
        resultados = calcular_resultados(precio, cantidad, costo_variable, costos_fijos)
        mensajes = analizar_negocio(resultados)

        estado, descripcion = clasificar_estado(resultados["utilidad"], resultados["margen"])
        recomendacion = recomendacion_producto(
            resultados["utilidad"],
            resultados["margen"],
            resultados["punto_equilibrio"],
            cantidad
        )

        st.session_state.analisis_guardado = True
        st.session_state.modo_analisis = "Producto individual"
        st.session_state.nombre_producto = nombre_producto
        st.session_state.datos_base = {
            "precio": precio,
            "cantidad": cantidad,
            "costos_fijos": costos_fijos,
            "costo_variable": costo_variable,
            "detalle_costos_fijos": {
                "alquiler_asignado": alquiler_asignado,
                "sueldos_asignados": sueldos_asignados,
                "servicios_asignados": servicios_asignados,
                "marketing_fijo": marketing_fijo,
                "licencias_fijas": licencias_fijas,
                "otros_fijos": otros_fijos,
            },
            "detalle_costos_variables": {
                "materia": materia,
                "empaque": empaque,
                "transporte": transporte,
                "comision": comision,
                "mano_obra_variable": mano_obra_variable,
                "otros_var": otros_var,
            }
        }
        st.session_state.resultados_base = resultados
        st.session_state.mensajes_base = mensajes
        st.session_state.descripcion_estado = descripcion
        st.session_state.estado_texto = estado
        st.session_state.recomendacion_base = recomendacion


# -------------------------
# FORMULARIO: NEGOCIO
# -------------------------
else:
    st.markdown('<div class="section-title">Análisis del negocio completo</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-muted">Evalúa la salud económica general de toda la operación.</div>', unsafe_allow_html=True)

    with st.form("form_negocio"):
        st.markdown("## Paso 1: Ventas totales del negocio")
        ventas_totales = st.number_input("Ventas totales del período", min_value=0.0, step=1.0, value=0.0)
        unidades_totales = st.number_input("Unidades totales vendidas", min_value=0.0, step=1.0, value=0.0)

        st.markdown("## Paso 2: Costos fijos totales")
        st.info(
            """
Los **costos fijos totales** son los gastos que tu negocio debe pagar independientemente del nivel de ventas.

Ejemplos:
- alquiler
- sueldos fijos
- servicios
"""
        )

        alquiler = st.number_input("Alquiler total", min_value=0.0, step=1.0, value=0.0)
        sueldos = st.number_input("Sueldos fijos totales", min_value=0.0, step=1.0, value=0.0)
        servicios = st.number_input("Servicios totales", min_value=0.0, step=1.0, value=0.0)
        otros_fijos = st.number_input("Otros costos fijos totales", min_value=0.0, step=1.0, value=0.0)

        costos_fijos = alquiler + sueldos + servicios + otros_fijos

        st.markdown("## Paso 3: Costos variables totales")
        st.info(
            """
Los **costos variables totales** aumentan a medida que vendes o produces más.

Ejemplos:
- materia prima total
- transporte total
- comisiones totales
"""
        )

        materia_total = st.number_input("Materia prima total", min_value=0.0, step=1.0, value=0.0)
        transporte_total = st.number_input("Transporte total", min_value=0.0, step=1.0, value=0.0)
        comisiones_total = st.number_input("Comisiones totales", min_value=0.0, step=1.0, value=0.0)
        otros_variables_total = st.number_input("Otros costos variables totales", min_value=0.0, step=1.0, value=0.0)

        costos_variables_totales = materia_total + transporte_total + comisiones_total + otros_variables_total

        precio = ventas_totales / unidades_totales if unidades_totales > 0 else 0
        costo_variable = costos_variables_totales / unidades_totales if unidades_totales > 0 else 0
        cantidad = unidades_totales

        r1, r2, r3 = st.columns(3)
        r1.metric("Ventas totales", round(ventas_totales, 2))
        r2.metric("Costos fijos totales", round(costos_fijos, 2))
        r3.metric("Costos variables totales", round(costos_variables_totales, 2))

        submit_negocio = st.form_submit_button("Analizar negocio completo")

    if submit_negocio:
        resultados = calcular_resultados(precio, cantidad, costo_variable, costos_fijos)
        mensajes = analizar_negocio(resultados)

        estado, descripcion = clasificar_estado(resultados["utilidad"], resultados["margen"])
        recomendacion = recomendacion_negocio(
            resultados["utilidad"],
            resultados["margen"],
            resultados["punto_equilibrio"],
            cantidad
        )

        st.session_state.analisis_guardado = True
        st.session_state.modo_analisis = "Negocio completo"
        st.session_state.nombre_producto = ""
        st.session_state.datos_base = {
            "precio": precio,
            "cantidad": cantidad,
            "costos_fijos": costos_fijos,
            "costo_variable": costo_variable,
            "ventas_totales": ventas_totales,
            "costos_variables_totales": costos_variables_totales
        }
        st.session_state.resultados_base = resultados
        st.session_state.mensajes_base = mensajes
        st.session_state.descripcion_estado = descripcion
        st.session_state.estado_texto = estado
        st.session_state.recomendacion_base = recomendacion


# -------------------------
# RESULTADOS
# -------------------------
if st.session_state.analisis_guardado:
    resultados = st.session_state.resultados_base
    mensajes = st.session_state.mensajes_base
    datos = st.session_state.datos_base
    estado = st.session_state.estado_texto
    descripcion = st.session_state.descripcion_estado
    recomendacion = st.session_state.recomendacion_base

    st.divider()
    st.markdown('<div class="section-title">Resumen ejecutivo</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="{clase_estado_css(estado)}">{estado} — {descripcion}</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Estado", estado)
    c2.metric("Utilidad", round(resultados["utilidad"], 2))
    c3.metric("Margen", f"{round(resultados['margen'] * 100, 2)}%")
    c4.metric("Equilibrio", round(resultados["punto_equilibrio"], 2))

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("### Interpretación de costos y resultado")
    st.write(f"**Costo fijo total:** {round(datos['costos_fijos'], 2)}")
    st.write(f"**Costo variable total:** {round(resultados['costos_variables_totales'], 2)}")
    st.write(f"**Costo total:** {round(resultados['costos_totales'], 2)}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("### Diagnóstico")
    for m in mensajes:
        st.write("•", m)
    st.markdown("### Recomendación clave")
    st.success(recomendacion)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.modo_analisis == "Producto individual":
        with st.expander("Ver desglose de costos del producto"):
            detalle_fijos = datos.get("detalle_costos_fijos", {})
            detalle_variables = datos.get("detalle_costos_variables", {})

            st.markdown("### Costos fijos asignados")
            st.write("• Alquiler asignado:", round(detalle_fijos.get("alquiler_asignado", 0.0), 2))
            st.write("• Sueldos administrativos asignados:", round(detalle_fijos.get("sueldos_asignados", 0.0), 2))
            st.write("• Servicios asignados:", round(detalle_fijos.get("servicios_asignados", 0.0), 2))
            st.write("• Marketing fijo asignado:", round(detalle_fijos.get("marketing_fijo", 0.0), 2))
            st.write("• Licencias / suscripciones:", round(detalle_fijos.get("licencias_fijas", 0.0), 2))
            st.write("• Otros costos fijos:", round(detalle_fijos.get("otros_fijos", 0.0), 2))

            st.markdown("### Costos variables por unidad")
            st.write("• Materia prima:", round(detalle_variables.get("materia", 0.0), 2))
            st.write("• Empaque:", round(detalle_variables.get("empaque", 0.0), 2))
            st.write("• Transporte:", round(detalle_variables.get("transporte", 0.0), 2))
            st.write("• Comisión:", round(detalle_variables.get("comision", 0.0), 2))
            st.write("• Mano de obra variable:", round(detalle_variables.get("mano_obra_variable", 0.0), 2))
            st.write("• Otros costos variables:", round(detalle_variables.get("otros_var", 0.0), 2))

    with st.expander("Ver estructura económica"):
        fig, ax = plt.subplots(figsize=(5, 3))
        etiquetas = ["Variables", "Fijos", "Utilidad"]
        valores = [
            resultados["costos_variables_totales"],
            datos["costos_fijos"],
            max(resultados["utilidad"], 0)
        ]
        ax.bar(etiquetas, valores)
        ax.set_ylabel("Monto")
        st.pyplot(fig)

    with st.expander("Probar simulación"):
        precio_base = float(datos["precio"])
        cantidad_base = float(datos["cantidad"])
        costo_variable_base = float(datos["costo_variable"])
        costos_fijos_base = float(datos["costos_fijos"])

        nuevo_precio = st.slider(
            "Nuevo precio",
            min_value=0.0,
            max_value=float(precio_base * 2) if precio_base > 0 else 10.0,
            value=float(precio_base),
            step=0.1
        )

        nueva_cantidad = st.slider(
            "Nueva cantidad",
            min_value=0.0,
            max_value=float(cantidad_base * 2) if cantidad_base > 0 else 10.0,
            value=float(cantidad_base),
            step=1.0
        )

        sim = calcular_resultados(
            float(nuevo_precio),
            float(nueva_cantidad),
            costo_variable_base,
            costos_fijos_base
        )

        s1, s2, s3 = st.columns(3)
        s1.metric("Utilidad simulada", round(sim["utilidad"], 2))
        s2.metric("Margen simulado", f"{round(sim['margen'] * 100, 2)}%")
        s3.metric("Ingresos simulados", round(sim["ingresos"], 2))

    st.markdown("## Guardar análisis")
    if st.button("💾 Guardar este análisis"):
        guardar_analisis_csv(
            datos,
            resultados,
            st.session_state.modo_analisis,
            st.session_state.nombre_producto
        )
        st.success("Análisis guardado correctamente en historial.csv")


# -------------------------
# HISTORIAL
# -------------------------
st.divider()
st.markdown('<div class="section-title">Historial de análisis guardados</div>', unsafe_allow_html=True)

archivo_historial = "historial.csv"

if os.path.exists(archivo_historial):
    historial_df = pd.read_csv(archivo_historial)

    if not historial_df.empty:
        historial_df["fecha"] = pd.to_datetime(historial_df["fecha"], errors="coerce")
        historial_df["margen_pct"] = historial_df["margen"] * 100

        colf1, colf2 = st.columns(2)
        tipos_disponibles = ["Todos"] + sorted(historial_df["tipo_analisis"].dropna().astype(str).unique().tolist())
        productos_disponibles = ["Todos"] + sorted(historial_df["producto"].dropna().astype(str).unique().tolist())

        filtro_tipo = colf1.selectbox("Filtrar por tipo de análisis", tipos_disponibles)
        filtro_producto = colf2.selectbox("Filtrar por producto", productos_disponibles)

        historial_filtrado = historial_df.copy()

        if filtro_tipo != "Todos":
            historial_filtrado = historial_filtrado[historial_filtrado["tipo_analisis"].astype(str) == filtro_tipo]

        if filtro_producto != "Todos":
            historial_filtrado = historial_filtrado[historial_filtrado["producto"].astype(str) == filtro_producto]

        historial_filtrado = historial_filtrado.sort_values("fecha", ascending=False)

        # -------------------------
        # MÉTRICAS EJECUTIVAS
        # -------------------------
        st.markdown("### Resumen ejecutivo del historial")

        ultimo_registro = historial_filtrado.iloc[0]
        mejor_utilidad = historial_filtrado["utilidad"].max()
        peor_utilidad = historial_filtrado["utilidad"].min()
        margen_promedio = historial_filtrado["margen_pct"].mean()
        ultimo_producto = str(ultimo_registro["producto"])
        ultima_fecha = str(ultimo_registro["fecha"])

        e1, e2, e3 = st.columns(3)
        e4, e5, e6 = st.columns(3)

        e1.metric("Análisis filtrados", len(historial_filtrado))
        e2.metric("Último producto", ultimo_producto)
        e3.metric("Mejor utilidad", round(mejor_utilidad, 2))
        e4.metric("Peor utilidad", round(peor_utilidad, 2))
        e5.metric("Margen promedio", f"{round(margen_promedio, 2)}%")
        e6.metric("Último análisis", ultima_fecha)

        # -------------------------
        # COMPARACIÓN DE PRODUCTOS
        # -------------------------
        resumen_prod = resumen_productos(historial_filtrado)

        if not resumen_prod.empty:
            st.markdown("### Comparación entre productos")

            prod_mas_rentable = resumen_prod.iloc[0]
            prod_mas_riesgoso = resumen_prod.sort_values("utilidad_promedio", ascending=True).iloc[0]
            prod_mejor_margen = resumen_prod.sort_values("margen_promedio", ascending=False).iloc[0]
            prod_peor_margen = resumen_prod.sort_values("margen_promedio", ascending=True).iloc[0]
            prod_mas_analizado = resumen_prod.sort_values("analisis", ascending=False).iloc[0]

            p1, p2, p3 = st.columns(3)
            p4, p5 = st.columns(2)

            p1.metric(
                "Producto más rentable",
                str(prod_mas_rentable["producto"]),
                f"Utilidad prom. {round(prod_mas_rentable['utilidad_promedio'], 2)}"
            )
            p2.metric(
                "Producto más riesgoso",
                str(prod_mas_riesgoso["producto"]),
                f"Utilidad prom. {round(prod_mas_riesgoso['utilidad_promedio'], 2)}"
            )
            p3.metric(
                "Mayor margen promedio",
                str(prod_mejor_margen["producto"]),
                f"{round(prod_mejor_margen['margen_promedio'], 2)}%"
            )
            p4.metric(
                "Peor margen promedio",
                str(prod_peor_margen["producto"]),
                f"{round(prod_peor_margen['margen_promedio'], 2)}%"
            )
            p5.metric(
                "Producto más analizado",
                str(prod_mas_analizado["producto"]),
                f"{int(prod_mas_analizado['analisis'])} análisis"
            )

            with st.expander("Ver tabla comparativa de productos"):
                tabla_productos = resumen_prod.copy()
                tabla_productos["utilidad_promedio"] = tabla_productos["utilidad_promedio"].round(2)
                tabla_productos["mejor_utilidad"] = tabla_productos["mejor_utilidad"].round(2)
                tabla_productos["peor_utilidad"] = tabla_productos["peor_utilidad"].round(2)
                tabla_productos["margen_promedio"] = tabla_productos["margen_promedio"].round(2)
                tabla_productos["ingresos_promedio"] = tabla_productos["ingresos_promedio"].round(2)
                st.dataframe(tabla_productos, use_container_width=True)

        g1, g2, g3 = st.columns(3)

        if g1.button("🗑️ Borrar todo el historial"):
            os.remove(archivo_historial)
            st.success("Se eliminó todo el historial.")
            st.rerun()

        if g2.button("🧹 Borrar solo los datos filtrados"):
            historial_completo = pd.read_csv(archivo_historial)
            historial_completo["fecha"] = pd.to_datetime(historial_completo["fecha"], errors="coerce")

            fechas_filtradas = set(historial_filtrado["fecha"].astype(str))
            tipos_filtrados = set(historial_filtrado["tipo_analisis"].astype(str))
            productos_filtrados = set(historial_filtrado["producto"].astype(str))

            restante = historial_completo[
                ~(
                    historial_completo["fecha"].astype(str).isin(fechas_filtradas)
                    & historial_completo["tipo_analisis"].astype(str).isin(tipos_filtrados)
                    & historial_completo["producto"].astype(str).isin(productos_filtrados)
                )
            ].copy()

            guardar_historial_df(restante)
            st.success("Se eliminaron los registros filtrados.")
            st.rerun()

        csv_descarga = historial_filtrado.copy()
        csv_descarga["fecha"] = csv_descarga["fecha"].astype(str)
        csv_bytes = csv_descarga.to_csv(index=False).encode("utf-8")

        g3.download_button(
            label="⬇️ Descargar historial filtrado",
            data=csv_bytes,
            file_name="historial_filtrado_valora.csv",
            mime="text/csv"
        )

        tabla_mostrar = historial_filtrado.copy()
        tabla_mostrar["margen_pct"] = tabla_mostrar["margen_pct"].round(2)

        columnas_preferidas = [
            "fecha",
            "tipo_analisis",
            "producto",
            "ingresos",
            "costos_fijos",
            "costos_variables_totales",
            "costos_totales",
            "utilidad",
            "margen_pct",
            "punto_equilibrio"
        ]
        columnas_visibles = [c for c in columnas_preferidas if c in tabla_mostrar.columns]
        st.dataframe(tabla_mostrar[columnas_visibles], use_container_width=True)

        with st.expander("Ver dashboard histórico"):
            if len(historial_filtrado) > 0:
                historial_graf = historial_filtrado.sort_values("fecha", ascending=True).copy()

                m1, m2, m3 = st.columns(3)
                m1.metric("Análisis guardados", len(historial_filtrado))
                m2.metric("Utilidad promedio", round(historial_filtrado["utilidad"].mean(), 2))
                m3.metric("Ingresos promedio", round(historial_filtrado["ingresos"].mean(), 2))

                fig1, ax1 = plt.subplots(figsize=(8, 4))
                ax1.plot(historial_graf["fecha"], historial_graf["utilidad"], marker="o")
                ax1.set_title("Utilidad en el tiempo")
                ax1.set_xlabel("Fecha")
                ax1.set_ylabel("Utilidad")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig1)

                fig2, ax2 = plt.subplots(figsize=(8, 4))
                ax2.plot(historial_graf["fecha"], historial_graf["margen_pct"], marker="o")
                ax2.set_title("Margen porcentual en el tiempo")
                ax2.set_xlabel("Fecha")
                ax2.set_ylabel("Margen (%)")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig2)

                fig3, ax3 = plt.subplots(figsize=(8, 4))
                ax3.plot(historial_graf["fecha"], historial_graf["ingresos"], marker="o", label="Ingresos")
                ax3.plot(historial_graf["fecha"], historial_graf["costos_totales"], marker="o", label="Costos totales")
                ax3.set_title("Ingresos y costos totales en el tiempo")
                ax3.set_xlabel("Fecha")
                ax3.set_ylabel("Monto")
                ax3.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig3)
    else:
        st.info("Todavía no hay análisis guardados.")
else:
    st.info("Todavía no hay análisis guardados.")
