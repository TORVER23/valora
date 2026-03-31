import streamlit as st
from calculos import calcular_resultados
from analisis import analizar_negocio
from utils import guardar_analisis_csv, clase_estado_css
from styles import aplicar_estilos

st.set_page_config(page_title="VALORA", page_icon="📈", layout="centered")
aplicar_estilos()


# -------------------------
# FUNCIONES LOCALES
# -------------------------
def clasificar_estado(utilidad, margen):
    if utilidad < 0:
        return "🔴 Crítico", "La operación está generando pérdidas."
    elif margen < 0.1:
        return "🟡 En riesgo", "Existe utilidad, pero el margen es bajo."
    else:
        return "🟢 Saludable", "La estructura es rentable."


def recomendacion_producto(utilidad, margen, punto_equilibrio, cantidad):
    if utilidad < 0:
        return "Este producto no está siendo rentable. Revisa su precio, su costo variable o la cantidad vendida."
    elif punto_equilibrio > cantidad:
        return "Este producto todavía no alcanza su punto de equilibrio. Necesitas vender más unidades o mejorar su margen."
    elif margen < 0.1:
        return "Este producto deja poca utilidad por venta. Evalúa subir precio o reducir costos variables."
    else:
        return "Este producto tiene una estructura sana. Puede ser una línea conveniente para impulsar."


def recomendacion_negocio(utilidad, margen, punto_equilibrio, cantidad):
    if utilidad < 0:
        return "Tu negocio completo no está siendo sostenible. Debes actuar sobre costos, ventas o precios."
    elif punto_equilibrio > cantidad:
        return "Tu operación general todavía no cubre bien su estructura de costos. Necesitas aumentar ventas o mejorar rentabilidad."
    elif margen < 0.1:
        return "Tu empresa genera utilidad, pero con muy poca holgura. Un cambio pequeño en costos podría afectarte."
    else:
        return "Tu negocio tiene una base saludable. El siguiente paso es optimizar y crecer."


def interpretar_utilidad(utilidad):
    if utilidad < 0:
        return "La utilidad es negativa: el escenario actual destruye valor."
    elif utilidad == 0:
        return "La utilidad es cero: la operación está exactamente en equilibrio."
    else:
        return "La utilidad es positiva: después de cubrir costos, la operación sí genera ganancia."


def interpretar_margen(margen):
    if margen < 0:
        return "El margen es negativo: la estructura actual es inviable."
    elif margen < 0.1:
        return "El margen es bajo: la rentabilidad sigue siendo frágil."
    elif margen < 0.2:
        return "El margen es aceptable, aunque todavía existe espacio de mejora."
    else:
        return "El margen es sólido: la operación retiene una parte saludable de los ingresos como utilidad."


def interpretar_equilibrio(punto_equilibrio, cantidad):
    if punto_equilibrio > cantidad:
        return "Todavía no se alcanza el punto de equilibrio con el nivel actual de ventas."
    elif punto_equilibrio == 0:
        return "No se pudo estimar un punto de equilibrio útil con estos valores."
    else:
        return "El nivel actual de ventas ya supera el punto de equilibrio."


def acciones_sugeridas(utilidad, margen, punto_equilibrio, cantidad):
    acciones = []

    if utilidad < 0:
        acciones.append("Revisar si el precio actual es demasiado bajo para la estructura de costos.")
        acciones.append("Buscar reducción de costos variables antes de intentar crecer por volumen.")
    if punto_equilibrio > cantidad:
        acciones.append("Aumentar ventas o mejorar margen para alcanzar el equilibrio.")
    if margen < 0.1:
        acciones.append("Trabajar en mejorar el margen subiendo precio o reduciendo costos variables.")
    if utilidad > 0 and margen >= 0.2:
        acciones.append("Este escenario puede servir como base para crecer o impulsar esta línea.")
    if not acciones:
        acciones.append("Mantener seguimiento del desempeño para confirmar que el buen resultado se repita.")

    return acciones


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
# CABECERA
# -------------------------
st.markdown('<div class="main-title">VALORA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Herramienta de análisis económico para tomar mejores decisiones de negocio</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="soft-card">', unsafe_allow_html=True)
st.markdown("### ¿Qué puedes hacer aquí?")
st.markdown(
    """
VALORA te permite evaluar si un producto o negocio:

- está generando utilidad real
- tiene una estructura de costos saludable
- necesita ajustes en precio, costos o volumen

Obtendrás:
- diagnóstico automático
- interpretación económica
- recomendaciones accionables
"""
)

st.markdown("### ¿Cómo usar la app?")
st.markdown(
    """
1. Ingresa los datos  
2. Analiza el resultado  
3. Guarda el análisis  
4. Usa las demás secciones de la plataforma  
"""
)

st.markdown("### Flujo recomendado")
st.markdown(
    """
1. Analizar  
2. Guardar  
3. Revisar historial  
4. Comparar  
5. Ver recomendaciones  
6. Consultar dashboard  
7. Revisar reporte  
"""
)

