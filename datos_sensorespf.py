import random
import math
import json
from datetime import datetime, timedelta
import os

# Configuración inicial - las mismas que en datospf.py
fecha_inicio_base = datetime(2025, 4, 16, 6, 0)  # 16 de abril de 2025 a las 6:00
fecha_fin_base = datetime(2025, 5, 31, 23, 59)   # 31 de mayo de 2025
num_ciclos = 500  # Aumentado a 500 ciclos
num_equipos = 14
registros_por_archivo = 100  # Número de ciclos por archivo INSERT

# Duración diferente según tipo de equipo
duracion_cocina_horas = 3
duracion_enfriador_horas = 4

# Duración de pre-operativo según tipo de equipo
preop_cocina_minutos = 60     # 1 hora
preop_enfriador_minutos = 90  # 1.5 horas

# IDs de los sensores para cada tipo
SENSORES = {
    'temp_agua': {'id': 1, 'nombre': 'temperatura_agua'},
    'temp_producto': {'id': 3, 'nombre': 'temperatura_producto'},
    'nivel_agua': {'id': 5, 'nombre': 'nivel_agua'}
}

# Crear diccionarios para almacenar los datos generados por sensor
sensores_datos = {
    'temp_agua': [],
    'temp_producto': [],
    'nivel_agua': []
}

# Función para generar todas las fechas de ciclos (500)
def generar_fechas_ciclos():
    fechas_ciclos = {}
    
    # Calcular el intervalo entre ciclos para distribuir uniformemente
    periodo_total = (fecha_fin_base - fecha_inicio_base).total_seconds()
    intervalo_segundos = periodo_total / num_ciclos
    
    for i in range(1, num_ciclos + 1):
        # Determinar duración según tipo de equipo
        id_equipo = ((i - 1) % num_equipos) + 1
        es_enfriador = id_equipo >= 7
        duracion_ciclo = duracion_enfriador_horas if es_enfriador else duracion_cocina_horas
        
        # Calcular fecha de inicio basada en la distribución uniforme
        offset_segundos = (i - 1) * intervalo_segundos
        fecha_inicio_ciclo = fecha_inicio_base + timedelta(seconds=offset_segundos)
        fecha_fin_ciclo = fecha_inicio_ciclo + timedelta(hours=duracion_ciclo)
        
        # Guardar las fechas
        fechas_ciclos[str(i)] = {
            "fecha_inicio": fecha_inicio_ciclo,
            "fecha_fin": fecha_fin_ciclo,
            "es_enfriador": es_enfriador
        }
    
    return fechas_ciclos

# Generar directamente las fechas de ciclo sin depender del archivo JSON
fechas_ciclos = generar_fechas_ciclos()
print(f"✅ Fechas generadas para {len(fechas_ciclos)} ciclos")

