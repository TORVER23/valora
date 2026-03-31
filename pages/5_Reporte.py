import streamlit as st
from styles import aplicar_estilos
from utils import clase_estado_css
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO

st.set_page_config(page_title="Reporte - VALORA", page_icon="🧾", layout="centered")
aplicar_estilos()

st.title("Reporte ejecutivo")
st.caption("Versión formal del análisis actual")


def construir_acciones(resultados, datos):
    acciones = []

    if resultados["utilidad"] < 0:
        acciones.append("Revisar si el precio actual es demasiado bajo para la estructura de costos.")
        acciones.append("Buscar reducción de costos variables antes de aumentar volumen.")
    if resultados["punto_equilibrio"] > datos["cantidad"]:
        acciones.append("Aumentar ventas o mejorar margen para alcanzar el equilibrio.")
    if resultados["margen"] < 0.1:
        acciones.append("Trabajar en mejorar el margen subiendo precio o reduciendo costos.")
    if resultados["utilidad"] > 0 and resultados["margen"] >= 0.2:
        acciones.append("Evaluar crecimiento o impulso comercial sobre esta línea.")
    if not acciones:
        acciones.append("Mantener seguimiento continuo para confirmar que el resultado se sostenga en el tiempo.")

    return acciones


def construir_reporte_texto(modo, nombre_producto, datos, resultados, estado, descripcion, recomendacion, mensajes):
    acciones = construir_acciones(resultados, datos)
    nombre = nombre_producto if nombre_producto else "Negocio completo"

    lineas = [
        "REPORTE EJECUTIVO - VALORA",
        "========================================",
        f"Tipo de análisis: {modo}",
        f"Elemento analizado: {nombre}",
        "",
        "RESUMEN GENERAL",
        "----------------------------------------",
        f"Estado: {estado}",
        f"Descripción: {descripcion}",
        f"Utilidad: {round(resultados['utilidad'], 2)}",
        f"Margen: {round(resultados['margen'] * 100, 2)}%",
        f"Punto de equilibrio: {round(resultados['punto_equilibrio'], 2)}",
        "",
        "ESTRUCTURA ECONÓMICA",
        "----------------------------------------",
        f"Ingresos: {round(resultados['ingresos'], 2)}",
        f"Costos fijos: {round(datos['costos_fijos'], 2)}",
        f"Costos variables totales: {round(resultados['costos_variables_totales'], 2)}",
        f"Costos totales: {round(resultados['costos_totales'], 2)}",
        "",
        "DIAGNÓSTICO",
        "----------------------------------------",
    ]

    for m in mensajes:
        lineas.append(f"- {m}")

    lineas.extend([
        "",
        "RECOMENDACIÓN PRINCIPAL",
        "----------------------------------------",
        recomendacion,
        "",
        "ACCIONES SUGERIDAS",
        "----------------------------------------",
    ])

    for accion in acciones:
        lineas.append(f"- {accion}")

    lineas.extend([
        "",
        "CIERRE",
        "----------------------------------------",
        "Este reporte resume el análisis actual realizado en VALORA y sirve como apoyo para la toma de decisiones económicas."
    ])

    return "\n".join(lineas)


