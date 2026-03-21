from locust import HttpUser, task, between
import random, string

LOGIN_EMAIL = "admin@floricultura.com"
LOGIN_SENHA  = "123456"

def gerar_cnpj():
    return "".join([str(random.randint(0,9)) for _ in range(14)])

class FornecedorUser(HttpUser):
    host = "http://localhost:8080"
    wait_time = between(1, 3)

    def on_start(self):
        r = self.client.post("/api/auth/login",
            json={"login": LOGIN_EMAIL, "password": LOGIN_SENHA},
            name="[AUTH] Login")
        self.headers = {"Authorization": f"Bearer {r.json()['token']}"}
        self.ultimo_id = None

    @task(3)
    def criar_fornecedor(self):
        r = self.client.post("/api/fornecedores",
            json={"nome": f"Fornecedor {random.randint(1,999999)}",
                  "cnpj": gerar_cnpj(),
                  "endereco": "Rua Teste, 1",
                  "cep": "86070000",
                  "telefone": "43988880000"},
            headers=self.headers,
            name="POST /api/fornecedores")
        if r.status_code == 200:
            self.ultimo_id = r.json().get("id")

    @task(1)
    def buscar_fornecedor(self):
        if self.ultimo_id:
            self.client.get(f"/api/fornecedores/{self.ultimo_id}",
                headers=self.headers,
                name="GET /api/fornecedores/{id}")