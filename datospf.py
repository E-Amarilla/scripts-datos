import random
from datetime import datetime, timedelta

# Configuración inicial
fecha_inicio = datetime(2025, 4, 16, 6, 0)  # 16 de abril de 2025 a las 6:00
fecha_fin = datetime(2025, 5, 31, 23, 59)  # 31 de mayo de 2025
num_ciclos = 500
num_equipos = 14
num_recetas = 6

# Calcular el intervalo entre ciclos para distribuir uniformemente
periodo_total = (fecha_fin - fecha_inicio).total_seconds()
intervalo_segundos = periodo_total / num_ciclos

# Duración según tipo de equipo (esto no cambia)
duracion_cocina_horas = 3
duracion_enfriador_horas = 4

# Listas para almacenar los datos generados
ciclos = []

# Generar datos de ciclos distribuidos uniformemente
for i in range(1, num_ciclos + 1):
    lote = f"{i:04d}"  # Formato: 0001, 0002, etc.
    cantidad_torres = random.randint(1, 4)
    peso = round(950 + random.random() * 100, 2)  # Peso entre 950 y 1050
    id_equipo = ((i - 1) % num_equipos) + 1  # Ciclo entre 1 y 14
    
    # Determinar duración según tipo de equipo
    es_enfriador = id_equipo >= 7
    duracion_ciclo = duracion_enfriador_horas if es_enfriador else duracion_cocina_horas
    
    # Calcular fecha de inicio basada en la distribución uniforme
    offset_segundos = (i - 1) * intervalo_segundos
    fecha_inicio_ciclo = fecha_inicio + timedelta(seconds=offset_segundos)
    
    id_receta = random.randint(1, num_recetas)
    fecha_fin_ciclo = fecha_inicio_ciclo + timedelta(hours=duracion_ciclo)
    cantidad_pausas = random.randint(0, 4)
    
    # Ajustar el tiempo transcurrido según el tipo de equipo
    tiempo_transcurrido = f"{duracion_ciclo:02d}:00:00"
    
    ciclos.append({
        'estado_maquina': 'FINALIZADO',
        'cantidad_torres': cantidad_torres,
        'lote': lote,
        'cantidad_pausas': cantidad_pausas,
        'tiempo_transcurrido': tiempo_transcurrido,
        'fecha_inicio': fecha_inicio_ciclo,
        'fecha_fin': fecha_fin_ciclo,
        'peso': peso,
        'id_equipo': id_equipo,
        'id_receta': id_receta
    })

# Generar archivo SQL con formato de INSERT directo
with open("ciclos_insert.sql", "w") as file:
    
    # Crear un INSERT múltiple
    file.write("INSERT INTO ciclo (estadoMaquina, cantidadTorres, lote, cantidadPausas, tiempoTranscurrido, fecha_inicio, fecha_fin, peso, idEquipo, idReceta) VALUES\n")
    
    # Agregar cada ciclo como un valor en la declaración INSERT
    for i, ciclo in enumerate(ciclos):
        file.write(f"('{ciclo['estado_maquina']}', ")
        file.write(f"{ciclo['cantidad_torres']}, ")
        file.write(f"'{ciclo['lote']}', ")
        file.write(f"{ciclo['cantidad_pausas']}, ")
        file.write(f"'{ciclo['tiempo_transcurrido']}', ")
        file.write(f"'{ciclo['fecha_inicio'].strftime('%Y-%m-%d %H:%M:%S')}', ")
        file.write(f"'{ciclo['fecha_fin'].strftime('%Y-%m-%d %H:%M:%S')}', ")
        file.write(f"{ciclo['peso']}, ")
        file.write(f"{ciclo['id_equipo']}, ")
        file.write(f"{ciclo['id_receta']}")
        
        # Agregar coma si no es el último elemento, punto y coma si es el último
        if i < len(ciclos) - 1:
            file.write("),\n")
        else:
            file.write(");\n")

print("✅ Datos generados en 'ciclos_insert.sql'")
print(f"✅ Ciclos distribuidos desde {fecha_inicio.strftime('%Y-%m-%d')} hasta {fecha_fin.strftime('%Y-%m-%d')}")