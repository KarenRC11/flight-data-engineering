from pipeline.airport_performance import create_airport_performance
from pipeline.gold import create_airline_performance
from pipeline.route_performance import create_route_performance
from pipeline.bronze import main as create_bronze
from pipeline.profile import main as profile_flights
from pipeline.silver import process_bronze_to_silver
from pipeline.transform.catalogs import transform_catalogs
from pipeline.transform.enrich_flights import enrich_flights


def run():
    print("=" * 70)
    print("FLIGHT DATA ENGINEERING PIPELINE")
    print("=" * 70)

    # 1. Bronze
    print("\n[1/7] BRONZE - Extrayendo vuelos...")
    create_bronze()

    # 2. Profiling
    print("\n[2/7] PROFILE - Analizando datos...")
    profile_flights()

    # 3. Silver - Flights
    print("\n[3/7] SILVER - Transformando vuelos...")
    process_bronze_to_silver()

    # 4. Silver - Catalogs
    print("\n[4/7] SILVER - Transformando catálogos...")
    transform_catalogs()

    # 5. Silver - Enrichment
    print("\n[5/7] SILVER - Enriqueciendo vuelos...")
    enrich_flights()

    # 6. Gold
    print("\n[6/7] GOLD - Airline performance...")
    create_airline_performance()

    print("\n[6/7] GOLD - Airport performance...")
    create_airport_performance()

    print("\n[6/7] GOLD - Route performance...")
    create_route_performance()

    # 7. Final
    print("\n[7/7] PIPELINE COMPLETADO")

    print("=" * 70)
    print("FLIGHT DATA ENGINEERING PIPELINE FINALIZADO")
    print("=" * 70)


if __name__ == "__main__":
    run()
