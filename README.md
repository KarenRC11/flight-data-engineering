# ✈️ Flight Data Engineering 2024

## Descripción

Proyecto de Ingeniería de Datos para el procesamiento y análisis de información de vuelos durante 2024.

El proyecto implementa un pipeline **end-to-end** utilizando Python y AWS, siguiendo una arquitectura **Bronze / Silver / Gold**, procesamiento por chunks, particionamiento por fecha, validaciones de calidad, enriquecimiento mediante catálogos y almacenamiento de resultados analíticos en Amazon S3.

---

## 🎯 Objetivo

Construir un pipeline de datos reproducible y escalable capaz de transformar un dataset de vuelos de gran tamaño en datasets confiables y preparados para análisis.

El pipeline permite:

* Procesar más de **7 millones de registros**.
* Evitar cargar el dataset completo en memoria.
* Aplicar transformaciones y reglas de calidad.
* Particionar los datos por fecha.
* Enriquecer los vuelos con información de aeropuertos y aerolíneas.
* Generar datasets analíticos Gold.
* Publicar los resultados Gold en Amazon S3.
* Ejecutar pruebas automatizadas.
* Mantener el proyecto versionado mediante Git/GitHub.

---

## 🏗️ Arquitectura

```text
                    ┌─────────────────────┐
                    │  Flight Data 2024   │
                    │       CSV           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       BRONZE        │
                    │                     │
                    │ Raw + Parquet       │
                    │ event_date          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       SILVER        │
                    │                     │
                    │ Cleaning            │
                    │ Standardization     │
                    │ Data Quality         │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │    Catalogs     │   │    Enrichment   │
          │ Airports        │   │ Flights +       │
          │ Airlines        │   │ Airports +      │
          └─────────────────┘   │ Airlines        │
                                └────────┬────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │        GOLD         │
                              │                     │
                              │ Airline Performance │
                              │ Airport Performance │
                              │ Route Performance   │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │      Amazon S3      │
                              │                     │
                              │ flight-data-        │
                              │ engineering/gold/   │
                              └─────────────────────┘
```

---

## 🥉 Bronze

La capa Bronze toma el dataset CSV original y lo procesa utilizando **chunks de 100,000 registros** para evitar cargar todo el archivo en memoria.

Los datos se almacenan en formato **Parquet** y se particionan utilizando:

```text
event_date=YYYY-MM-DD
```

Ejemplo:

```text
data/bronze/flights/
├── event_date=2024-01-01/
├── event_date=2024-01-02/
├── event_date=2024-01-03/
└── ...
```

El dataset procesado contiene aproximadamente:

**7,079,081 registros**

---

## 🥈 Silver

La capa Silver transforma y valida los datos Bronze.

Entre los procesos realizados se encuentran:

* Conversión y estandarización de tipos.
* Transformaciones de columnas.
* Creación de indicadores.
* Validaciones de calidad.
* Procesamiento incremental por archivos.
* Almacenamiento en formato Parquet.

Las validaciones de calidad se ejecutan antes de guardar los datos procesados.

Resultado:

* **7,079,081 registros procesados**
* **0 archivos con errores de calidad**

---

## 🔗 Data Enrichment

Los vuelos son enriquecidos utilizando catálogos de aeropuertos y aerolíneas.

### Aeropuertos

Se incorporan atributos como:

* Nombre del aeropuerto.
* Ciudad.
* País.

### Aerolíneas

Se incorporan atributos como:

* Nombre de la aerolínea.
* País.

El resultado genera una capa de vuelos enriquecidos en:

```text
data/silver/flights_enriched/
```

El proceso generó:

* **436 chunks**
* **7,079,081 registros**

---

## 🥇 Gold

La capa Gold genera datasets agregados orientados al análisis.

### ✈️ Airline Performance

Métricas por aerolínea:

* Total de vuelos.
* Vuelos cancelados.
* Vuelos desviados.
* Vuelos retrasados.
* Promedio de retraso de llegada.
* Tasa de cancelación.
* Tasa de retraso.

Salida:

```text
data/gold/airline_performance/
```

### 🛫 Airport Performance

Métricas por aeropuerto:

* Total de salidas.
* Salidas canceladas.
* Vuelos desviados.
* Llegadas retrasadas.
* Total de llegadas.
* Tasa de retraso.
* Tasa de cancelación.
* Promedio de retraso de llegada.

Salida:

```text
data/gold/airport_performance/
```

El análisis contiene **348 aeropuertos**.

### 🛣️ Route Performance

Métricas por ruta:

* Aeropuerto de origen.
* Aeropuerto de destino.
* Total de vuelos.
* Vuelos cancelados.
* Vuelos desviados.
* Vuelos retrasados.
* Promedio de retraso.
* Distancia promedio.
* Tasa de retraso.
* Tasa de cancelación.

