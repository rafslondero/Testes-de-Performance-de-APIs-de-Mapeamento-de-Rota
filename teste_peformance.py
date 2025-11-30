import requests
import time
import csv
from datetime import datetime
import openrouteservice

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImUzNTMyODI0MDAxZjQ0MDhhYjQxOGQ3ZmI3ODQ2OTgwIiwiaCI6Im11cm11cjY0In0="
GEOAPIFY_KEY = "14a1c3e4d620410094f2d8d97b3d132b"
GRAPHOPPER_API_KEY = "a2d818dd-7271-44f7-8646-27e9c4cfc986"

ors_client = openrouteservice.Client(key=ORS_API_KEY)

rotas = [
    ((-54.4912, -27.8685), (-54.4725, -27.8679)),  # Dentro de Santa Rosa
    ((-54.3130, -27.6250), (-54.2970, -27.6285)),  # Dentro de Horizontina
    ((-54.4818, -27.8706), (-54.3061, -27.6265)),  # Entre as cidades
    ((-54.4600, -27.8600), (-54.3100, -27.6300)),  # Outro ponto entre as cidades
    ((-54.4750, -27.8800), (-54.3070, -27.6270)),  # Outra ligação Santa Rosa → Horizontina
]

INTERVALO = 600  #10min
DURACAO_TOTAL = 60 * 60  #1hr
NUM_EXECUCOES = DURACAO_TOTAL // INTERVALO

with open("resultado_rotas_apis.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "api", "rota_id", "status_code", "tempo_resposta_s"])

    for execucao in range(int(NUM_EXECUCOES)):
        print(f"Execução {execucao + 1}/{int(NUM_EXECUCOES)} - {datetime.now().isoformat()}")

        for idx, (origem, destino) in enumerate(rotas):
            try:
                inicio = time.time()
                openrouteservice.Client(key=ORS_API_KEY).directions(
                    coordinates=[origem, destino],
                    profile='driving-car',
                    format='geojson',
                    validate=True
                )
                duracao = round(time.time() - inicio, 3)
                writer.writerow([datetime.now().isoformat(), "OpenRouteService", idx + 1, 200, duracao])
            except:
                writer.writerow([datetime.now().isoformat(), "OpenRouteService", idx + 1, "erro", None])

            try:
                geo_url = (
                    f"https://api.geoapify.com/v1/routing?"
                    f"waypoints={origem[1]},{origem[0]}|{destino[1]},{destino[0]}"
                    f"&mode=drive&apiKey={GEOAPIFY_KEY}"
                )
                inicio = time.time()
                r = requests.get(geo_url, timeout=10)
                duracao = round(time.time() - inicio, 3)
                writer.writerow([datetime.now().isoformat(), "Geoapify", idx + 1, r.status_code, duracao])
            except:
                writer.writerow([datetime.now().isoformat(), "Geoapify", idx + 1, "erro", None])

            try:
                osrm_url = (
                    f"https://router.project-osrm.org/route/v1/driving/"
                    f"{origem[0]},{origem[1]};{destino[0]},{destino[1]}"
                    f"?overview=false"
                )
                inicio = time.time()
                r = requests.get(osrm_url, timeout=10)
                duracao = round(time.time() - inicio, 3)
                writer.writerow([datetime.now().isoformat(), "OSRM", idx + 1, r.status_code, duracao])
            except:
                writer.writerow([datetime.now().isoformat(), "OSRM", idx + 1, "erro", None])

            try:
                graph_url = (
                    f"https://graphhopper.com/api/1/route?"
                    f"point={origem[1]},{origem[0]}&point={destino[1]},{destino[0]}"
                    f"&profile=car&locale=pt&calc_points=true&key={GRAPHOPPER_API_KEY}&points_encoded=false"
                )
                inicio = time.time()
                r = requests.get(graph_url, timeout=10)
                duracao = round(time.time() - inicio, 3)
                writer.writerow([datetime.now().isoformat(), "GraphHopper", idx + 1, r.status_code, duracao])
            except:
                writer.writerow([datetime.now().isoformat(), "GraphHopper", idx + 1, "erro", None])

        if execucao < NUM_EXECUCOES - 1:
            print(f"Aguardando {INTERVALO // 60} minutos...\n")
            time.sleep(INTERVALO)

print("Finalizado.")