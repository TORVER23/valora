import streamlit as st
import pandas as pd
import os
from datetime import datetime
from styles import aplicar_estilos

st.set_page_config(page_title="Caja - VALORA", page_icon="💰", layout="centered")
aplicar_estilos()

st.title("Sistema de Caja")
st.caption("Controla ingresos, egresos y el flujo real de dinero de tu negocio")

ARCHIVO = "caja.csv"


# -------------------------
# FUNCIONES
# -------------------------
def normalizar_caja(df: pd.DataFrame) -> pd.DataFrame:
    columnas_base = ["id", "fecha", "tipo", "categoria", "monto", "descripcion"]

    if df.empty:
        return pd.DataFrame(columns=columnas_base)

    # Crear columnas faltantes por compatibilidad con versiones antiguas
    if "fecha" not in df.columns:
        df["fecha"] = datetime.today().strftime("%Y-%m-%d")

    if "tipo" not in df.columns:
        df["tipo"] = "Egreso"

    if "categoria" not in df.columns:
        df["categoria"] = "Otros"

    if "monto" not in df.columns:
        df["monto"] = 0.0

    if "descripcion" not in df.columns:
        df["descripcion"] = ""

    # Si no existe id, crearla
    if "id" not in df.columns:
        df = df.copy().reset_index(drop=True)
        df["id"] = range(1, len(df) + 1)

    # Ordenar columnas
    df = df[["id", "fecha", "tipo", "categoria", "monto", "descripcion"]].copy()

    # Tipos consistentes
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0.0)
    df["descripcion"] = df["descripcion"].fillna("").astype(str)

    # Reparar ids nulos o duplicados
    if df["id"].isna().any() or df["id"].duplicated().any():
        df = df.reset_index(drop=True)
        df["id"] = range(1, len(df) + 1)
    else:
        df["id"] = df["id"].astype(int)

    return df


def cargar_caja():
    if os.path.exists(ARCHIVO):
        df = pd.read_csv(ARCHIVO)
        df = normalizar_caja(df)
        # Guarda la versión normalizada para migrar archivos viejos
        df.to_csv(ARCHIVO, index=False)
        return df

    return pd.DataFrame(columns=["id", "fecha", "tipo", "categoria", "monto", "descripcion"])


def guardar_caja(df):
    df = normalizar_caja(df)
    df.to_csv(ARCHIVO, index=False)


def siguiente_id(df):
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


def agregar_movimiento(tipo, categoria, monto, descripcion, fecha_manual):
    df = cargar_caja()

    nuevo = pd.DataFrame([{
        "id": siguiente_id(df),
        "fecha": fecha_manual.strftime("%Y-%m-%d"),
        "tipo": tipo,
        "categoria": categoria,
        "monto": float(monto),
        "descripcion": descripcion if descripcion else ""
    }])

    df = pd.concat([df, nuevo], ignore_index=True)
    guardar_caja(df)


def eliminar_movimiento(id_movimiento):
    df = cargar_caja()
    df = df[df["id"] != int(id_movimiento)].copy()
    guardar_caja(df)


# -------------------------
# FORMULARIO
# -------------------------
st.markdown("## Registrar movimiento")

with st.form("form_caja"):
    c1, c2 = st.columns(2)

    with c1:
        tipo = st.selectbox("Tipo", ["Ingreso", "Egreso"])
        categoria = st.selectbox(
            "Categoría",
            ["Ventas", "Costos variables", "Costos fijos", "Inversión", "Otros"]
        )

    with c2:
        monto = st.number_input("Monto", min_value=0.0, step=1.0)
        fecha_manual = st.date_input("Fecha del movimiento", value=datetime.today())

    descripcion = st.text_input("Descripción", placeholder="Ej. Compra de insumos")

    submit = st.form_submit_button("Registrar movimiento")

    if submit:
        agregar_movimiento(tipo, categoria, monto, descripcion, fecha_manual)
        st.success("Movimiento registrado correctamente.")
        st.rerun()


# -------------------------
# DATOS
# -------------------------
df = cargar_caja()

