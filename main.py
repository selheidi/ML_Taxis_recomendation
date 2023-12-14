import pandas as pd
from fastapi import FastAPI
import uvicorn 
#instanciar la aplicación

app = FastAPI()

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, this is the root endpoint!"}

# Dataframe que se utiliza en las funciones de la API
df = pd.read_csv('demanda_taxi_amarillo_pronostrico4dias_contaminacion_aire_NYC.csv')

@app.get("/recomendacion/{recomendacion}", name='Recomendacion')
async def sugerir_mejor_momento(rango_horario: str, zona_partida: str, zona_destino: str):
    """
    La siguiente función retorna una recomendacion de día y horario de viaje para viajar de forma más ecológica, rápida y con menos contaminación atmosférica

    Parametro: 
    # Ejemplo de uso 
                    (rango_horario=(8, 10),
                       zona_partida='Upper East Side South',
                       zona_destino='Upper East Side North'
                       )    
    Retorna:
    
            {'zona_partida': 'Upper East Side South',
            'zona_destino': 'Upper East Side North',
            'dia_semana': 'Monday',
            'hora_dia': 8,
            'calidad_aire': 'Good',
            'demanda_promedio': 112.0}
    """
    # Procesar rango_horario y convertirlo a una tupla de enteros
    rango_horario = tuple(map(int, rango_horario.split(',')))

    # Filtrar por rango horario y zonas de partida y destino
    filtro_rango_horario = df['hour_of_day'].between(rango_horario[0], rango_horario[1])
    filtro_partida = (df['Partida_Zone'] == zona_partida)
    filtro_destino = (df['Destino_Zone'] == zona_destino)

    # Filtrar por categorías específicas de calidad del aire
    categorias_calidad_aire = ['Very Good', 'Good', 'Moderate']
    filtro_calidad_aire = df['Air_Quality_Index_(aqi)'].isin(categorias_calidad_aire)

    viajes_filtrados = df[filtro_rango_horario & filtro_partida & filtro_destino & filtro_calidad_aire]

    # Agrupar por día de la semana, rango horario y categoría de calidad del aire
    resumen = viajes_filtrados.groupby(['day_of_week', 'hour_of_day', 'Air_Quality_Index_(aqi)']).agg({
        'count': 'mean'
    }).reset_index()

    # Encontrar el momento con la demanda más baja y mejor calidad del aire
    mejor_momento = resumen.loc[resumen['count'].idxmin()]

    return {
        'zona_partida': zona_partida,
        'zona_destino': zona_destino,
        'dia_semana': mejor_momento['day_of_week'],
        'hora_dia': mejor_momento['hour_of_day'],
        'calidad_aire': mejor_momento['Air_Quality_Index_(aqi)'],
        'demanda_promedio': mejor_momento['count']
    }
