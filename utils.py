import pandas as pd
import os
from datetime import datetime


# -------------------------
# ARCHIVOS DE HISTORIAL
# -------------------------
def cargar_historial(archivo="historial.csv"):
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        if not df.empty and "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        if not df.empty and "margen" in df.columns:
            df["margen_pct"] = df["margen"] * 100
        return df
    return pd.DataFrame()


def guardar_historial_df(df, archivo="historial.csv"):
    if df.empty:
        if os.path.exists(archivo):
            os.remove(archivo)
    else:
        df.to_csv(archivo, index=False)


def guardar_analisis_csv(datos, resultados, modo, nombre_producto, archivo="historial.csv"):
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


# -------------------------
# RESÚMENES Y FILTROS
# -------------------------
def aplicar_filtros_historial(historial_df, filtro_tipo="Todos", filtro_producto="Todos"):
    if historial_df.empty:
        return historial_df

    historial_filtrado = historial_df.copy()

    if filtro_tipo != "Todos":
        historial_filtrado = historial_filtrado[
            historial_filtrado["tipo_analisis"].astype(str) == filtro_tipo
        ]

    if filtro_producto != "Todos":
        historial_filtrado = historial_filtrado[
            historial_filtrado["producto"].astype(str) == filtro_producto
        ]

    if "fecha" in historial_filtrado.columns:
        historial_filtrado = historial_filtrado.sort_values("fecha", ascending=False)

    return historial_filtrado


def resumen_productos(historial_df: pd.DataFrame) -> pd.DataFrame:
    df = historial_df.copy()
    if df.empty:
        return pd.DataFrame()

    df = df[df["producto"].astype(str) != "N/A"].copy()
    if df.empty:
        return pd.DataFrame()

    if "margen_pct" not in df.columns and "margen" in df.columns:
        df["margen_pct"] = df["margen"] * 100

    resumen = (
        df.groupby("producto", as_index=False)
        .agg(
            analisis=("producto", "count"),
            utilidad_promedio=("utilidad", "mean"),
            mejor_utilidad=("utilidad", "max"),
            peor_utilidad=("utilidad", "min"),
            margen_promedio=("margen_pct", "mean"),
            ingresos_promedio=("ingresos", "mean"),
            costos_promedio=("costos_totales", "mean"),
        )
    )
    return resumen.sort_values("utilidad_promedio", ascending=False)


# -------------------------
# RECOMENDACIONES
# -------------------------
def generar_recomendaciones_estrategicas(historial_filtrado: pd.DataFrame) -> list[str]:
    recomendaciones = []

    if historial_filtrado.empty:
        return recomendaciones

    df = historial_filtrado.copy()

    if "margen_pct" not in df.columns and "margen" in df.columns:
        df["margen_pct"] = df["margen"] * 100

    utilidad_promedio = df["utilidad"].mean()
    margen_promedio = df["margen_pct"].mean()
    ingresos_promedio = df["ingresos"].mean()
    costos_promedio = df["costos_totales"].mean()

    if utilidad_promedio < 0:
        recomendaciones.append(
            "Tu historial muestra pérdidas promedio. Antes de crecer, conviene corregir precio, costos variables o estructura fija."
        )

    if 0 <= utilidad_promedio < 50:
        recomendaciones.append(
            "La utilidad promedio existe, pero es baja. Tu negocio necesita más holgura para resistir cambios en costos o ventas."
        )

    if margen_promedio < 10:
        recomendaciones.append(
            "Tu margen promedio está en zona de riesgo. Un pequeño aumento de costos podría afectar fuertemente tu rentabilidad."
        )
    elif margen_promedio >= 20:
        recomendaciones.append(
            "Tu margen promedio luce sólido. Hay espacio para pensar en crecimiento o en impulsar los productos más fuertes."
        )

    if costos_promedio > ingresos_promedio:
        recomendaciones.append(
            "Tus costos promedio superan tus ingresos promedio. Debes revisar urgente tu estructura económica."
        )

    if len(df) >= 3 and "fecha" in df.columns:
        ultimos = df.sort_values("fecha", ascending=False).head(3)
        if (ultimos["utilidad"] < 0).all():
            recomendaciones.append(
                "Tus tres análisis más recientes muestran pérdidas. Eso sugiere un problema persistente, no un caso aislado."
            )

    resumen_prod = resumen_productos(df)
    if not resumen_prod.empty:
        mejor = resumen_prod.sort_values("utilidad_promedio", ascending=False).iloc[0]
        peor = resumen_prod.sort_values("utilidad_promedio", ascending=True).iloc[0]

        if mejor["utilidad_promedio"] > 0:
            recomendaciones.append(
                f"Conviene impulsar el producto '{mejor['producto']}', porque es el que deja mejor utilidad promedio."
            )

        if peor["utilidad_promedio"] < 0:
            recomendaciones.append(
                f"El producto '{peor['producto']}' está destruyendo rentabilidad promedio. Necesita ajuste o revisión inmediata."
            )

        mejor_margen = resumen_prod.sort_values("margen_promedio", ascending=False).iloc[0]
        if mejor_margen["margen_promedio"] > 15:
            recomendaciones.append(
                f"'{mejor_margen['producto']}' destaca por su margen promedio. Puede ser una buena línea para priorizar."
            )

    return recomendaciones


# -------------------------
# VISUAL
# -------------------------
def clase_estado_css(estado_texto):
    if "Saludable" in estado_texto:
        return "state-good"
    elif "riesgo" in estado_texto.lower():
        return "state-risk"
    return "state-bad"