El dataset generado contiene aproximadamente **6,805 rutas**.

Salida:

```text
data/gold/route_performance/
```

---

## ☁️ Amazon S3

Los datasets Gold se publican automáticamente en Amazon S3.

Estructura:

```text
s3://<bucket>/flight-data-engineering/gold/
├── airline_performance/
│   └── airline_performance.parquet
├── airport_performance/
│   └── airport_performance.parquet
└── route_performance/
    └── route_performance.parquet
```

La configuración se realiza mediante variables de entorno:

```env
PROJECT_ENV=dev
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
S3_PREFIX=flight-data-engineering
```

Las credenciales de AWS **no forman parte del repositorio**.

---

## 📁 Estructura del proyecto

```text
flight-data-engineering-2024/
│
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── src/
│   └── pipeline/
│       ├── extract/
│       ├── transform/
│       ├── load/
│       ├── airport_performance.py
│       ├── route_performance.py
│       ├── gold.py
│       ├── bronze.py
│       ├── silver.py
│       ├── profile.py
│       ├── config.py
│       └── main.py
│
├── tests/
├── Makefile
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ Instalación

Clonar el repositorio:

```bash
git clone https://github.com/KarenRC11/flight-data-engineering.git

cd flight-data-engineering
```

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activar el entorno:

### Linux / WSL

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
make install
```

---

## 🔐 Configuración

Crear un archivo `.env` en la raíz del proyecto:

```env
PROJECT_ENV=dev

INPUT_FILE_PATH=./data/raw/flight_data_2024.csv

OUTPUT_DIR=./data

CLOUD_PROVIDER=aws

AWS_REGION=us-east-1

S3_BUCKET=your-bucket-name

S3_PREFIX=flight-data-engineering
```

Las credenciales de AWS deben configurarse mediante AWS CLI o el mecanismo de credenciales correspondiente.

**Nunca subir credenciales, Access Keys o archivos `.env` al repositorio.**

---

## ▶️ Ejecución

El pipeline completo puede ejecutarse mediante:

```bash
make run
```

El flujo ejecuta:

```text
Bronze
   ↓
Profile
   ↓
Silver
   ↓
Catalogs
   ↓
Enrichment
   ↓
Gold
   ↓
Amazon S3
```

Los datasets Gold son publicados automáticamente en S3 al finalizar el pipeline.

---

## 🧪 Testing

Ejecutar las pruebas:

```bash
make test
```

El proyecto utiliza `pytest`.

---

## 🔍 Lint / Validación

Para validar que el código Python pueda compilarse:

```bash
make lint
```

---

## 🛠️ Tecnologías

| Tecnología   | Uso                            |
| ------------ | ------------------------------ |
| Python       | Procesamiento y transformación |
| Pandas       | Manipulación de datos          |
| PyArrow      | Formato Parquet                |
| Boto3        | Integración con AWS S3         |
| Amazon S3    | Almacenamiento cloud           |
| Pytest       | Testing                        |
| Git          | Control de versiones           |
| GitHub       | Repositorio                    |
| Make         | Automatización de comandos     |
| WSL / Ubuntu | Entorno de desarrollo          |

---

## 📊 Resultados actuales

| Capa / proceso         |               Resultado |
| ---------------------- | ----------------------: |
| Dataset de vuelos      |     7,079,081 registros |
| Bronze                 | 366 particiones diarias |
| Silver                 |     7,079,081 registros |
| Enrichment             |              436 chunks |
| Aeropuertos analizados |                     348 |
| Rutas analizadas       |                   6,805 |
| Gold datasets          |                       3 |
| Data Quality           |  0 archivos con errores |
| Tests                  |               ✅ Passing |
| Lint                   |               ✅ Passing |
| S3                     |           ✅ Configurado |

---

## 🚧 Próximas etapas

El proyecto está diseñado para evolucionar hacia una arquitectura cloud más completa.

Próximas mejoras:

* [ ] Automatización del pipeline.
* [ ] Orquestación con Apache Airflow.
* [ ] Procesamiento distribuido con PySpark / AWS Glue.
* [ ] Catálogo de datos mediante AWS Glue Data Catalog.
* [ ] Consultas analíticas mediante Amazon Athena.
* [ ] Automatización CI/CD.
* [ ] Monitoreo y logging.
* [ ] Dashboard de análisis de vuelos.

---

## 👩‍💻 Autor

**Karen**

Data Engineering Project — 2024 Flight Data

---

⭐ Proyecto desarrollado como práctica de Ingeniería de Datos, procesamiento de grandes volúmenes y arquitectura de datos en AWS.
