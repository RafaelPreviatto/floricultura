import time
from locust import HttpUser, task, between


class FornecedorUser(HttpUser):
    wait_time = between(1, 2)


    def on_start(self):
        """Autenticação inicial"""
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
    def fluxo_fornecedor(self):
        if not self.token:
            return


        headers = {"Authorization": f"Bearer {self.token}"}
       
        cnpj_unico = "99" + str(int(time.time() * 1000000))[-12:]


        payload_fornecedor = {
            "nome": f"Fornecedor Teste {cnpj_unico[-4:]} Ltda",
            "cnpj": cnpj_unico,
            "endereco": "Av. Industrial, 500",
            "cep": "86070000",
            "telefone": "43988880000"
        }



        with self.client.post("/api/fornecedores", json=payload_fornecedor, headers=headers, catch_response=True) as response:
            if response.status_code in [200, 201]:
                try:
                   
                    fornecedor_id = response.json().get("id") or response.json().get("idFornecedor")
                   
                    if fornecedor_id:
                    
                        res_get = self.client.get(
                            f"/api/fornecedores/{fornecedor_id}",
                            headers=headers,
                            name="/api/fornecedores/[id]"
                        )
                       
                        if res_get.status_code == 200:
                            response.success()
                        else:
                            response.failure(f"GET falhou: Status {res_get.status_code}")
                    else:
                        response.failure("ID não retornado no corpo do POST")
                except Exception as e:
                    response.failure(f"Erro ao processar JSON: {e}")
            else:
                response.failure(f"POST falhou: {response.status_code} - {response.text}")