# Generar datos para cada ciclo
for ciclo_id in range(1, num_ciclos + 1):
    # Obtener las fechas y tipo de equipo para este ciclo
    ciclo_info = fechas_ciclos[str(ciclo_id)]
    es_enfriador = ciclo_info["es_enfriador"]
    ciclo_actual_inicio = ciclo_info["fecha_inicio"]
    
    # Establecer duración del ciclo y preoperativo según el tipo de equipo
    if es_enfriador:
        duracion_ciclo_minutos = duracion_enfriador_horas * 60
        duracion_preop_minutos = preop_enfriador_minutos
    else:
        duracion_ciclo_minutos = duracion_cocina_horas * 60
        duracion_preop_minutos = preop_cocina_minutos
    
    # Variable para mantener el último nivel de agua y evitar cambios bruscos
    ultimo_nivel_agua = random.uniform(1560, 1600)
    
    # Generar datos para cada sensor a intervalos de 2 minutos durante todo el ciclo
    for minuto in range(0, duracion_ciclo_minutos, 2):  # cada 2 minutos
        tiempo_actual = ciclo_actual_inicio + timedelta(minutes=minuto)
        
        # Determinar si estamos en fase pre-operativa u operativa
        es_preoperativo = minuto < duracion_preop_minutos
        
        # 1. Temperatura del Agua
        if es_enfriador:
            # Para enfriadores: el agua comienza a 24°C y baja a 2-5°C
            if es_preoperativo:
                # Curva más suave para preoperativo con algo de ruido
                progreso = minuto / duracion_preop_minutos
                # Función sigmoide para una curva más natural
                factor = 1 / (1 + math.exp(-12 * (progreso - 0.5)))
                temp_agua = 24 - (factor * (24 - 2)) + random.uniform(-0.5, 0.5)
            else:
                # Fase operativa del enfriador
                minuto_operativo = minuto - duracion_preop_minutos
                
                if minuto_operativo < 5:
                    # En los primeros 5 minutos, aumentar 10 grados
                    temp_agua = 2 + (10 * minuto_operativo / 5) + random.uniform(-0.3, 0.3)
                elif minuto_operativo < 20:
                    # En los siguientes 15 minutos, volver a temperatura normal
                    temp_agua = 12 - ((12 - 2) * (minuto_operativo - 5) / 15) + random.uniform(-0.3, 0.3)
                else:
                    # Resto del tiempo operativo
                    temp_agua = random.uniform(1, 3)
        else:
            # Para cocinas: el agua se calienta de 24°C a 85-90°C
            if es_preoperativo:
                # Curva más suave para preoperativo con algo de ruido
                progreso = minuto / duracion_preop_minutos
                # Función sigmoide para una curva más natural
                factor = 1 / (1 + math.exp(-12 * (progreso - 0.5)))
                temp_agua = 24 + (factor * (85 - 24)) + random.uniform(-0.5, 0.5)
            else:
                # Fase operativa de la cocina
                minuto_operativo = minuto - duracion_preop_minutos
                
                if minuto_operativo < 5:
                    # En los primeros 5 minutos, bajar 10 grados
                    temp_agua = 85 - (10 * minuto_operativo / 5) + random.uniform(-0.3, 0.3)
                elif minuto_operativo < 20:
                    # En los siguientes 15 minutos, volver a temperatura normal
                    temp_agua = 75 + ((85 - 75) * (minuto_operativo - 5) / 15) + random.uniform(-0.3, 0.3)
                else:
                    # Resto del tiempo operativo
                    base_temp = 85 + ((90 - 85) / (duracion_ciclo_minutos - duracion_preop_minutos - 20)) * (minuto_operativo - 20)
                    temp_agua = base_temp + random.uniform(-0.7, 0.7)
        
        temp_agua_valor = round(temp_agua, 2)
        sensores_datos['temp_agua'].append({
            'id_sensor': SENSORES['temp_agua']['id'],
            'valor': temp_agua_valor,
            'id_ciclo': ciclo_id,
            'fecha_registro': tiempo_actual
        })
        
        # 2. Temperatura del Producto - solo en fase operativa, NO agregamos registros en preoperativo
        if not es_preoperativo:  # Solo agregamos registros cuando estamos en la fase operativa
            # Calculamos la temperatura con curvas mejoradas
            minuto_operativo = minuto - duracion_preop_minutos
            duracion_operativo = duracion_ciclo_minutos - duracion_preop_minutos
            
            if es_enfriador:
                # Para enfriadores: el producto comienza a 75°C y baja a 5°C (enfriamiento)
                k = 0.025  # Factor más agresivo para llegar al punto objetivo
                tiempo_normalizado = minuto_operativo / duracion_operativo
                # Curva exponencial modificada para asegurar llegar a 5°
                temp_producto = 5 + (70 * math.exp(-4 * tiempo_normalizado))
                # Añadimos fluctuaciones menores
                temp_producto = max(5, temp_producto + random.uniform(-0.5, 0.5))
            else:
                # Para cocinas: el producto comienza a 5°C y aumenta a 75°C (calentamiento)
                # Usamos la misma función logística que el servidor OPC
                L = 70  # Rango de temperatura (75 - 5 = 70)
                k = 0.09  # Factor de velocidad de calentamiento
                
                # Ajustamos x0 para que se adapte a la duración del ciclo operativo
                x0_adjusted = duracion_operativo / 4  # Punto de inflexión a 1/4 del tiempo operativo
                
                temp_producto = 5 + L / (1 + math.exp(-k * (minuto_operativo - x0_adjusted)))
                # Añadimos variabilidad similar al servidor OPC
                temp_producto = min(75, temp_producto + random.uniform(-0.7, 0.7))
                
            temp_producto_valor = round(temp_producto, 2)
            sensores_datos['temp_producto'].append({
                'id_sensor': SENSORES['temp_producto']['id'],
                'valor': temp_producto_valor,
                'id_ciclo': ciclo_id,
                'fecha_registro': tiempo_actual
            })
        
        # 3. Nivel de Agua - con oscilaciones suaves (max 10mm cambio)
        if es_preoperativo:
            if minuto < 5:
                nivel_agua = random.uniform(1560, 1580)
            else:
                # Incremento gradual durante preoperativo
                nivel_base = 1580 + ((1650 - 1580) * minuto / duracion_preop_minutos)
                nivel_agua = nivel_base + random.uniform(-5, 5)
        elif minuto < duracion_preop_minutos + 10:  # Inicio operativo
            nivel_base = 1650 + ((1950 - 1650) / 10) * (minuto - duracion_preop_minutos)
            nivel_agua = nivel_base + random.uniform(-5, 5)
        elif minuto >= duracion_ciclo_minutos - 10:  # Finalización
            nivel_base = max(1800, 1950 - 15 * (minuto - (duracion_ciclo_minutos - 10)))
            nivel_agua = nivel_base + random.uniform(-5, 5)
        else:  # Operativo normal con oscilaciones suaves
            # Cambio aleatorio limitado a ±10mm respecto al valor anterior
            cambio = random.uniform(-10, 10)
            nivel_agua = ultimo_nivel_agua + cambio
            nivel_agua = max(1900, min(2000, nivel_agua))  # Mantener en rango
        
        ultimo_nivel_agua = nivel_agua  # Guardar para el siguiente ciclo
        nivel_agua_valor = round(nivel_agua, 2)
        
        sensores_datos['nivel_agua'].append({
            'id_sensor': SENSORES['nivel_agua']['id'],
            'valor': nivel_agua_valor,
            'id_ciclo': ciclo_id,
            'fecha_registro': tiempo_actual
        })

