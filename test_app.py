import sys
import io
from fastapi.testclient import TestClient
from app.main import app

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = TestClient(app)

def run_tests():
    print("--- 1. Testing Index HTML ---")
    r = client.get("/")
    assert r.status_code == 200, f"Index failed: {r.status_code}"
    print("[PASS] Index HTML 200 OK")

    print("\n--- 2. Testing API Status ---")
    r = client.get("/api/status")
    assert r.status_code == 200, f"Status failed: {r.status_code}"
    status_data = r.json()
    print("[PASS] Status:", status_data)

    print("\n--- 3. Testing Grafana Dashboards ---")
    r = client.get("/api/grafana/dashboards")
    assert r.status_code == 200, f"Dashboards failed: {r.status_code}"
    dbs = r.json().get("dashboards", [])
    print(f"[PASS] Grafana Dashboards count: {len(dbs)}")

    print("\n--- 4. Testing Search-and-Draft (Caso: RESA) ---")
    r = client.post("/api/search-and-draft", json={
        "idea": "El sistema de protección RESA se ha activado otra vez. El deterioro de nuestra infraestructura eléctrica no para.",
        "tone": "Divulgativo"
    })
    assert r.status_code == 200, f"Draft failed: {r.status_code}"
    data_resa = r.json()
    print("[PASS] Fact-check verdict:", data_resa["fact_check"]["verdict"])
    print("[PASS] Tweet preparado directo:", data_resa["tweet_text"])
    print("[PASS] Longitud:", data_resa["char_count"], "/ 280")
    print("[PASS] Infografía generada:", data_resa["infographic_url"])

    print("\n--- 5. Testing Search-and-Draft (Caso NO-RESA: Cero memoria residual) ---")
    r = client.post("/api/search-and-draft", json={
        "idea": "Récord histórico de generación solar fotovoltaica en España con precios mínimos.",
        "tone": "Analítico"
    })
    assert r.status_code == 200, f"Draft solar failed: {r.status_code}"
    data_solar = r.json()
    assert "resa" not in data_solar["tweet_text"].lower(), "ERROR: RESA sigue en memoria!"
    print("[PASS] Tweet solar (sin rastro de RESA):", data_solar["tweet_text"])
    print("[PASS] Noticias encontradas:", len(data_solar["news"]))

    print("\n--- 6. Testing Iterative Tweet Refinement Loop ---")
    r = client.post("/api/refine", json={
        "current_text": data_solar["tweet_text"],
        "feedback": "Hazlo más corto y cita a @RedElectricaREE",
        "fact_context": data_solar["fact_check"]["explanation"]
    })
    assert r.status_code == 200
    ref_data = r.json()
    print("[PASS] Tweet refinado:", ref_data["updated_text"])
    print("[PASS] Explicación:", ref_data["explanation"])
    assert "resa" not in ref_data["updated_text"].lower(), "ERROR: RESA en feedback!"

    print("\n--- 7. Testing Infographic Custom Modification Orders ---")
    r = client.post("/api/update-infographic", json={
        "title": "Récord Solar Fotovoltaico",
        "subtitle": "Generación máxima en horas centrales",
        "cards": data_solar["infographic_data"]["cards"],
        "instruction": "Cambia la tarjeta 2 y pon que fueron 18.500 MW de pico"
    })
    assert r.status_code == 200
    info_mod = r.json()
    print("[PASS] Infografía modificada URL:", info_mod["infographic_url"])
    print("[PASS] Tarjeta 2 actualizada:", info_mod["infographic_data"]["cards"][1]["desc"])

    print("\n=======================================================")
    print("ALL APP INTEGRATION TESTS PASSED (SIN MEMORIA RESIDUAL)!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
