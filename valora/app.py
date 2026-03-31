import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

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


def cargar_historial():
    archivo = "historial.csv"
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    return pd.DataFrame()


def guardar_historial_df(df):
    archivo = "historial.csv"
    if df.empty:
        if os.path.exists(archivo):
            os.remove(archivo)
    else:
        df.to_csv(archivo, index=False)


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

st.markdown("## ¿Cómo funciona este análisis?")
st.info(
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

        alquiler_asignado = st.number_input(
            "Alquiler asignado al producto",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        sueldos_asignados = st.number_input(
            "Sueldos administrativos asignados",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        servicios_asignados = st.number_input(
            "Servicios asignados al producto",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        marketing_fijo = st.number_input(
            "Marketing fijo asignado",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        licencias_fijas = st.number_input(
            "Licencias / suscripciones asignadas",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        otros_fijos = st.number_input(
            "Otros costos fijos asignados",
            min_value=0.0,
            step=1.0,
            value=0.0
        )

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

        materia = st.number_input(
            "Materia prima por unidad",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        empaque = st.number_input(
            "Empaque por unidad",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        transporte = st.number_input(
            "Transporte por unidad",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        comision = st.number_input(
            "Comisión por unidad",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        mano_obra_variable = st.number_input(
            "Mano de obra variable por unidad",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        otros_var = st.number_input(
            "Otros costos variables por unidad",
            min_value=0.0,
            step=1.0,
            value=0.0
        )

        costo_variable = (
            materia
            + empaque
            + transporte
            + comision
            + mano_obra_variable
            + otros_var
        )

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
    st.subheader("Análisis del negocio completo")
    st.write("Evalúa la salud económica general de toda la operación.")

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

Estos costos definen la base mínima que tu negocio necesita cubrir.
"""
        )

        alquiler = st.number_input("Alquiler total", min_value=0.0, step=1.0, value=0.0)
        sueldos = st.number_input("Sueldos fijos totales", min_value=0.0, step=1.0, value=0.0)
        servicios = st.number_input("Servicios totales", min_value=0.0, step=1.0, value=0.0)
        otros_fijos = st.number_input("Otros costos fijos totales", min_value=0.0, step=1.0, value=0.0)

        costos_fijos = alquiler + sueldos + servicios + otros_fijos

        st.caption(
            "Los costos fijos totales son la suma de todos los gastos que el negocio debe cubrir aunque venda poco o nada."
        )

        st.markdown("## Paso 3: Costos variables totales")
        st.info(
            """
Los **costos variables totales** aumentan a medida que vendes o produces más.

Ejemplos:
- materia prima total
- transporte total
- comisiones totales

Reflejan cuánto te cuesta operar al nivel actual de ventas.
"""
        )

        materia_total = st.number_input("Materia prima total", min_value=0.0, step=1.0, value=0.0)
        transporte_total = st.number_input("Transporte total", min_value=0.0, step=1.0, value=0.0)
        comisiones_total = st.number_input("Comisiones totales", min_value=0.0, step=1.0, value=0.0)
        otros_variables_total = st.number_input("Otros costos variables totales", min_value=0.0, step=1.0, value=0.0)

        costos_variables_totales = (
            materia_total + transporte_total + comisiones_total + otros_variables_total
        )

        st.caption(
            "Los costos variables totales representan el gasto total que cambia con el nivel de producción o ventas."
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

        st.markdown("## Interpretación de costos y resultado")
        st.write(f"**Costo fijo total:** {round(datos['costos_fijos'], 2)}")
        st.caption("Es el monto fijo asignado a este producto. No cambia directamente con cada unidad vendida en el corto plazo.")

        st.write(f"**Costo variable total:** {round(resultados['costos_variables_totales'], 2)}")
        st.caption("Se obtiene multiplicando el costo variable por unidad por la cantidad vendida. Este costo crece cuando vendes más unidades.")

        st.write(f"**Costo total:** {round(resultados['costos_totales'], 2)}")
        st.caption("Es la suma del costo fijo total y del costo variable total. Representa el gasto completo asociado al producto.")

        st.markdown("## Diagnóstico del producto")
        for m in mensajes:
            st.write("•", m)

        st.markdown("## Recomendación clave")
        st.success(recomendacion)

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
            st.write("**Total costos fijos asignados:**", round(datos["costos_fijos"], 2))

            st.markdown("### Costos variables por unidad")
            st.write("• Materia prima:", round(detalle_variables.get("materia", 0.0), 2))
            st.write("• Empaque:", round(detalle_variables.get("empaque", 0.0), 2))
            st.write("• Transporte:", round(detalle_variables.get("transporte", 0.0), 2))
            st.write("• Comisión:", round(detalle_variables.get("comision", 0.0), 2))
            st.write("• Mano de obra variable:", round(detalle_variables.get("mano_obra_variable", 0.0), 2))
            st.write("• Otros costos variables:", round(detalle_variables.get("otros_var", 0.0), 2))
            st.write("**Costo variable por unidad:**", round(datos["costo_variable"], 2))

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

        st.markdown("## Interpretación de costos y resultado")
        st.write(f"**Costo fijo total:** {round(datos['costos_fijos'], 2)}")
        st.caption("Es la suma de los gastos fijos del negocio. Deben pagarse incluso si las ventas bajan.")

        st.write(f"**Costo variable total:** {round(resultados['costos_variables_totales'], 2)}")
        st.caption("Representa el costo total asociado al volumen actual de operación. Aumenta cuando el negocio vende o produce más.")

        st.write(f"**Costo total:** {round(resultados['costos_totales'], 2)}")
        st.caption("Es la suma de los costos fijos totales y los costos variables totales. Refleja el gasto completo de la operación.")

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

    st.markdown("## Guardar análisis")
    if st.button("💾 Guardar este análisis"):
        guardar_analisis_csv(
            datos,
            resultados,
            st.session_state.modo_analisis,
            st.session_state.nombre_producto
        )
        st.success("Análisis guardado correctamente en historial.csv")

    st.divider()
    st.caption("Próximo paso: guardar cada análisis en base de datos para ver evolución en el tiempo.")


# -------------------------
# HISTORIAL CSV + DASHBOARD
# -------------------------
st.divider()
st.markdown("## Historial de análisis guardados")

archivo_historial = "historial.csv"

if os.path.exists(archivo_historial):
    historial_df = pd.read_csv(archivo_historial)

    if not historial_df.empty:
        historial_df["fecha"] = pd.to_datetime(historial_df["fecha"], errors="coerce")
        historial_df["margen_pct"] = historial_df["margen"] * 100

        st.markdown("### Filtros")
        col_f1, col_f2 = st.columns(2)

        tipos_disponibles = ["Todos"] + sorted(historial_df["tipo_analisis"].dropna().astype(str).unique().tolist())
        filtro_tipo = col_f1.selectbox("Filtrar por tipo de análisis", tipos_disponibles)

        productos_disponibles = ["Todos"] + sorted(historial_df["producto"].dropna().astype(str).unique().tolist())
        filtro_producto = col_f2.selectbox("Filtrar por producto", productos_disponibles)

        historial_filtrado = historial_df.copy()

        if filtro_tipo != "Todos":
            historial_filtrado = historial_filtrado[historial_filtrado["tipo_analisis"].astype(str) == filtro_tipo]

        if filtro_producto != "Todos":
            historial_filtrado = historial_filtrado[historial_filtrado["producto"].astype(str) == filtro_producto]

        historial_filtrado = historial_filtrado.sort_values("fecha", ascending=False)

        st.markdown("### Gestión del historial")
        g1, g2, g3 = st.columns(3)

        if g1.button("🗑️ Borrar todo el historial"):
            if os.path.exists(archivo_historial):
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
        if "fecha" in csv_descarga.columns:
            csv_descarga["fecha"] = csv_descarga["fecha"].astype(str)

        csv_bytes = csv_descarga.to_csv(index=False).encode("utf-8")

        g3.download_button(
            label="⬇️ Descargar historial filtrado",
            data=csv_bytes,
            file_name="historial_filtrado_valora.csv",
            mime="text/csv"
        )

        st.markdown("### Tabla de historial")
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

                st.markdown("### Evolución de la utilidad")
                fig1, ax1 = plt.subplots(figsize=(8, 4))
                ax1.plot(historial_graf["fecha"], historial_graf["utilidad"], marker="o")
                ax1.set_title("Utilidad en el tiempo")
                ax1.set_xlabel("Fecha")
                ax1.set_ylabel("Utilidad")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig1)

                st.markdown("### Evolución del margen")
                fig2, ax2 = plt.subplots(figsize=(8, 4))
                ax2.plot(historial_graf["fecha"], historial_graf["margen_pct"], marker="o")
                ax2.set_title("Margen porcentual en el tiempo")
                ax2.set_xlabel("Fecha")
                ax2.set_ylabel("Margen (%)")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig2)

                st.markdown("### Ingresos vs costos totales")
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
                st.info("No hay datos que coincidan con los filtros seleccionados.")
    else:
        st.info("Todavía no hay análisis guardados.")
else:
    st.info("Todavía no hay análisis guardados.")
