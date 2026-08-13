# ✈️ Flight Data Engineering 2024

## Descripción

Proyecto de Ingeniería de Datos enfocado en el procesamiento y análisis de información de vuelos durante 2024.

El proyecto implementa un pipeline **end-to-end** utilizando Python y AWS, siguiendo una arquitectura **Bronze / Silver / Gold** y buenas prácticas de Data Engineering.

## Arquitectura

El pipeline integrará datos de vuelos y fuentes complementarias, aplicará procesos de extracción, transformación y validación, y almacenará los datos procesados en AWS.

La orquestación del pipeline se realizará utilizando **Apache Airflow**.

### Tecnologías

- Python
- Apache Airflow
- Amazon S3
- AWS Glue
- PySpark
- Amazon Athena
- Git / GitHub

## Capas de datos

### 🥉 Bronze

Datos originales, almacenados sin transformaciones significativas.

### 🥈 Silver

Datos limpiados, tipados y estandarizados.

### 🥇 Gold

Datos enriquecidos y preparados para análisis.

## Objetivo

Construir un pipeline reproducible y automatizado que permita transformar datos de vuelos en datasets confiables para análisis y toma de decisiones.

## Estado del proyecto

🚧 En desarrollo
