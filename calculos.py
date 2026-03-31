def calcular_resultados(precio, cantidad, costo_variable, costos_fijos):
    ingresos = precio * cantidad
    costos_variables_totales = costo_variable * cantidad
    costos_totales = costos_variables_totales + costos_fijos

    utilidad = ingresos - costos_totales
    margen = utilidad / ingresos if ingresos != 0 else 0

    punto_equilibrio = (
        costos_fijos / (precio - costo_variable)
        if (precio - costo_variable) != 0 else 0
    )

    return {
        "ingresos": ingresos,
        "costos_variables_totales": costos_variables_totales,
        "costos_totales": costos_totales,
        "utilidad": utilidad,
        "margen": margen,
        "punto_equilibrio": punto_equilibrio
    }