def generar_pdf_reporte(modo, nombre_producto, datos, resultados, estado, descripcion, recomendacion, mensajes):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    x_margin = 50
    y = height - 50
    usable_width = width - 2 * x_margin

    color_titulo = colors.HexColor("#0f172a")
    color_subtitulo = colors.HexColor("#334155")
    color_linea = colors.HexColor("#cbd5e1")
    color_texto = colors.HexColor("#111827")
    color_estado = colors.HexColor("#065f46") if "Saludable" in estado else (
        colors.HexColor("#92400e") if "riesgo" in estado.lower() else colors.HexColor("#991b1b")
    )

    def nueva_pagina():
        nonlocal y
        pdf.showPage()
        y = height - 50

    def asegurar_espacio(min_y=70):
        nonlocal y
        if y < min_y:
            nueva_pagina()

    def escribir_linea(texto, size=11, bold=False, color=color_texto, espacio=16):
        nonlocal y
        asegurar_espacio()
        fuente = "Helvetica-Bold" if bold else "Helvetica"
        pdf.setFont(fuente, size)
        pdf.setFillColor(color)
        pdf.drawString(x_margin, y, texto)
        y -= espacio

    def escribir_parrafo(texto, size=11, bold=False, color=color_texto, espacio_linea=14, separacion=6):
        nonlocal y
        fuente = "Helvetica-Bold" if bold else "Helvetica"
        lineas = simpleSplit(texto, fuente, size, usable_width)

        for linea in lineas:
            asegurar_espacio()
            pdf.setFont(fuente, size)
            pdf.setFillColor(color)
            pdf.drawString(x_margin, y, linea)
            y -= espacio_linea
        y -= separacion

    def linea_divisora():
        nonlocal y
        asegurar_espacio()
        pdf.setStrokeColor(color_linea)
        pdf.setLineWidth(1)
        pdf.line(x_margin, y, width - x_margin, y)
        y -= 14

    def escribir_seccion(titulo):
        nonlocal y
        y -= 4
        asegurar_espacio()
        pdf.setFont("Helvetica-Bold", 13)
        pdf.setFillColor(color_subtitulo)
        pdf.drawString(x_margin, y, titulo)
        y -= 10
        pdf.setStrokeColor(color_linea)
        pdf.setLineWidth(1)
        pdf.line(x_margin, y, width - x_margin, y)
        y -= 14

    def escribir_bloque_metrica(label, valor):
        escribir_parrafo(f"{label}: {valor}", size=11, bold=False, color=color_texto, espacio_linea=14, separacion=2)

    nombre = nombre_producto if nombre_producto else "Negocio completo"
    acciones = construir_acciones(resultados, datos)

    # Encabezado
    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(color_titulo)
    pdf.drawString(x_margin, y, "REPORTE EJECUTIVO")
    y -= 24

    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(color_subtitulo)
    pdf.drawString(x_margin, y, "VALORA")
    y -= 20

    linea_divisora()

    escribir_linea(f"Tipo de análisis: {modo}", size=11, bold=False)
    escribir_linea(f"Elemento analizado: {nombre}", size=11, bold=False)
    escribir_linea(f"Estado general: {estado}", size=11, bold=True, color=color_estado, espacio=18)
    escribir_parrafo(f"Descripción del estado: {descripcion}", size=11)

    escribir_seccion("Resumen general")
    escribir_bloque_metrica("Utilidad", round(resultados["utilidad"], 2))
    escribir_bloque_metrica("Margen", f"{round(resultados['margen'] * 100, 2)}%")
    escribir_bloque_metrica("Punto de equilibrio", round(resultados["punto_equilibrio"], 2))
    escribir_bloque_metrica("Ingresos", round(resultados["ingresos"], 2))

    escribir_seccion("Estructura económica")
    escribir_bloque_metrica("Costos fijos", round(datos["costos_fijos"], 2))
    escribir_bloque_metrica("Costos variables totales", round(resultados["costos_variables_totales"], 2))
    escribir_bloque_metrica("Costos totales", round(resultados["costos_totales"], 2))

    escribir_seccion("Diagnóstico")
    for m in mensajes:
        escribir_parrafo(f"• {m}", size=11)

    escribir_seccion("Recomendación principal")
    escribir_parrafo(recomendacion, size=11, bold=True, color=color_subtitulo)

    escribir_seccion("Acciones sugeridas")
    for accion in acciones:
        escribir_parrafo(f"• {accion}", size=11)

    escribir_seccion("Cierre")
    escribir_parrafo(
        "Este reporte resume el análisis actual realizado en VALORA y sirve como apoyo para la toma de decisiones económicas.",
        size=10,
        color=colors.HexColor("#475569")
    )

    # Pie de página
    asegurar_espacio(40)
    pdf.setStrokeColor(color_linea)
    pdf.line(x_margin, 35, width - x_margin, 35)
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#64748b"))
    pdf.drawString(x_margin, 22, "Generado por VALORA")

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


