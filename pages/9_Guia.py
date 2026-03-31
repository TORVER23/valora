import streamlit as st
from styles import aplicar_estilos

st.set_page_config(page_title="Guía - VALORA", page_icon="📘", layout="centered")
aplicar_estilos()

st.title("Guía económica de VALORA")
st.caption("Aprende a interpretar correctamente las variables y resultados del análisis")

st.markdown("""
Esta guía está pensada para que el usuario entienda **qué significa cada variable** dentro de VALORA, 
cómo debe ingresarla y cómo afecta el resultado final.

La idea no es solo que llenes campos, sino que entiendas **qué está pasando económicamente** en tu producto o negocio.
""")

st.divider()

# -------------------------
# COSTOS FIJOS
# -------------------------
st.markdown("## 1. Costos fijos")
st.markdown("""
Los **costos fijos** son los gastos que debes pagar aunque vendas poco, mucho o incluso nada en el corto plazo.

### Ejemplos comunes
- alquiler
- sueldos administrativos
- servicios básicos
- licencias
- suscripciones
- marketing fijo mensual

### Idea clave
No cambian directamente con cada unidad vendida.

Si vendes 10 unidades o 100 unidades, estos costos normalmente siguen siendo los mismos durante ese período.

### En VALORA
Cuando usas análisis por producto, no siempre ingresarás el costo fijo total del negocio, sino la **parte que ese producto debe cubrir**.

Por eso hablamos de:
- alquiler asignado al producto
- servicios asignados
- sueldos asignados

### Error común
Creer que todo gasto es variable.  
Muchos usuarios meten alquiler o sueldos como si aumentaran por cada unidad, y eso distorsiona completamente el análisis.
""")

st.info("""
Piensa así: los costos fijos son la base económica que tu producto o negocio tiene que sostener aunque no venda mucho.
""")

st.divider()

# -------------------------
# COSTOS VARIABLES
# -------------------------
st.markdown("## 2. Costos variables")
st.markdown("""
Los **costos variables** son los gastos que sí cambian directamente con la cantidad producida o vendida.

### Ejemplos comunes
- materia prima
- empaque
- transporte por unidad
- comisión por venta
- mano de obra variable
- otros insumos por unidad

### Idea clave
Cada unidad adicional vendida genera más de estos costos.

Si vendes más, suben.  
Si vendes menos, bajan.

### En VALORA
En producto individual, VALORA te pide el **costo variable por unidad**.

Eso significa:
- cuánto te cuesta producir o vender **una unidad más**

### Error común
Meter costos variables totales en vez de variables por unidad.

Por ejemplo:
si gastaste 100 en materia prima total para 20 unidades,
eso no significa que el costo variable por unidad sea 100,
sino 5 por unidad.
""")

st.info("""
Piensa así: el costo variable es el costo que aparece cada vez que produces o vendes una unidad adicional.
""")

st.divider()

# -------------------------
# INGRESOS
# -------------------------
st.markdown("## 3. Ingresos")
st.markdown("""
Los **ingresos** son el dinero total que entra por ventas.

### Fórmula básica
**Ingresos = precio × cantidad vendida**

### Ejemplo
Si vendes:
- 100 unidades
- a 20 cada una

Entonces tus ingresos son:
- 2.000

### En VALORA
Esta variable es clave porque es el punto de partida del análisis.

Todo lo demás responde a esta pregunta:
**de lo que vendiste, cuánto realmente te quedó?**
""")

st.divider()

# -------------------------
# COSTO VARIABLE TOTAL
# -------------------------
st.markdown("## 4. Costo variable total")
st.markdown("""
El **costo variable total** es la suma de todos los costos variables generados por la cantidad vendida.

### Fórmula básica
**Costo variable total = costo variable por unidad × cantidad**

### Ejemplo
Si tu costo variable por unidad es 8 y vendes 100 unidades:

- costo variable total = 800

### Por qué importa
Porque aunque un costo variable por unidad parezca pequeño, al multiplicarse por muchas unidades puede volverse muy grande.
""")

st.divider()

# -------------------------
# COSTOS TOTALES
# -------------------------
st.markdown("## 5. Costos totales")
st.markdown("""
Los **costos totales** representan todo lo que te costó operar en el período analizado.

### Fórmula básica
**Costos totales = costos fijos + costos variables totales**

### Qué significa
Aquí ya no estamos viendo solo una parte del negocio, sino el gasto completo.

### En VALORA
Este valor es importantísimo porque permite responder:
**¿cuánto me costó realmente generar estas ventas?**
""")

st.divider()

# -------------------------
# UTILIDAD
# -------------------------
st.markdown("## 6. Utilidad")
st.markdown("""
La **utilidad** es lo que queda después de cubrir todos los costos.

### Fórmula básica
**Utilidad = ingresos - costos totales**

### Interpretación
- si es positiva → estás ganando
- si es cero → estás en equilibrio
- si es negativa → estás perdiendo

### Importancia
La utilidad no dice solo si vendiste, sino si el negocio o producto **realmente conviene**.

### Error común
Confundir “vender mucho” con “ganar mucho”.

Puedes vender bastante y aun así perder dinero si:
- el precio es bajo
- los costos variables son altos
- los costos fijos pesan demasiado
""")

