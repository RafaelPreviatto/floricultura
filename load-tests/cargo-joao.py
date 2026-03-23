import time
import uuid
from locust import HttpUser, task, between

class CargoUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        """Realiza o login uma única vez por usuário virtual"""
        res = self.client.post("/api/auth/login", json={
            "email": "teste-carga@floricultura.com",
            "senha": "teste-carga"
        })
       
        if res.status_code == 200:
            self.token = res.json().get("token")
        else:
            self.token = None
            print(f"FALHA NO LOGIN: {res.status_code}")

    @task
    def fluxo_cargo(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
       
        sufixo = str(uuid.uuid4())[:8]

        payload_cargo = {
            "nomeCargo": f"Cargo-{sufixo}",
            "descricao": "Cargo gerado pelo teste de carga"
        }

    
        with self.client.post("/api/cargos", json=payload_cargo, headers=headers, catch_response=True) as response:
            if response.status_code in [200, 201]:
                try:
              
                    cargo_id = response.json().get("id") or response.json().get("idCargo")
                   
                    if cargo_id:
                  
                        res_get = self.client.get(f"/api/cargos/{cargo_id}", headers=headers, name="/api/cargos/[id]")
                       
                        if res_get.status_code == 200:
                            response.success()
                        else:
                            response.failure(f"GET falhou: Status {res_get.status_code}")
                    else:
                        response.failure(f"ID não encontrado na resposta do POST. JSON: {response.text}")
                except Exception as e:
                    response.failure(f"Erro ao processar resposta: {e}")
            else:
                response.failure(f"POST falhou: Status {response.status_code} - {response.text}")

