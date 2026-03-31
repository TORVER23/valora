import streamlit as st
import matplotlib.pyplot as plt

from utils import (
    cargar_historial,
    aplicar_filtros_historial,
)
from styles import aplicar_estilos

st.set_page_config(page_title="Dashboard - VALORA", page_icon="📊", layout="centered")
aplicar_estilos()

st.title("Dashboard")
st.caption("Visualiza la evolución histórica de utilidad, margen, ingresos y costos")


def lectura_tendencia(historial_filtrado):
    lecturas = []

    if historial_filtrado.empty or len(historial_filtrado) < 2:
        return lecturas

    df = historial_filtrado.sort_values("fecha", ascending=True).copy()

    utilidad_inicial = df["utilidad"].iloc[0]
    utilidad_final = df["utilidad"].iloc[-1]

    margen_inicial = df["margen_pct"].iloc[0]
    margen_final = df["margen_pct"].iloc[-1]

    ingresos_promedio = df["ingresos"].mean()
    costos_promedio = df["costos_totales"].mean()

    if utilidad_final > utilidad_inicial:
        lecturas.append("La utilidad muestra una mejora respecto a los primeros registros analizados.")
    elif utilidad_final < utilidad_inicial:
        lecturas.append("La utilidad final está por debajo del inicio del historial filtrado, lo que sugiere deterioro reciente.")
    else:
        lecturas.append("La utilidad se mantiene estable respecto al inicio del historial filtrado.")

    if margen_final > margen_inicial:
        lecturas.append("El margen ha mejorado con el tiempo, señal de una estructura más eficiente.")
    elif margen_final < margen_inicial:
        lecturas.append("El margen se ha debilitado frente al inicio del período observado.")
    else:
        lecturas.append("El margen se mantiene prácticamente estable.")

    if costos_promedio > ingresos_promedio:
        lecturas.append("En promedio, los costos superan los ingresos. Esto es una señal económica crítica.")
    else:
        lecturas.append("En promedio, los ingresos superan los costos, lo que sostiene la operación.")

    if (df["utilidad"] < 0).sum() >= max(2, len(df) // 2):
        lecturas.append("Una parte importante del historial presenta pérdidas. Conviene revisar si el problema es estructural.")
    else:
        lecturas.append("La mayor parte del historial no está en pérdida, lo que da una base más estable para decidir.")

    return lecturas


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

    historial_filtrado = historial_filtrado.sort_values("fecha", ascending=True)

    if len(historial_filtrado) > 0:
        st.markdown("## Resumen ejecutivo del dashboard")

        utilidad_promedio = historial_filtrado["utilidad"].mean()
        ingresos_promedio = historial_filtrado["ingresos"].mean()
        costos_promedio = historial_filtrado["costos_totales"].mean()
        margen_promedio = historial_filtrado["margen_pct"].mean()

        mejor_utilidad = historial_filtrado["utilidad"].max()
        peor_utilidad = historial_filtrado["utilidad"].min()

        m1, m2, m3 = st.columns(3)
        m4, m5, m6 = st.columns(3)

        m1.metric("Análisis guardados", len(historial_filtrado))
        m2.metric("Utilidad promedio", round(utilidad_promedio, 2))
        m3.metric("Margen promedio", f"{round(margen_promedio, 2)}%")
        m4.metric("Ingresos promedio", round(ingresos_promedio, 2))
        m5.metric("Costos promedio", round(costos_promedio, 2))
        m6.metric("Mejor utilidad", round(mejor_utilidad, 2))

        st.markdown("## Lectura rápida de tendencia")
        lecturas = lectura_tendencia(historial_filtrado)
        for lectura in lecturas:
            st.write("•", lectura)

        st.markdown("## Evolución de la utilidad")
        st.caption("Aquí ves si la ganancia mejora, empeora o se vuelve inestable con el tiempo.")

        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(historial_filtrado["fecha"], historial_filtrado["utilidad"], marker="o")
        ax1.set_title("Utilidad en el tiempo")
        ax1.set_xlabel("Fecha")
        ax1.set_ylabel("Utilidad")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig1)

        st.markdown("## Evolución del margen")
        st.caption("Este gráfico muestra qué porcentaje de tus ingresos se convierte en ganancia.")

        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.plot(historial_filtrado["fecha"], historial_filtrado["margen_pct"], marker="o")
        ax2.set_title("Margen porcentual en el tiempo")
        ax2.set_xlabel("Fecha")
        ax2.set_ylabel("Margen (%)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)

        st.markdown("## Ingresos vs costos totales")
        st.caption("Sirve para ver si la operación está dejando espacio suficiente entre lo que entra y lo que cuesta operar.")

        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.plot(historial_filtrado["fecha"], historial_filtrado["ingresos"], marker="o", label="Ingresos")
        ax3.plot(historial_filtrado["fecha"], historial_filtrado["costos_totales"], marker="o", label="Costos totales")
        ax3.set_title("Ingresos y costos totales en el tiempo")
        ax3.set_xlabel("Fecha")
        ax3.set_ylabel("Monto")
        ax3.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig3)

        st.markdown("## Extremos del período")
        e1, e2 = st.columns(2)
        e1.metric("Mejor utilidad registrada", round(mejor_utilidad, 2))
        e2.metric("Peor utilidad registrada", round(peor_utilidad, 2))

    else:
        st.info("No hay registros que coincidan con los filtros.")
else:
    st.info("Todavía no hay análisis guardados.")