if "analisis_guardado" not in st.session_state or not st.session_state.analisis_guardado:
    st.info("Todavía no hay un análisis actual para mostrar en formato de reporte.")
else:
    resultados = st.session_state.resultados_base
    datos = st.session_state.datos_base
    estado = st.session_state.estado_texto
    descripcion = st.session_state.descripcion_estado
    recomendacion = st.session_state.recomendacion_base
    mensajes = st.session_state.mensajes_base
    modo = st.session_state.modo_analisis
    nombre_producto = st.session_state.nombre_producto if st.session_state.nombre_producto else "Negocio completo"

    st.markdown("## Encabezado del reporte")
    st.write(f"**Tipo de análisis:** {modo}")
    st.write(f"**Elemento analizado:** {nombre_producto}")

    st.markdown(
        f'<div class="{clase_estado_css(estado)}">{estado} — {descripcion}</div>',
        unsafe_allow_html=True
    )

    st.markdown("## Resumen ejecutivo")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Utilidad", round(resultados["utilidad"], 2))
    c2.metric("Margen", f"{round(resultados['margen'] * 100, 2)}%")
    c3.metric("Equilibrio", round(resultados["punto_equilibrio"], 2))
    c4.metric("Ingresos", round(resultados["ingresos"], 2))

    st.markdown("## Estructura económica")
    e1, e2, e3 = st.columns(3)
    e1.metric("Costos fijos", round(datos["costos_fijos"], 2))
    e2.metric("Costos variables totales", round(resultados["costos_variables_totales"], 2))
    e3.metric("Costos totales", round(resultados["costos_totales"], 2))

    st.markdown("## Diagnóstico")
    for m in mensajes:
        st.write("•", m)

    st.markdown("## Recomendación principal")
    st.success(recomendacion)

    st.markdown("## Interpretación ejecutiva")

    if resultados["utilidad"] < 0:
        st.write("• La utilidad es negativa, por lo que el escenario actual está destruyendo valor.")
    elif resultados["utilidad"] == 0:
        st.write("• La utilidad es nula, así que la operación está exactamente en equilibrio.")
    else:
        st.write("• La utilidad es positiva, por lo que la operación sí genera ganancia.")

    if resultados["margen"] < 0:
        st.write("• El margen es negativo, lo cual indica una estructura económicamente inviable.")
    elif resultados["margen"] < 0.1:
        st.write("• El margen es bajo, así que la rentabilidad actual sigue siendo frágil.")
    elif resultados["margen"] < 0.2:
        st.write("• El margen es aceptable, pero todavía existe espacio de mejora.")
    else:
        st.write("• El margen es sólido y muestra una estructura más saludable.")

    if resultados["punto_equilibrio"] > datos["cantidad"]:
        st.write("• El nivel actual de ventas todavía no supera el punto de equilibrio.")
    else:
        st.write("• El nivel actual de ventas ya supera el punto de equilibrio.")

    st.markdown("## Acciones sugeridas")
    acciones = construir_acciones(resultados, datos)
    for accion in acciones:
        st.write("•", accion)

    st.markdown("## Cierre")
    st.info(
        "Este reporte resume el análisis actual realizado en VALORA y sirve como apoyo para la toma de decisiones económicas."
    )

    reporte_txt = construir_reporte_texto(
        modo,
        nombre_producto,
        datos,
        resultados,
        estado,
        descripcion,
        recomendacion,
        mensajes
    )

    pdf_bytes = generar_pdf_reporte(
        modo,
        nombre_producto,
        datos,
        resultados,
        estado,
        descripcion,
        recomendacion,
        mensajes
    )

    st.markdown("## Descargas del reporte")

    nombre_base = nombre_producto.replace(" ", "_").lower() if nombre_producto else "negocio"
    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            label="⬇️ Descargar reporte en TXT",
            data=reporte_txt.encode("utf-8"),
            file_name=f"reporte_valora_{nombre_base}.txt",
            mime="text/plain"
        )

    with c2:
        st.download_button(
            label="⬇️ Descargar reporte en PDF",
            data=pdf_bytes,
            file_name=f"reporte_valora_{nombre_base}.pdf",
            mime="application/pdf"
        )