st.success("""
En términos simples: la utilidad responde a la pregunta más importante de toda la app:
¿este producto o negocio realmente deja dinero?
""")

st.divider()

# -------------------------
# MARGEN
# -------------------------
st.markdown("## 7. Margen")
st.markdown("""
El **margen** muestra qué porcentaje de tus ingresos se convierte en ganancia.

### Fórmula básica
**Margen = utilidad / ingresos**

### Ejemplo
Si ingresaste 1.000 y tu utilidad fue 200:

- margen = 20%

Eso significa que por cada 100 que vendes, te quedan 20 de ganancia.

### Por qué es tan importante
Porque la utilidad sola no siempre alcanza.

Por ejemplo:
- una utilidad de 100 puede ser buena o mala
- depende del tamaño de tus ingresos

Si ganaste 100 sobre 200 ingresos, es excelente.
Si ganaste 100 sobre 10.000 ingresos, es muy débil.

### En VALORA
El margen ayuda a clasificar el estado del negocio:
- saludable
- en riesgo
- crítico
""")

st.info("""
El margen te ayuda a entender qué tan eficiente es tu estructura, no solo cuánto dinero absoluto ganaste.
""")

st.divider()

# -------------------------
# PUNTO DE EQUILIBRIO
# -------------------------
st.markdown("## 8. Punto de equilibrio")
st.markdown("""
El **punto de equilibrio** es la cantidad mínima que necesitas vender para cubrir todos tus costos.

### Qué significa
En ese punto:
- no ganas
- no pierdes

### Interpretación
- si vendes menos que eso → pierdes
- si vendes más que eso → empiezas a ganar

### Por qué importa
Te ayuda a saber si tu nivel actual de ventas es suficiente.

Un negocio puede parecer activo, pero si todavía no alcanza su punto de equilibrio, sigue siendo económicamente frágil.

### En VALORA
Cuando el punto de equilibrio es mayor que la cantidad vendida actual, eso es una señal de alerta.
""")

st.warning("""
Muchos negocios creen que están bien porque venden, pero si no alcanzan su punto de equilibrio todavía no están sosteniendo bien su estructura.
""")

st.divider()

# -------------------------
# DIFERENCIA ENTRE PRODUCTO Y NEGOCIO
# -------------------------
st.markdown("## 9. Diferencia entre analizar un producto y analizar el negocio completo")
st.markdown("""
### Producto individual
Sirve para evaluar si una línea, artículo o servicio específico conviene.

Aquí quieres responder:
- ¿este producto deja utilidad?
- ¿vale la pena impulsarlo?
- ¿está sosteniendo su parte de costos?

### Negocio completo
Sirve para evaluar la salud económica general de toda la operación.

Aquí quieres responder:
- ¿mi empresa está siendo rentable?
- ¿mi estructura general está sana?
- ¿mis ventas cubren bien mis costos?

### Importancia de no confundirlos
Un producto puede ser rentable y el negocio total no.
También puede pasar lo contrario:
el negocio puede sostenerse, pero algunos productos específicos estar destruyendo margen.
""")

st.divider()

# -------------------------
# ERRORES COMUNES
# -------------------------
st.markdown("## 10. Errores comunes al usar VALORA")
st.markdown("""
### Error 1: mezclar costos fijos con variables
Esto cambia completamente el resultado.

### Error 2: meter costos totales donde la app pide costo por unidad
Especialmente en productos.

### Error 3: pensar que vender más siempre mejora la rentabilidad
Si el margen es malo, vender más puede aumentar el problema.

### Error 4: interpretar utilidad sin mirar margen
La utilidad sola no siempre cuenta toda la historia.

### Error 5: ignorar el punto de equilibrio
Puedes estar operando por debajo del nivel mínimo necesario.
""")

st.divider()

# -------------------------
# CÓMO LEER LOS RESULTADOS
# -------------------------
st.markdown("## 11. Cómo interpretar los resultados en VALORA")
st.markdown("""
Cuando la app te da resultados, intenta leerlos en este orden:

### 1. Estado general
¿Está saludable, en riesgo o crítico?

### 2. Utilidad
¿Está ganando o perdiendo?

### 3. Margen
¿La estructura deja suficiente espacio de ganancia?

### 4. Punto de equilibrio
¿La venta actual ya cubre bien los costos?

### 5. Recomendación
¿Qué te sugiere hacer la app?

### 6. Historial y comparaciones
¿Qué patrones se repiten en el tiempo?
""")

st.divider()

# -------------------------
# CIERRE
# -------------------------
st.markdown("## 12. Idea final")
st.markdown("""
VALORA no solo sirve para calcular números.

Sirve para ayudarte a responder preguntas económicas fundamentales como:

- ¿estoy ganando realmente?
- ¿qué producto conviene impulsar?
- ¿qué parte de mi operación está destruyendo margen?
- ¿cuánto necesito vender para sostenerme?
- ¿mi negocio está sano o solo parece activo?

Mientras mejor entiendas estas variables, mejores decisiones podrás tomar.
""")

st.success("Consejo final: usa esta guía como referencia cada vez que tengas dudas sobre qué dato ingresar o cómo interpretar el análisis.")
