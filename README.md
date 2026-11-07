# ✈️ Flight Data Engineering 2024

[![CI](https://github.com/KarenRC11/flight-data-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/KarenRC11/flight-data-engineering/actions/workflows/ci.yml)

## Descripción


Proyecto end-to-end de Ingeniería de Datos para el procesamiento y análisis de más de 7 millones de registros de vuelos de 2024.

Implementa un pipeline ETL con Python basado en arquitectura Medallion (Bronze, Silver y Gold), procesamiento por chunks, validaciones de calidad, enriquecimiento de datos y almacenamiento en Amazon S3.

Integra Snowflake como Data Warehouse para la ingesta y consulta de datos analíticos, incorporando controles de acceso RBAC, Secure Views, monitoreo de errores y automatización con Snowflake Tasks.

Incluye una aplicación de monitoreo con Streamlit y un pipeline de integración continua (CI) mediante GitHub Actions para ejecutar validaciones automatizadas con pytest.

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


                         Flight Data 2024 (CSV)
                                  |
                                  v
                       +---------------------+
                       |       BRONZE        |
                       | Raw Data / Parquet  |
                       | Date Partitioning   |
                       +----------+----------+
                                  |
                                  v
                       +---------------------+
                       |       SILVER        |
                       | Cleaning            |
                       | Data Quality        |
                       | Catalog Enrichment  |
                       +----------+----------+
                                  |
                                  v
                       +---------------------+
                       |        GOLD         |
                       | Airline Performance |
                       | Airport Performance |
                       | Route Performance   |
                       +----------+----------+
                                  |
                                  v
                       +---------------------+
                       |       AWS S3        |
                       |    Parquet Files    |
                       +----------+----------+
                                  |
                                  v
                       +---------------------+
                       |      SNOWFLAKE      |
                       | Storage Integration |
                       | External Stage      |
                       | RAW / STAGING       |
                       | MARTS / AUDIT       |
                       +----------+----------+
                                  |
                   +--------------+--------------+
                   |              |              |
                   v              v              v
              +----------+   +----------+   +----------+
              | Analytics|   | Security |   |Monitoring|
              | SQL Marts|   | RBAC     |   | Query    |
              |          |   | Secure   |   | History  |
              |          |   | Views    |   | Tasks    |
              +----------+   +----------+   +----+-----+
                                                   |
                                                   v
                                             +-----------+
                                             | Streamlit |
                                             +-----------+

       GitHub Actions CI: Python validation + automated pytest tests

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


## ❄️ Snowflake Integration

El proyecto integra los datasets Gold almacenados en Amazon S3 con Snowflake para su consulta, análisis y gobierno de datos.

### Arquitectura de integración

```text
Python ETL Pipeline
        |
        v
Bronze → Silver → Gold
        |
        v
     AWS S3
   (Parquet files)
        |
        v
Snowflake Storage Integration
        |
        v
   External Stage
        |
        v
   RAW Schema
        |
        v
   MARTS Schema
        |
        v
Analytical Queries
```

### Componentes implementados

- **Storage Integration:** conexión segura entre Snowflake y AWS S3 mediante un rol IAM.
- **External Stage:** acceso a los archivos Parquet almacenados en S3.
- **COPY INTO:** carga de métricas Gold a tablas de Snowflake.
- **RAW:** almacenamiento de los datos ingeridos.
- **STAGING:** esquema para transformaciones y preparación de datos.
- **MARTS:** tablas analíticas para consulta.
- **AUDIT:** almacenamiento y monitoreo de errores de ejecución.

### Analytical Mart

Se implementó la tabla `FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL`, utilizando datos reales procesados por el pipeline Python.

Incluye métricas como:

- Vuelos cancelados por aerolínea.
- Vuelos retrasados por aerolínea.
- Porcentaje de cancelaciones.
- Promedio de retraso de llegada.

Los scripts SQL se encuentran en el directorio `snowflake/sql/`.


## 🔐 Data Governance & Security

Se implementaron controles de acceso y protección de datos en Snowflake utilizando Role-Based Access Control (RBAC) y Secure Views.

### Role-Based Access Control (RBAC)

Se creó el rol `FLIGHT_ANALYST` para proporcionar acceso de solo lectura a los datos analíticos publicados en el esquema MARTS.

Permisos implementados:

- `USAGE` sobre el warehouse `COMPUTE_WH`.
- `USAGE` sobre la base de datos `FLIGHT_DATA_DB`.
- `USAGE` sobre el esquema `MARTS`.
- `SELECT` sobre las tablas analíticas autorizadas.

Se validó el acceso utilizando `USE ROLE FLIGHT_ANALYST` y `USE SECONDARY ROLES NONE`, para comprobar los permisos sin utilizar roles administrativos adicionales.

### Secure Views & Data Protection

Se implementó la vista `MARTS.V_PASSENGERS_SECURE` para demostrar la protección de información personal.

La vista permite consultar información de pasajeros ficticios mostrando los correos electrónicos parcialmente ocultos.

Ejemplo:

`maria@example.com` → `*****@example.com`

Esta implementación utiliza una Secure View con enmascaramiento fijo mediante SQL, no una política dinámica de Data Masking.

### Security Principles

- Principio de mínimo privilegio (*Least Privilege*).
- Separación entre datos de origen (RAW) y datos de consumo (MARTS).
- Acceso controlado mediante roles.
- Protección de información sensible mediante vistas seguras.
- Validación de permisos con roles secundarios desactivados.

Los scripts de seguridad se encuentran en `snowflake/sql/`.


## 📊 Data Monitoring & Automation

Se implementó un mecanismo de monitoreo en Snowflake para identificar, clasificar y analizar errores de ejecución de consultas SQL.

### Query Error Monitoring

Se utiliza `INFORMATION_SCHEMA.QUERY_HISTORY` como fuente de información para identificar consultas que presentan errores.

El proceso permite:

- Consultar el historial de ejecuciones SQL.
- Identificar consultas fallidas.
- Registrar información de errores en el esquema `AUDIT`.
- Actualizar los registros mediante sentencias `MERGE`.
- Clasificar errores para facilitar su análisis y seguimiento.

### Snowflake Tasks

Se creó la tarea `TASK_QUERY_ERRORS` para automatizar la actualización del registro de errores.

Características:

- Frecuencia configurada: cada 60 minutos.
- Ejecución mediante Snowflake Tasks.
- Validación mediante ejecución manual exitosa.
- Tarea actualmente suspendida para controlar el consumo de créditos del entorno de prueba.

### Monitoring Dashboard with Streamlit

Se desarrolló una aplicación de ejemplo utilizando Streamlit en Snowflake para visualizar información relacionada con el monitoreo de consultas.

Esta implementación permite explorar cómo presentar indicadores operativos y registros de errores mediante una interfaz interactiva.

### SQL & Application Files

Los componentes se encuentran documentados en:

- `snowflake/sql/05_audit_monitoring.sql`
- `snowflake/sql/06_tasks.sql`
- `snowflake/streamlit/streamlit_app.py`

---

## 📁 Estructura del proyecto


## 📁 Estructura del proyecto

```text
flight-data-engineering-2024/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── snowflake/
│   ├── README.md
│   └── sql/
│
├── tests/
│
└── README.md
```


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


## 🚀 Continuous Integration (CI) with GitHub Actions

Se implementó un pipeline de integración continua utilizando GitHub Actions para validar automáticamente el código del proyecto.

### CI Workflow

El workflow se encuentra en:

`.github/workflows/ci.yml`

Se ejecuta automáticamente cuando se realizan:

- Pushes a la rama `main`.
- Pull Requests hacia la rama `main`.

### Automated Validation

El pipeline ejecuta los siguientes pasos:

1. Descarga del repositorio mediante `actions/checkout`.
2. Configuración del entorno con Python 3.11.
3. Instalación del proyecto y dependencias de desarrollo.
4. Validación de compilación del código Python.
5. Ejecución de pruebas automatizadas con `pytest`.

### CI Results

La implementación inicial de CI se validó exitosamente:

- **Workflow:** CI
- **Status:** Successful
- **Automated tests:** 2 passed
- **Execution time:** aproximadamente 43 segundos

Las pruebas actuales cubren validaciones iniciales de calidad y transformaciones. Se contempla ampliar su cobertura para incorporar más escenarios del pipeline ETL.

### CI Status

El estado actualizado del workflow puede consultarse mediante el badge de GitHub Actions ubicado al inicio de este README.

Esta implementación permite detectar errores de forma temprana y validar automáticamente los cambios antes de continuar con nuevas funcionalidades.

---

## 🔍 Lint / Validación

Para validar que el código Python pueda compilarse:

```bash
make lint
```

---

## 🛠️ Tecnologías


| Categoría | Tecnología | Implementación |
|---|---|---|
| Programming | Python, Pandas | Procesamiento ETL y transformaciones |
| Data Formats | PyArrow, Parquet | Almacenamiento columnar |
| Data Architecture | Medallion Architecture | Capas Bronze, Silver y Gold |
| Cloud Storage | AWS S3, Boto3 | Almacenamiento de datasets Gold |
| Data Warehouse | Snowflake | Ingesta y consultas analíticas |
| SQL | Snowflake SQL | Transformaciones, MERGE y consultas |
| Data Governance | Snowflake RBAC | Roles y permisos de acceso |
| Data Security | Secure Views | Protección de información |
| Monitoring | Snowflake Query History | Auditoría y clasificación de errores |
| Automation | Snowflake Tasks | Automatización programada de consultas |
| Visualization | Streamlit | Aplicación de monitoreo |
| Continuous Integration | GitHub Actions | Validación automática del código |
| Testing | Pytest | Pruebas automatizadas |
| Version Control | Git, GitHub | Gestión de versiones |
| Development | WSL, Ubuntu, Make | Entorno de desarrollo y comandos |

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

## 🔁 Reproducción del proyecto

El proyecto puede ser reproducido a partir del repositorio de GitHub y de los datasets públicos utilizados como fuentes de datos.

Los archivos de datos no se incluyen en el repositorio debido a su tamaño. Deben descargarse previamente y colocarse en las rutas indicadas.

### 1. Clonar el repositorio

```bash
git clone https://github.com/KarenRC11/flight-data-engineering.git
cd flight-data-engineering
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

También puede utilizarse:

```bash
make install
```

### 4. Descargar los datasets

El pipeline utiliza dos fuentes públicas de datos disponibles en Kaggle.

#### 4.1 Flight Data 2024

Dataset principal utilizado para el procesamiento de vuelos:

[Flight Data 2024 — Kaggle](https://www.kaggle.com/datasets/hrishitpatil/flight-data-2024?utm_source=chatgpt.com)

Descargar el archivo correspondiente al dataset y colocarlo en:

```text
data/raw/flight_data_2024.csv
```

#### 4.2 Global Air Transportation Network

Los catálogos utilizados para el enriquecimiento de los vuelos provienen del siguiente dataset:

[Global Air Transportation Network — Kaggle](https://www.kaggle.com/datasets/thedevastator/global-air-transportation-network-mapping-the-wo?utm_source=chatgpt.com)

Los archivos requeridos son:

```text
airlines.csv
airplanes.csv
airports.csv
routes.csv
```

Deben colocarse en:

```text
data/raw/catalogs/
├── airlines.csv
├── airplanes.csv
├── airports.csv
└── routes.csv
```

La estructura final esperada de los datos de entrada es:

```text
data/
└── raw/
    ├── flight_data_2024.csv
    └── catalogs/
        ├── airlines.csv
        ├── airplanes.csv
        ├── airports.csv
        └── routes.csv
```

> Los datasets no se incluyen directamente en el repositorio debido a su tamaño y para mantener separados el código fuente y los datos de entrada.

### 5. Configurar variables de entorno

Copiar la plantilla de configuración:

```bash
cp .env.example .env
```

Configurar las variables correspondientes al entorno de ejecución.

Ejemplo:

```env
PROJECT_ENV=dev
INPUT_FILE_PATH=./data/raw/flight_data_2024.csv
OUTPUT_DIR=./data
CLOUD_PROVIDER=aws
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
S3_PREFIX=flight-data-engineering
```

Para ejecutar el procesamiento local no es necesario utilizar un bucket propio de S3.

Para publicar los resultados Gold en Amazon S3 se requiere:

* Una cuenta de AWS.
* AWS CLI configurado.
* Credenciales válidas.
* Permisos de escritura sobre el bucket configurado.
* Un bucket existente.

> Nunca subir credenciales, Access Keys, Secrets o archivos `.env` al repositorio.

### 6. Ejecutar las pruebas

Antes de ejecutar el pipeline:

```bash
make test
```

El proyecto utiliza `pytest` para validar las transformaciones y reglas de calidad.

### 7. Validar el código

Ejecutar:

```bash
make lint
```

Esto valida que los módulos Python puedan compilarse correctamente.

### 8. Ejecutar el pipeline

Ejecutar el pipeline completo mediante:

```bash
make run
```

El flujo ejecuta:

```text
Flight Data 2024
      ↓
    Extract
      ↓
    Bronze
      ↓
   Profiling
      ↓
Silver - Flights
      ↓
Silver - Catalogs
      ↓
  Enrichment
      ↓
     Gold
      ↓
 Amazon S3
```

El pipeline genera tres datasets analíticos Gold:

```text
data/gold/
├── airline_performance/
│   └── airline_performance.parquet
├── airport_performance/
│   └── airport_performance.parquet
└── route_performance/
    └── route_performance.parquet
```

Cuando AWS está configurado correctamente, los datasets Gold se publican en Amazon S3.

### 9. Resultados esperados

Con los datasets utilizados durante el desarrollo, el pipeline produjo:

* **7,079,081 registros** de vuelos.
* **366 particiones diarias** en Bronze.
* **7,079,081 registros** procesados en Silver.
* **436 chunks** durante el enriquecimiento.
* **348 aeropuertos** analizados.
* **6,805 rutas** analizadas.
* **3 datasets Gold**.
* **0 archivos con errores de Data Quality**.
* Tests exitosos.
* Validación de compilación exitosa.

Los resultados pueden variar si las versiones de los datasets de Kaggle cambian.

### 10. Estructura de datos generada

Después de ejecutar el pipeline, se generan las siguientes capas:

```text
data/
├── raw/
│   ├── flight_data_2024.csv
│   └── catalogs/
│       ├── airlines.csv
│       ├── airplanes.csv
│       ├── airports.csv
│       └── routes.csv
│
├── bronze/
│   ├── flights/
│   ├── airlines/
│   ├── airplanes/
│   ├── airports/
│   └── routes/
│
├── silver/
│   ├── flights/
│   ├── flights_enriched/
│   ├── airlines/
│   ├── airplanes/
│   ├── airports/
│   └── routes/
│
└── gold/
    ├── airline_performance/
    ├── airport_performance/
    └── route_performance/
```

### 11. Reproducción mínima

Para reproducir el proyecto desde cero:

```bash
git clone https://github.com/KarenRC11/flight-data-engineering.git
cd flight-data-engineering

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

# Descargar y colocar los datasets en data/raw/

make test
make lint
make run
```

Con esto se puede reproducir el pipeline completo a partir del código versionado y de las fuentes de datos públicas.


## 🚧 Roadmap & Future Improvements

### ✅ Implementaciones completadas

- [x] Pipeline ETL con Python.
- [x] Arquitectura Medallion: Bronze, Silver y Gold.
- [x] Procesamiento de más de 7 millones de registros.
- [x] Validaciones de calidad de datos.
- [x] Publicación de datasets Gold en Amazon S3.
- [x] Integración de AWS S3 con Snowflake.
- [x] Creación de tablas analíticas en Snowflake.
- [x] Implementación de RBAC y Secure Views.
- [x] Auditoría y clasificación de errores SQL.
- [x] Configuración y prueba de Snowflake Tasks.
- [x] Aplicación de ejemplo con Streamlit.
- [x] Integración continua con GitHub Actions.
- [x] Ejecución automática de pruebas con pytest.

### 🔜 Próximas mejoras

- [ ] Ampliar la cobertura de pruebas automatizadas.
- [ ] Implementar orquestación del ETL con Apache Airflow.
- [ ] Explorar procesamiento distribuido con PySpark / AWS Glue.
- [ ] Incorporar AWS Glue Data Catalog.
- [ ] Implementar consultas analíticas con Amazon Athena.
- [ ] Desarrollar un dashboard de análisis de vuelos.
- [ ] Incorporar validaciones de calidad en Snowflake.
- [ ] Explorar despliegue automatizado (CD).


## 👩‍💻 Autor

**Karen Reglero**

Data Engineering Project — 2024 Flight Data

---

⭐ Proyecto desarrollado como práctica de Ingeniería de Datos, procesamiento de grandes volúmenes y arquitectura de datos en AWS.
