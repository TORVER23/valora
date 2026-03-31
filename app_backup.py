import streamlit as st
import matplotlib.pyplot as plt

from calculos import calcular_resultados
from analisis import analizar_negocio

st.set_page_config(page_title="VALORA", page_icon="📈", layout="centered")


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
st.title("VALORA")
st.caption("Asesor económico para decisiones de negocio")

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
    st.subheader("Análisis por producto")
    st.write("Evalúa si un producto específico realmente conviene.")

    with st.form("form_producto"):
        st.markdown("## Paso 1: Identifica tu producto")
        nombre_producto = st.text_input(
            "Nombre del producto",
            value=st.session_state.nombre_producto,
            placeholder="Ej. Mermelada de arándano"
        )

        st.markdown("## Paso 2: Ingresa tus ventas")
        st.caption("Completa los datos y luego presiona Analizar producto.")

        precio = st.number_input("Precio de venta por unidad", min_value=0.0, step=1.0, value=0.0)
        cantidad = st.number_input("Cantidad vendida del producto", min_value=0.0, step=1.0, value=0.0)

        st.markdown("## Paso 3: Costos fijos asignados")
        st.caption("Ingresa solo la parte de costos fijos que corresponde a este producto.")
        costos_fijos = st.number_input("Costos fijos asignados al producto", min_value=0.0, step=1.0, value=0.0)

        st.markdown("## Paso 4: Costos variables por unidad")
        materia = st.number_input("Materia prima por unidad", min_value=0.0, step=1.0, value=0.0)
        empaque = st.number_input("Empaque por unidad", min_value=0.0, step=1.0, value=0.0)
        transporte = st.number_input("Transporte por unidad", min_value=0.0, step=1.0, value=0.0)
        comision = st.number_input("Comisión por unidad", min_value=0.0, step=1.0, value=0.0)
        otros_var = st.number_input("Otros costos variables por unidad", min_value=0.0, step=1.0, value=0.0)

        costo_variable = materia + empaque + transporte + comision + otros_var

        st.markdown("### Resumen de costos")
        r1, r2 = st.columns(2)
        r1.metric("Costo fijo asignado", round(costos_fijos, 2))
        r2.metric("Costo variable por unidad", round(costo_variable, 2))

        submit_producto = st.form_submit_button("Analizar producto")

    if submit_producto:
        resultados = calcular_resultados(precio, cantidad, costo_variable, costos_fijos)
        mensajes = analizar_negocio(resultados)

        estado, descripcion = clasificar_estado(
            resultados["utilidad"],
            resultados["margen"]
        )

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
            "costo_variable": costo_variable
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
    st.subheader("Análisis del negocio completo")
    st.write("Evalúa la salud económica general de toda la operación.")

    with st.form("form_negocio"):
        st.markdown("## Paso 1: Ventas totales del negocio")
        ventas_totales = st.number_input("Ventas totales del período", min_value=0.0, step=1.0, value=0.0)
        unidades_totales = st.number_input("Unidades totales vendidas", min_value=0.0, step=1.0, value=0.0)

        st.markdown("## Paso 2: Costos fijos totales")
        alquiler = st.number_input("Alquiler total", min_value=0.0, step=1.0, value=0.0)
        sueldos = st.number_input("Sueldos fijos totales", min_value=0.0, step=1.0, value=0.0)
        servicios = st.number_input("Servicios totales", min_value=0.0, step=1.0, value=0.0)
        otros_fijos = st.number_input("Otros costos fijos totales", min_value=0.0, step=1.0, value=0.0)

        costos_fijos = alquiler + sueldos + servicios + otros_fijos

        st.markdown("## Paso 3: Costos variables totales")
        materia_total = st.number_input("Materia prima total", min_value=0.0, step=1.0, value=0.0)
        transporte_total = st.number_input("Transporte total", min_value=0.0, step=1.0, value=0.0)
        comisiones_total = st.number_input("Comisiones totales", min_value=0.0, step=1.0, value=0.0)
        otros_variables_total = st.number_input("Otros costos variables totales", min_value=0.0, step=1.0, value=0.0)

        costos_variables_totales = (
            materia_total + transporte_total + comisiones_total + otros_variables_total
        )

        precio = ventas_totales / unidades_totales if unidades_totales > 0 else 0
        costo_variable = costos_variables_totales / unidades_totales if unidades_totales > 0 else 0
        cantidad = unidades_totales

        st.markdown("### Resumen de estructura general")
        r1, r2, r3 = st.columns(3)
        r1.metric("Ventas totales", round(ventas_totales, 2))
        r2.metric("Costos fijos totales", round(costos_fijos, 2))
        r3.metric("Costos variables totales", round(costos_variables_totales, 2))

        submit_negocio = st.form_submit_button("Analizar negocio completo")

    if submit_negocio:
        resultados = calcular_resultados(precio, cantidad, costo_variable, costos_fijos)
        mensajes = analizar_negocio(resultados)

        estado, descripcion = clasificar_estado(
            resultados["utilidad"],
            resultados["margen"]
        )

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
# BLOQUE DE RESULTADOS
# -------------------------
if st.session_state.analisis_guardado:
    resultados = st.session_state.resultados_base
    mensajes = st.session_state.mensajes_base
    datos = st.session_state.datos_base
    estado = st.session_state.estado_texto
    descripcion = st.session_state.descripcion_estado
    recomendacion = st.session_state.recomendacion_base

    st.divider()

    if st.session_state.modo_analisis == "Producto individual":
        titulo = st.session_state.nombre_producto if st.session_state.nombre_producto else "Producto analizado"
        st.markdown("## Resumen ejecutivo")
        st.markdown(f"### {titulo}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estado", estado)
        c2.metric("Utilidad", round(resultados["utilidad"], 2))
        c3.metric("Margen", f"{round(resultados['margen'] * 100, 2)}%")
        c4.metric("Equilibrio", round(resultados["punto_equilibrio"], 2))

        st.info(descripcion)

        st.markdown("## Diagnóstico del producto")
        for m in mensajes:
            st.write("•", m)

        st.markdown("## Recomendación clave")
        st.success(recomendacion)

        with st.expander("Ver estructura económica del producto"):
            fig, ax = plt.subplots(figsize=(4.5, 3))
            labels = ["Variables", "Fijos", "Utilidad"]
            values = [
                resultados["costos_variables_totales"],
                datos["costos_fijos"],
                max(resultados["utilidad"], 0)
            ]
            ax.bar(labels, values)
            ax.set_title("Distribución económica del producto")
            ax.set_ylabel("Monto")
            st.pyplot(fig)

        with st.expander("Probar simulación del producto"):
            nuevo_precio = st.slider(
                "Nuevo precio del producto",
                0.0,
                datos["precio"] * 2 if datos["precio"] > 0 else 10.0,
                datos["precio"]
            )
            nueva_cantidad = st.slider(
                "Nueva cantidad vendida del producto",
                0.0,
                datos["cantidad"] * 2 if datos["cantidad"] > 0 else 10.0,
                datos["cantidad"]
            )

            sim = calcular_resultados(
                nuevo_precio,
                nueva_cantidad,
                datos["costo_variable"],
                datos["costos_fijos"]
            )

            s1, s2, s3 = st.columns(3)
            s1.metric("Utilidad simulada", round(sim["utilidad"], 2))
            s2.metric("Margen simulado", f"{round(sim['margen'] * 100, 2)}%")
            s3.metric("Ingresos simulados", round(sim["ingresos"], 2))

            if sim["utilidad"] > resultados["utilidad"]:
                st.success("Este escenario mejora el desempeño del producto.")
            elif sim["utilidad"] < resultados["utilidad"]:
                st.warning("Este escenario empeora el desempeño del producto.")
            else:
                st.info("Este escenario mantiene un resultado similar.")

    else:
        st.markdown("## Resumen ejecutivo del negocio")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estado", estado)
        c2.metric("Resultado operativo", round(resultados["utilidad"], 2))
        c3.metric("Margen operativo", f"{round(resultados['margen'] * 100, 2)}%")
        c4.metric("Equilibrio estimado", round(resultados["punto_equilibrio"], 2))

        st.info(descripcion)

        st.markdown("## Diagnóstico general")
        for m in mensajes:
            st.write("•", m)

        st.markdown("## Recomendación clave")
        st.success(recomendacion)

        with st.expander("Ver estructura económica del negocio"):
            fig, ax = plt.subplots(figsize=(4.5, 3))
            labels = ["Variables", "Fijos", "Resultado"]
            values = [
                resultados["costos_variables_totales"],
                datos["costos_fijos"],
                max(resultados["utilidad"], 0)
            ]
            ax.bar(labels, values)
            ax.set_title("Distribución económica del negocio")
            ax.set_ylabel("Monto")
            st.pyplot(fig)

        with st.expander("Probar simulación del negocio"):
            ventas_totales = datos.get("ventas_totales", resultados["ingresos"])
            cantidad_base = datos["cantidad"]

            nuevas_ventas = st.slider(
                "Nuevas ventas totales",
                0.0,
                ventas_totales * 2 if ventas_totales > 0 else 10.0,
                ventas_totales
            )
            nuevas_unidades = st.slider(
                "Nuevas unidades vendidas",
                0.0,
                cantidad_base * 2 if cantidad_base > 0 else 10.0,
                cantidad_base
            )

            nuevo_precio = nuevas_ventas / nuevas_unidades if nuevas_unidades > 0 else 0

            sim = calcular_resultados(
                nuevo_precio,
                nuevas_unidades,
                datos["costo_variable"],
                datos["costos_fijos"]
            )

            s1, s2, s3 = st.columns(3)
            s1.metric("Resultado simulado", round(sim["utilidad"], 2))
            s2.metric("Margen simulado", f"{round(sim['margen'] * 100, 2)}%")
            s3.metric("Ventas simuladas", round(sim["ingresos"], 2))

            if sim["utilidad"] > resultados["utilidad"]:
                st.success("Este escenario mejora el desempeño general del negocio.")
            elif sim["utilidad"] < resultados["utilidad"]:
                st.warning("Este escenario empeora el desempeño general del negocio.")
            else:
                st.info("Este escenario mantiene un resultado similar.")

    st.divider()
    st.caption("Próximo paso: guardar cada análisis en base de datos para ver evolución en el tiempo.")

