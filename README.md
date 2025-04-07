# AtrelamentoMadrugada

### O que o script faz:
1. **Calcula a distância** entre as motos e os guinchos usando a fórmula de Haversine.
2. **Atribui motos aos guinchos** com base na proximidade, considerando a capacidade máxima de cada guincho.
3. **Cria um serviço de recolhimento** para cada moto, quando ela é atribuída a um guincho.


### Passos para rodar o script:

1. **Instalar dependências**:
   O script utiliza `requests` para fazer chamadas HTTP. Instale a biblioteca `requests` se não a tiver:
   ```bash
   pip install requests
   ```

2. **Ajustar a URL da API**:
   A variável `API_BASE_URL` deve ser configurada para o endpoint da sua API.

3. **Rodar o script**:
   O script pode ser executado a partir de qualquer ambiente Python, como um terminal ou IDE. Basta definir as variáveis de entrada (dados dos guinchos e usuários) e o URL da API, e depois executar o script.

### Como rodar:

1. **Configure a URL da API** substituindo `API_BASE_URL` com o endereço correto da sua API.
2. **Execute o script** usando Python.

Isso deve permitir que você otimize a alocação dos guinchos e crie os serviços automaticamente.
