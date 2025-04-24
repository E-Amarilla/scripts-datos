import random
from datetime import datetime, timedelta

# Configuración inicial
recetas_nombres = [
    "Cuadrado", "Rectangular 7K", "Mandolina 6K", "Ovalado A",
    "Ovalado B", "Lunch", "Cuadrado Largo", "Queso Puerco"
]
num_torres_por_receta = [13, 19, 4, 30, 30, 4, 2, 7]
tipos_correcciones = ["Fallas", "HN", "ChG", "ChB", "uHN"]
niveles_min = 11
niveles_max = 11
valor_min = 0
valor_max = 0
fecha_base = datetime(2025, 2, 18, 8, 0)

# Generar recetas
recetas = [
    (
        i + 1,  # id
        recetas_nombres[i],  # codigoProducto
        random.randint(0, 0),  # nroGripper
        random.choice(["", "", ""]),  # tipoMolde
        random.randint(0, 0),  # anchoProducto
        random.randint(0, 0),  # altoProducto
        random.randint(0, 0),  # largoProducto
        random.randint(0, 0),  # pesoProducto
        random.randint(0, 0),  # moldesNivel
        random.randint(0, 0),  # altoMolde
        random.randint(0, 0),  # largoMolde
        random.randint(0, 0),  # ajusteAltura
        random.randint(niveles_min, niveles_max),  # cantidadNiveles
        random.randint(0, 0),  # deltaNiveles
        random.randint(0, 0),  # n1Altura
        random.randint(0, 0),  # bastidorAltura
        random.randint(0, 0),  # ajusteN1Altura
        random.randint(0, 0)  # productosMolde
    )
    for i in range(len(recetas_nombres))
]

# Generar torres
torres = []
NTorre = 1
torre_nombres = {
    "Cuadrado": "CU", "Rectangular 7K": "7K", "Mandolina 6K": "6K",
    "Ovalado A": "OVA-0", "Ovalado B": "OVB-0", "Lunch": "LU",
    "Cuadrado Largo": "CUA", "Queso Puerco": "QP"
}

for receta, cantidad in zip(recetas, num_torres_por_receta):
    receta_id, receta_nombre = receta[:2]
    prefijo = torre_nombres[receta_nombre]

    for i in range(1, cantidad + 1):
        id_torre = f"{prefijo}{i:02d}"
        cantidad_niveles = random.randint(niveles_min, niveles_max)
        hBastidor = random.randint(valor_min, valor_max)
        hAjuste = random.randint(valor_min, valor_max)
        hAjusteN1 = random.randint(valor_min, valor_max)
        DisteNivel = random.randint(valor_min, valor_max)

        torres.append((
            NTorre, id_torre, receta_nombre, cantidad_niveles, receta_id, 
            hBastidor, hAjuste, hAjusteN1, DisteNivel, id_torre
        ))
        NTorre += 1

# Generar configuraciones de torres
torre_configuraciones = []
config_id = 1

for NTorre, id_torre, nombreTag, cantidad_niveles, id_recetario, hBastidor, hAjuste, hAjusteN1, DisteNivel, ActualizarTAG in torres:
    for tipo in tipos_correcciones:
        for nivel in range(1, random.randint(niveles_min, niveles_max) + 1):
            valor = random.randint(valor_min, valor_max)
            fecha_registro = fecha_base + timedelta(minutes=5 * config_id)
            torre_configuraciones.append((config_id, fecha_registro, tipo, nivel, valor, NTorre, id_torre))
            config_id += 1

# Generar archivo SQL
with open("insert_recetario.sql", "w") as file:
    # Insert de recetario
    file.write("INSERT INTO recetario (id, codigoProducto, nroGripper, tipoMolde, anchoProducto, altoProducto, largoProducto, pesoProducto, moldesNivel, altoMolde, largoMolde, ajusteAltura, cantidadNiveles, deltaNiveles, n1Altura, bastidorAltura, ajusteN1Altura, productosMolde) VALUES\n")
    file.write(",\n".join([
        f"({r[0]}, '{r[1]}', {r[2]}, '{r[3]}', {r[4]}, {r[5]}, {r[6]}, {r[7]}, {r[8]}, {r[9]}, {r[10]}, {r[11]}, {r[12]}, {r[13]}, {r[14]}, {r[15]}, {r[16]}, {r[17]})"
        for r in recetas
    ]) + ";\n\n")

    # Insert de torres
    file.write("INSERT INTO torre (NTorre, id, nombreTag, cantidadNiveles, id_recetario, hBastidor, hAjuste, hAjusteN1, DisteNivel, ActualizarTAG) VALUES\n")
    file.write(",\n".join([
        f"({t[0]}, '{t[1]}', '{t[2]}', {t[3]}, {t[4]}, {t[5]}, {t[6]}, {t[7]}, {t[8]}, '{t[9]}')"
        for t in torres
    ]) + ";\n\n")

    # Insert de torreconfiguraciones
    file.write("INSERT INTO torreconfiguraciones (id, fecha_registro, tipo, nivel, valor, id_torreNum, id_torre) VALUES\n")
    file.write(",\n".join([
        f"({c[0]}, '{c[1].strftime('%Y-%m-%d %H:%M')}', '{c[2]}', {c[3]}, {c[4]}, {c[5]}, '{c[6]}')"
        for c in torre_configuraciones
    ]) + ";\n")

print("✅ Datos generados en 'insert_recetario.sql'")