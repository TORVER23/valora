def analizar_negocio(resultados):
    mensajes = []

    utilidad = resultados["utilidad"]
    margen = resultados["margen"]
    punto_equilibrio = resultados["punto_equilibrio"]

    if utilidad < 0:
        mensajes.append("⚠️ Estás operando con pérdidas.")
    else:
        mensajes.append("✅ Tu negocio está generando utilidad.")

    if margen < 0.1:
        mensajes.append("📉 Margen muy bajo, revisa costos o precios.")
    elif margen < 0.3:
        mensajes.append("📊 Margen aceptable pero mejorable.")
    else:
        mensajes.append("💰 Excelente margen de ganancia.")

    mensajes.append(
        f"📌 Debes vender aproximadamente {round(punto_equilibrio, 2)} unidades para no perder dinero."
    )

    return mensajes
