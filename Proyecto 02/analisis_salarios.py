from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


ARCHIVO_CSV = "ds_salaries.csv"
CARPETA_SALIDA = Path("resultados")

COLUMNAS_REQUERIDAS = {
    "job_title",
    "salary_in_usd",
    "experience_level",
    "remote_ratio",
}

NIVELES_EXPERIENCIA = {
    "EN": "Junior",
    "MI": "Intermedio",
    "SE": "Senior",
    "EX": "Ejecutivo",
}

MODALIDAD_REMOTA = {
    0: "Presencial",
    50: "Híbrido",
    100: "Remoto",
}


def cargar_datos():
    """Lee y valida el archivo de salarios."""
    archivo = Path(ARCHIVO_CSV)

    if not archivo.exists():
        print(f"No se encontró el archivo: {ARCHIVO_CSV}")
        sys.exit(1)

    datos = pd.read_csv(archivo)

    faltantes = COLUMNAS_REQUERIDAS - set(datos.columns)
    if faltantes:
        print("Faltan columnas:", ", ".join(faltantes))
        sys.exit(1)

    datos["salary_in_usd"] = pd.to_numeric(
        datos["salary_in_usd"],
        errors="coerce"
    )

    datos = datos.dropna(
        subset=["job_title", "salary_in_usd", "experience_level", "remote_ratio"]
    )

    datos["nivel_experiencia"] = datos["experience_level"].map(
        NIVELES_EXPERIENCIA
    )

    datos["modalidad"] = datos["remote_ratio"].map(MODALIDAD_REMOTA)

    return datos


def crear_resumenes(datos):
    """Calcula los resúmenes principales."""
    salario_por_puesto = (
        datos.groupby("job_title")["salary_in_usd"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    salario_por_experiencia = (
        datos.groupby("nivel_experiencia")["salary_in_usd"]
        .mean()
        .reindex(["Junior", "Intermedio", "Senior", "Ejecutivo"])
    )

    salario_por_modalidad = (
        datos.groupby("modalidad")["salary_in_usd"]
        .mean()
        .reindex(["Presencial", "Híbrido", "Remoto"])
    )

    return salario_por_puesto, salario_por_experiencia, salario_por_modalidad


def guardar_resultados(puesto, experiencia, modalidad):
    """Guarda los resúmenes como archivos CSV."""
    CARPETA_SALIDA.mkdir(exist_ok=True)

    puesto.to_csv(CARPETA_SALIDA / "salario_por_puesto.csv")
    experiencia.to_csv(CARPETA_SALIDA / "salario_por_experiencia.csv")
    modalidad.to_csv(CARPETA_SALIDA / "salario_por_modalidad.csv")


def crear_graficos(puesto, experiencia, modalidad):
    """Crea un panel visual de salarios."""
    CARPETA_SALIDA.mkdir(exist_ok=True)

    figura, ejes = plt.subplots(3, 1, figsize=(11, 15))

    puesto.sort_values().plot(kind="barh", ax=ejes[0], color="royalblue")
    ejes[0].set_title("Top 10 puestos por salario promedio")
    ejes[0].set_xlabel("Salario promedio en USD")
    ejes[0].set_ylabel("Puesto")

    experiencia.plot(kind="bar", ax=ejes[1], color="seagreen")
    ejes[1].set_title("Salario promedio por nivel de experiencia")
    ejes[1].set_xlabel("Nivel de experiencia")
    ejes[1].set_ylabel("Salario promedio en USD")
    ejes[1].tick_params(axis="x", rotation=0)

    modalidad.plot(kind="bar", ax=ejes[2], color="darkorange")
    ejes[2].set_title("Salario promedio por modalidad de trabajo")
    ejes[2].set_xlabel("Modalidad")
    ejes[2].set_ylabel("Salario promedio en USD")
    ejes[2].tick_params(axis="x", rotation=0)

    figura.tight_layout()
    figura.savefig(CARPETA_SALIDA / "panel_salarios.png", dpi=150)
    plt.show()


def main():
    datos = cargar_datos()

    puesto, experiencia, modalidad = crear_resumenes(datos)

    print("\n--- TOP PUESTOS POR SALARIO PROMEDIO ---")
    print(puesto.round(2))

    print("\n--- SALARIO POR EXPERIENCIA ---")
    print(experiencia.round(2))

    print("\n--- SALARIO POR MODALIDAD ---")
    print(modalidad.round(2))

    guardar_resultados(puesto, experiencia, modalidad)
    crear_graficos(puesto, experiencia, modalidad)

    print("\nProyecto terminado. Revisa la carpeta 'resultados'.")


if __name__ == "__main__":
    main()