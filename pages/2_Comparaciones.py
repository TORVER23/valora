import streamlit as st

from utils import (
    cargar_historial,
    aplicar_filtros_historial,
    resumen_productos,
)
from styles import aplicar_estilos

st.set_page_config(page_title="Comparaciones - VALORA", page_icon="⚖️", layout="centered")
aplicar_estilos()

st.title("Comparaciones")
st.caption("Compara productos según utilidad, margen y frecuencia de análisis")


def etiqueta_producto(utilidad_promedio, margen_promedio):
    if utilidad_promedio < 0:
        return "🔴 Revisar urgente"
    elif margen_promedio < 10:
        return "🟡 Margen débil"
    else:
        return "🟢 Buen desempeño"


def lectura_comparativa(resumen_prod):
    if resumen_prod.empty:
        return []

    lecturas = []

    mejor = resumen_prod.sort_values("utilidad_promedio", ascending=False).iloc[0]
    peor = resumen_prod.sort_values("utilidad_promedio", ascending=True).iloc[0]
    mejor_margen = resumen_prod.sort_values("margen_promedio", ascending=False).iloc[0]
    mas_analizado = resumen_prod.sort_values("analisis", ascending=False).iloc[0]

    if mejor["utilidad_promedio"] > 0:
        lecturas.append(
            f"'{mejor['producto']}' lidera en utilidad promedio y hoy es la referencia más fuerte dentro de tus productos analizados."
        )

    if peor["utilidad_promedio"] < 0:
        lecturas.append(
            f"'{peor['producto']}' muestra utilidad promedio negativa, así que conviene revisar precio, costos o incluso su permanencia."
        )

    if mejor_margen["margen_promedio"] >= 15:
        lecturas.append(
            f"'{mejor_margen['producto']}' tiene el mejor margen promedio, lo que sugiere una estructura más eficiente."
        )

    if mas_analizado["analisis"] >= 2:
        lecturas.append(
            f"'{mas_analizado['producto']}' es el producto más analizado, así que probablemente ya es una línea importante para tu negocio."
        )

    return lecturas


archivo = "historial.csv"
historial_df = cargar_historial(archivo)

if not historial_df.empty:
    st.markdown("### Filtros")

    tipos = ["Todos"] + sorted(historial_df["tipo_analisis"].dropna().astype(str).unique().tolist())
    filtro_tipo = st.selectbox("Filtrar por tipo de análisis", tipos)

    historial_filtrado = aplicar_filtros_historial(
        historial_df,
        filtro_tipo=filtro_tipo,
        filtro_producto="Todos"
    )

    resumen_prod = resumen_productos(historial_filtrado)

    if not resumen_prod.empty:
        st.markdown("## Resumen ejecutivo comparativo")

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

        st.markdown("## Lectura rápida")
        lecturas = lectura_comparativa(resumen_prod)
        for lectura in lecturas:
            st.write("•", lectura)

        st.markdown("## Productos destacados")

        top1, top2 = st.columns(2)

        with top1:
            st.markdown("### Producto a impulsar")
            st.success(
                f"**{prod_mas_rentable['producto']}**\n\n"
                f"- Utilidad promedio: {round(prod_mas_rentable['utilidad_promedio'], 2)}\n"
                f"- Margen promedio: {round(prod_mas_rentable['margen_promedio'], 2)}%\n"
                f"- Estado: {etiqueta_producto(prod_mas_rentable['utilidad_promedio'], prod_mas_rentable['margen_promedio'])}"
            )

        with top2:
            st.markdown("### Producto a revisar")
            st.warning(
                f"**{prod_mas_riesgoso['producto']}**\n\n"
                f"- Utilidad promedio: {round(prod_mas_riesgoso['utilidad_promedio'], 2)}\n"
                f"- Margen promedio: {round(prod_mas_riesgoso['margen_promedio'], 2)}%\n"
                f"- Estado: {etiqueta_producto(prod_mas_riesgoso['utilidad_promedio'], prod_mas_riesgoso['margen_promedio'])}"
            )

        st.markdown("## Tabla comparativa")

        tabla = resumen_prod.copy()
        tabla["utilidad_promedio"] = tabla["utilidad_promedio"].round(2)
        tabla["mejor_utilidad"] = tabla["mejor_utilidad"].round(2)
        tabla["peor_utilidad"] = tabla["peor_utilidad"].round(2)
        tabla["margen_promedio"] = tabla["margen_promedio"].round(2)
        tabla["ingresos_promedio"] = tabla["ingresos_promedio"].round(2)
        tabla["costos_promedio"] = tabla["costos_promedio"].round(2)

        tabla["estado_producto"] = tabla.apply(
            lambda row: etiqueta_producto(row["utilidad_promedio"], row["margen_promedio"]),
            axis=1
        )

        columnas_finales = [
            "producto",
            "estado_producto",
            "analisis",
            "utilidad_promedio",
            "margen_promedio",
            "ingresos_promedio",
            "costos_promedio",
            "mejor_utilidad",
            "peor_utilidad",
        ]

        st.dataframe(tabla[columnas_finales], use_container_width=True)

    else:
        st.info("No hay suficientes datos de productos para comparar.")
else:
    st.info("Todavía no hay análisis guardados.")