st.info("Si no entiendes alguna variable, revisa la Guía económica en el menú lateral.")
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
        st.caption("Usa un nombre claro para identificarlo luego en historial, comparaciones, recomendaciones y reporte.")

        st.markdown("## Paso 2: Ingresa tus ventas")
        st.caption("Aquí defines cuánto vendes y a qué precio. Esto determina tus ingresos.")

        precio = st.number_input(
            "Precio de venta por unidad",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        st.caption("Cuánto pagará el cliente por cada unidad del producto.")

        cantidad = st.number_input(
            "Cantidad vendida del producto",
            min_value=0.0,
            step=1.0,
            value=0.0
        )
        st.caption("Cuántas unidades esperas vender en el período analizado.")

        st.markdown("## Paso 3: Costos fijos asignados")
        st.caption("Son costos que debes pagar aunque vendas poco o nada.")

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

        st.markdown("## Paso 4: Costos variables por unidad")
        st.caption("Estos costos aumentan por cada unidad que vendes.")

        materia = st.number_input("Materia prima por unidad", min_value=0.0, step=1.0, value=0.0)
        empaque = st.number_input("Empaque por unidad", min_value=0.0, step=1.0, value=0.0)
        transporte = st.number_input("Transporte por unidad", min_value=0.0, step=1.0, value=0.0)
        comision = st.number_input("Comisión por unidad", min_value=0.0, step=1.0, value=0.0)
        mano_obra_variable = st.number_input("Mano de obra variable por unidad", min_value=0.0, step=1.0, value=0.0)
        otros_var = st.number_input("Otros costos variables por unidad", min_value=0.0, step=1.0, value=0.0)

        costo_variable = materia + empaque + transporte + comision + mano_obra_variable + otros_var

        st.markdown("### Resumen rápido del producto")
        r1, r2 = st.columns(2)
        r1.metric("Costo fijo total asignado", round(costos_fijos, 2))
        r2.metric("Costo variable por unidad", round(costo_variable, 2))

        st.caption("Este es el total de costos fijos que este producto debe cubrir.")
        st.caption("Este es el costo adicional que se genera por cada unidad vendida.")

        submit_producto = st.form_submit_button("🔍 Analizar producto")

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
        st.markdown("## Paso 1: Ventas totales del período")
        st.caption("Aquí defines el tamaño total de la operación que quieres analizar.")

        ventas_totales = st.number_input("Ventas totales del período", min_value=0.0, step=1.0, value=0.0)
        st.caption("Es el dinero total generado por todas las ventas del período.")

        unidades_totales = st.number_input("Unidades totales vendidas", min_value=0.0, step=1.0, value=0.0)
        st.caption("Sirve para estimar precio promedio y costo variable promedio por unidad.")

        st.markdown("## Paso 2: Costos fijos totales")
        st.caption("Son los costos que el negocio debe cubrir aunque venda poco o nada.")

        alquiler = st.number_input("Alquiler total", min_value=0.0, step=1.0, value=0.0)
        sueldos = st.number_input("Sueldos fijos totales", min_value=0.0, step=1.0, value=0.0)
        servicios = st.number_input("Servicios totales", min_value=0.0, step=1.0, value=0.0)
        otros_fijos = st.number_input("Otros costos fijos totales", min_value=0.0, step=1.0, value=0.0)

        costos_fijos = alquiler + sueldos + servicios + otros_fijos

        st.markdown("## Paso 3: Costos variables totales")
        st.caption("Estos costos aumentan a medida que el negocio vende o produce más.")

        materia_total = st.number_input("Materia prima total", min_value=0.0, step=1.0, value=0.0)
        transporte_total = st.number_input("Transporte total", min_value=0.0, step=1.0, value=0.0)
        comisiones_total = st.number_input("Comisiones totales", min_value=0.0, step=1.0, value=0.0)
        otros_variables_total = st.number_input("Otros costos variables totales", min_value=0.0, step=1.0, value=0.0)

        costos_variables_totales = materia_total + transporte_total + comisiones_total + otros_variables_total

        precio = ventas_totales / unidades_totales if unidades_totales > 0 else 0
        costo_variable = costos_variables_totales / unidades_totales if unidades_totales > 0 else 0
        cantidad = unidades_totales

        st.markdown("### Resumen rápido del negocio")
        r1, r2, r3 = st.columns(3)
        r1.metric("Ventas totales", round(ventas_totales, 2))
        r2.metric("Costos fijos totales", round(costos_fijos, 2))
        r3.metric("Costos variables totales", round(costos_variables_totales, 2))

        st.caption("Este bloque resume el tamaño general de tu operación antes de calcular resultados.")

        submit_negocio = st.form_submit_button("🔍 Analizar negocio")

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
# RESULTADO ACTUAL
# -------------------------
if st.session_state.analisis_guardado:
    resultados = st.session_state.resultados_base
    datos = st.session_state.datos_base
    estado = st.session_state.estado_texto
    descripcion = st.session_state.descripcion_estado
    recomendacion = st.session_state.recomendacion_base
    mensajes = st.session_state.mensajes_base

    st.divider()
    st.markdown("## Resultado del análisis")
    st.caption("Este bloque resume la situación económica actual según los datos ingresados.")

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
    st.markdown("### Interpretación ejecutiva")
    st.write(interpretar_utilidad(resultados["utilidad"]))
    st.write(interpretar_margen(resultados["margen"]))
    st.write(interpretar_equilibrio(resultados["punto_equilibrio"], datos["cantidad"]))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("### Diagnóstico")
    for m in mensajes:
        st.write("•", m)

    st.markdown("### Recomendación principal")
    st.success(recomendacion)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("### Acciones sugeridas")
    for accion in acciones_sugeridas(
        resultados["utilidad"],
        resultados["margen"],
        resultados["punto_equilibrio"],
        datos["cantidad"]
    ):
        st.write("•", accion)
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

    with st.expander("Ver simulación del escenario"):
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

    st.success("Análisis completado correctamente. Puedes guardarlo o explorar otras secciones.")

    if st.button("💾 Guardar análisis"):
        guardar_analisis_csv(
            datos,
            resultados,
            st.session_state.modo_analisis,
            st.session_state.nombre_producto
        )
        st.success("Análisis guardado correctamente en historial.csv")