if not df.empty:
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    # -------------------------
    # FILTROS
    # -------------------------
    st.markdown("## Filtros")

    f1, f2 = st.columns(2)
    tipos = ["Todos"] + sorted(df["tipo"].dropna().astype(str).unique().tolist())
    categorias = ["Todas"] + sorted(df["categoria"].dropna().astype(str).unique().tolist())

    filtro_tipo = f1.selectbox("Filtrar por tipo", tipos)
    filtro_categoria = f2.selectbox("Filtrar por categoría", categorias)

    df_filtrado = df.copy()

    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo"] == filtro_tipo]

    if filtro_categoria != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == filtro_categoria]

    # -------------------------
    # RESUMEN
    # -------------------------
    ingresos = df_filtrado[df_filtrado["tipo"] == "Ingreso"]["monto"].sum()
    egresos = df_filtrado[df_filtrado["tipo"] == "Egreso"]["monto"].sum()
    saldo = ingresos - egresos

    st.markdown("## Resumen de caja")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", round(ingresos, 2))
    c2.metric("Egresos", round(egresos, 2))
    c3.metric("Saldo", round(saldo, 2))

    # -------------------------
    # HISTORIAL
    # -------------------------
    st.markdown("## Historial de movimientos")
    st.caption("Aquí puedes revisar cada movimiento y eliminar registros individuales si te equivocaste.")

    tabla = df_filtrado.sort_values("fecha", ascending=False).copy()
    tabla["fecha"] = tabla["fecha"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        tabla[["id", "fecha", "tipo", "categoria", "monto", "descripcion"]],
        use_container_width=True
    )

    # -------------------------
    # ELIMINAR UNO POR UNO
    # -------------------------
    st.markdown("## Eliminar un movimiento")

    movimientos_ordenados = df_filtrado.sort_values("fecha", ascending=False).copy()

    movimientos_opciones = [
        (
            int(row["id"]),
            f'ID {int(row["id"])} | {row["fecha"].strftime("%Y-%m-%d")} | {row["tipo"]} | {row["categoria"]} | {round(row["monto"], 2)} | {row["descripcion"]}'
        )
        for _, row in movimientos_ordenados.iterrows()
    ]

    if movimientos_opciones:
        opcion_texto = st.selectbox(
            "Selecciona el movimiento que quieres eliminar",
            options=[texto for _, texto in movimientos_opciones]
        )

        id_seleccionado = next(
            id_mov for id_mov, texto in movimientos_opciones if texto == opcion_texto
        )

        if st.button("🗑️ Eliminar movimiento seleccionado"):
            eliminar_movimiento(id_seleccionado)
            st.success("Movimiento eliminado correctamente.")
            st.rerun()

    # -------------------------
    # FLUJO DE CAJA POR DÍA
    # -------------------------
    st.markdown("## Flujo de caja acumulado")
    st.caption("Este gráfico muestra cómo evoluciona tu saldo en el tiempo por día, no por hora.")

    graf = df_filtrado.copy()
    graf["flujo"] = graf.apply(
        lambda row: row["monto"] if row["tipo"] == "Ingreso" else -row["monto"],
        axis=1
    )

    flujo_diario = (
        graf.groupby(graf["fecha"].dt.date)["flujo"]
        .sum()
        .reset_index()
    )
    flujo_diario["fecha"] = pd.to_datetime(flujo_diario["fecha"])
    flujo_diario = flujo_diario.sort_values("fecha")
    flujo_diario["saldo_acumulado"] = flujo_diario["flujo"].cumsum()

    st.line_chart(flujo_diario.set_index("fecha")["saldo_acumulado"])

    # -------------------------
    # DESCARGA Y LIMPIEZA TOTAL
    # -------------------------
    st.markdown("## Gestión de caja")

    g1, g2 = st.columns(2)

    with g1:
        st.download_button(
            "⬇️ Descargar movimientos",
            df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name="caja_valora_filtrada.csv",
            mime="text/csv"
        )

    with g2:
        if st.button("🧹 Borrar toda la caja"):
            if os.path.exists(ARCHIVO):
                os.remove(ARCHIVO)
            st.success("Se eliminó toda la caja.")
            st.rerun()

else:
    st.info("Aún no hay movimientos registrados en caja.")
