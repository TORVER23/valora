import streamlit as st
import os

from utils import (
    cargar_historial,
    guardar_historial_df,
    aplicar_filtros_historial,
)
from styles import aplicar_estilos

st.set_page_config(page_title="Historial - VALORA", page_icon="📁", layout="centered")
aplicar_estilos()

st.title("Historial")
st.caption("Consulta, filtra, descarga y administra los análisis guardados")


def lectura_historial(historial_filtrado):
    lecturas = []

    if historial_filtrado.empty:
        return lecturas

    ultimo = historial_filtrado.iloc[0]
    utilidad_promedio = historial_filtrado["utilidad"].mean()
    margen_promedio = historial_filtrado["margen_pct"].mean()
    mejor_utilidad = historial_filtrado["utilidad"].max()
    peor_utilidad = historial_filtrado["utilidad"].min()

    lecturas.append(
        f"El último análisis registrado corresponde a '{ultimo['producto']}' con utilidad {round(ultimo['utilidad'], 2)}."
    )

    if utilidad_promedio < 0:
        lecturas.append("La utilidad promedio del historial filtrado es negativa, lo que indica un desempeño débil.")
    else:
        lecturas.append("La utilidad promedio del historial filtrado es positiva, lo que sugiere una base operativa más sana.")

    if margen_promedio < 10:
        lecturas.append("El margen promedio del historial filtrado está en zona de riesgo.")
    else:
        lecturas.append("El margen promedio del historial filtrado no está en zona crítica.")

    lecturas.append(
        f"El mejor resultado registrado fue {round(mejor_utilidad, 2)} y el peor fue {round(peor_utilidad, 2)}."
    )

    return lecturas


archivo_historial = "historial.csv"
historial_df = cargar_historial(archivo_historial)

if not historial_df.empty:
    st.markdown("## Filtros")

    col1, col2 = st.columns(2)

    tipos = ["Todos"] + sorted(historial_df["tipo_analisis"].dropna().astype(str).unique().tolist())
    productos = ["Todos"] + sorted(historial_df["producto"].dropna().astype(str).unique().tolist())

    filtro_tipo = col1.selectbox("Filtrar por tipo de análisis", tipos)
    filtro_producto = col2.selectbox("Filtrar por producto", productos)

    historial_filtrado = aplicar_filtros_historial(
        historial_df,
        filtro_tipo=filtro_tipo,
        filtro_producto=filtro_producto
    )

    st.markdown("## Resumen ejecutivo del historial")

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    c1.metric("Análisis filtrados", len(historial_filtrado))
    c2.metric("Mejor utilidad", round(historial_filtrado["utilidad"].max(), 2))
    c3.metric("Peor utilidad", round(historial_filtrado["utilidad"].min(), 2))
    c4.metric("Margen promedio", f"{round(historial_filtrado['margen_pct'].mean(), 2)}%")
    c5.metric("Ingresos promedio", round(historial_filtrado["ingresos"].mean(), 2))
    c6.metric("Costos promedio", round(historial_filtrado["costos_totales"].mean(), 2))

    st.markdown("## Lectura rápida del historial")
    for lectura in lectura_historial(historial_filtrado):
        st.write("•", lectura)

    st.markdown("## Gestión del historial")

    b1, b2, b3 = st.columns(3)

    if b1.button("🗑️ Borrar todo el historial"):
        if os.path.exists(archivo_historial):
            os.remove(archivo_historial)
        st.success("Se eliminó todo el historial.")
        st.rerun()

    if b2.button("🧹 Borrar solo los datos filtrados"):
        historial_completo = cargar_historial(archivo_historial)

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

        guardar_historial_df(restante, archivo_historial)
        st.success("Se eliminaron los registros filtrados.")
        st.rerun()

    csv_descarga = historial_filtrado.copy()
    csv_descarga["fecha"] = csv_descarga["fecha"].astype(str)
    csv_bytes = csv_descarga.to_csv(index=False).encode("utf-8")

    b3.download_button(
        label="⬇️ Descargar historial filtrado",
        data=csv_bytes,
        file_name="historial_filtrado_valora.csv",
        mime="text/csv"
    )

    st.markdown("## Tabla del historial")
    st.caption(
        "Aquí puedes revisar el detalle completo de los análisis guardados según los filtros aplicados."
    )

    tabla_mostrar = historial_filtrado.copy()
    tabla_mostrar["margen_pct"] = tabla_mostrar["margen_pct"].round(2)

    columnas = [
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
    columnas_visibles = [c for c in columnas if c in tabla_mostrar.columns]
    st.dataframe(tabla_mostrar[columnas_visibles], use_container_width=True)

else:
    st.info("Todavía no hay análisis guardados.")
