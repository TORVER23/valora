def analizar_negocio(resultados):
    mensajes = []

    if resultados["utilidad"] < 0:
        mensajes.append("Estás operando con pérdidas.")
    else:
        mensajes.append("Tu negocio genera utilidad.")

    if resultados["margen"] < 0.1:
        mensajes.append("El margen es bajo, cuidado.")

    if resultados["punto_equilibrio"] > 0:
        mensajes.append("Revisa si tu volumen de ventas alcanza el punto de equilibrio.")

    return mensajes