print(f"✅ Datos generados, creando archivos SQL...")

# Generar archivos SQL para cada sensor con inserts divididos en bloques de 100 ciclos
for sensor_key, datos in sensores_datos.items():
    # Agrupar datos por ciclos para garantizar que no se cortan los datos de un ciclo
    datos_por_ciclo = {}
    for registro in datos:
        ciclo_id = registro['id_ciclo']
        if ciclo_id not in datos_por_ciclo:
            datos_por_ciclo[ciclo_id] = []
        datos_por_ciclo[ciclo_id].append(registro)
    
    # Crear archivos SQL con bloques de registros
    ciclos_totales = len(datos_por_ciclo)
    num_archivos = (ciclos_totales + registros_por_archivo - 1) // registros_por_archivo  # Redondear hacia arriba
    
    for archivo_num in range(num_archivos):
        inicio_ciclo = archivo_num * registros_por_archivo + 1
        fin_ciclo = min((archivo_num + 1) * registros_por_archivo, ciclos_totales)
        
        # Recopilamos todos los registros de los ciclos seleccionados
        registros_bloque = []
        for ciclo_id in range(inicio_ciclo, fin_ciclo + 1):
            if ciclo_id in datos_por_ciclo:
                registros_bloque.extend(datos_por_ciclo[ciclo_id])
        
        # Nombre del archivo con número de parte
        nombre_archivo = f"sensor_{SENSORES[sensor_key]['nombre']}_part{archivo_num+1}_insert.sql"
        
        with open(nombre_archivo, 'w') as file:
            # Añadir USE statement al inicio
            
            # Crear INSERT múltiple para mejor rendimiento
            file.write(f"INSERT INTO sensoresaa (idSensor, valor, idCiclo, fechaRegistro) VALUES\n")
            
            total_registros = len(registros_bloque)
            for i, sensor in enumerate(registros_bloque):
                file.write(f"({sensor['id_sensor']}, ")
                file.write(f"{sensor['valor']}, ")
                file.write(f"{sensor['id_ciclo']}, ")
                file.write(f"'{sensor['fecha_registro'].strftime('%Y-%m-%d %H:%M:%S')}')")
                
                # Agregar coma o punto y coma según corresponda
                if i < total_registros - 1:
                    file.write(",\n")
                else:
                    file.write(";\n")
        
        print(f"✅ Generado archivo {nombre_archivo} con {len(registros_bloque)} registros (ciclos {inicio_ciclo}-{fin_ciclo})")

print(f"\n🔄 Resumen:")
print(f"  Ciclos procesados: {num_ciclos}")
print(f"  Equipos: {num_equipos} (Cocinas: 1-6, Enfriadores: 7-14)")
num_archivos = (num_ciclos + registros_por_archivo - 1) // registros_por_archivo
print(f"  Archivos generados: {num_archivos} archivos por tipo de sensor")
print(f"  Periodo: {fecha_inicio_base.strftime('%d/%m/%Y')} a {fecha_fin_base.strftime('%d/%m/%Y')}")