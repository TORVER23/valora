import streamlit as st

from utils import (
    cargar_historial,
    aplicar_filtros_historial,
    resumen_productos,
)
from styles import aplicar_estilos

st.set_page_config(page_title="Recomendaciones - VALORA", page_icon="🧠", layout="centered")
aplicar_estilos()

st.title("Recomendaciones estratégicas")
st.caption("Interpretación automática a partir del historial")


def clasificar_recomendaciones(historial_filtrado):
    alertas = []
    mejoras = []
    oportunidades = []

    if historial_filtrado.empty:
        return alertas, mejoras, oportunidades

    df = historial_filtrado.copy()
    utilidad_promedio = df["utilidad"].mean()
    margen_promedio = df["margen_pct"].mean()
    ingresos_promedio = df["ingresos"].mean()
    costos_promedio = df["costos_totales"].mean()

    # Alertas urgentes
    if utilidad_promedio < 0:
        alertas.append(
            "Tu utilidad promedio es negativa. Esto indica que, en conjunto, el escenario histórico analizado está destruyendo valor."
        )

    if costos_promedio > ingresos_promedio:
        alertas.append(
            "Tus costos promedio superan tus ingresos promedio. Esta es una señal crítica de desequilibrio económico."
        )

    if len(df) >= 3:
        ultimos = df.sort_values("fecha", ascending=False).head(3)
        if (ultimos["utilidad"] < 0).all():
            alertas.append(
                "Tus tres análisis más recientes presentan pérdidas. Esto sugiere un problema persistente, no un caso aislado."
            )

    if margen_promedio < 0:
        alertas.append(
            "Tu margen promedio es negativo. Estás perdiendo dinero proporcionalmente sobre tus ingresos."
        )

    # Mejoras recomendadas
    if 0 <= utilidad_promedio < 50:
        mejoras.append(
            "La utilidad promedio existe, pero sigue siendo baja. Conviene buscar más holgura financiera antes de crecer."
        )

    if 0 <= margen_promedio < 10:
        mejoras.append(
            "El margen promedio está en zona débil. Un pequeño aumento de costos podría afectar fuertemente la rentabilidad."
        )

    if ingresos_promedio > 0 and costos_promedio > 0 and costos_promedio / ingresos_promedio > 0.8:
        mejoras.append(
            "Tus costos absorben una gran parte de tus ingresos. Sería sano revisar estructura de costos fijos y variables."
        )

    resumen_prod = resumen_productos(df)
    if not resumen_prod.empty:
        peor = resumen_prod.sort_values("utilidad_promedio", ascending=True).iloc[0]
        peor_margen = resumen_prod.sort_values("margen_promedio", ascending=True).iloc[0]

        if peor["utilidad_promedio"] < 0:
            mejoras.append(
                f"El producto '{peor['producto']}' muestra utilidad promedio negativa. Deberías revisar precio, costos o volumen."
            )

        if peor_margen["margen_promedio"] < 10:
            mejoras.append(
                f"El producto '{peor_margen['producto']}' tiene un margen promedio débil. Puede requerir ajuste antes de impulsarlo."
            )

    # Oportunidades de crecimiento
    if margen_promedio >= 20:
        oportunidades.append(
            "Tu margen promedio luce sólido. Esto abre espacio para pensar en crecimiento o expansión controlada."
        )

    if utilidad_promedio > 0:
        oportunidades.append(
            "La utilidad promedio es positiva. Ya existe una base sobre la cual se puede optimizar y escalar."
        )

    if not resumen_prod.empty:
        mejor = resumen_prod.sort_values("utilidad_promedio", ascending=False).iloc[0]
        mejor_margen = resumen_prod.sort_values("margen_promedio", ascending=False).iloc[0]
        mas_analizado = resumen_prod.sort_values("analisis", ascending=False).iloc[0]

        if mejor["utilidad_promedio"] > 0:
            oportunidades.append(
                f"'{mejor['producto']}' es hoy tu producto más fuerte por utilidad promedio. Puede ser una línea estratégica para impulsar."
            )

        if mejor_margen["margen_promedio"] >= 15:
            oportunidades.append(
                f"'{mejor_margen['producto']}' destaca por su margen promedio. Su estructura parece más eficiente que la del resto."
            )

        if mas_analizado["analisis"] >= 3:
            oportunidades.append(
                f"'{mas_analizado['producto']}' es el producto más analizado. Podría ser una línea clave para tomar decisiones más profundas."
            )

    return alertas, mejoras, oportunidades


archivo = "historial.csv"
historial_df = cargar_historial(archivo)

if not historial_df.empty:
    st.markdown("### Filtros")

    tipos = ["Todos"] + sorted(historial_df["tipo_analisis"].dropna().astype(str).unique().tolist())
    productos = ["Todos"] + sorted(historial_df["producto"].dropna().astype(str).unique().tolist())

    c1, c2 = st.columns(2)
    filtro_tipo = c1.selectbox("Filtrar por tipo de análisis", tipos)
    filtro_producto = c2.selectbox("Filtrar por producto", productos)

    historial_filtrado = aplicar_filtros_historial(
        historial_df,
        filtro_tipo=filtro_tipo,
        filtro_producto=filtro_producto
    )

    if not historial_filtrado.empty:
        st.markdown("## Lectura general")
        st.write(
            "Esta página convierte tu historial en señales de decisión. "
            "No solo te dice qué pasó, sino qué conviene atender primero."
        )

        alertas, mejoras, oportunidades = clasificar_recomendaciones(historial_filtrado)

        st.markdown("## Alertas urgentes")
        if alertas:
            for alerta in alertas:
                st.error(alerta)
        else:
            st.success("No se detectan alertas críticas con los filtros actuales.")

        st.markdown("## Mejoras recomendadas")
        if mejoras:
            for mejora in mejoras:
                st.warning(mejora)
        else:
            st.info("No se detectan mejoras urgentes adicionales con los filtros actuales.")

        st.markdown("## Oportunidades de crecimiento")
        if oportunidades:
            for oportunidad in oportunidades:
                st.success(oportunidad)
        else:
            st.info("Todavía no se observan oportunidades claras de crecimiento con estos datos.")

        st.markdown("## Resumen final")
        if alertas:
            st.write(
                "La prioridad debería ser corregir alertas estructurales antes de pensar en crecimiento."
            )
        elif mejoras:
            st.write(
                "La operación no está en zona crítica, pero aún conviene ajustar y fortalecer antes de escalar."
            )
        else:
            st.write(
                "No se observan alertas importantes. Este historial sugiere una base más sana para optimizar o crecer."
            )

    else:
        st.info("No hay registros que coincidan con los filtros seleccionados.")
else:
    st.info("Todavía no hay análisis guardados.")
