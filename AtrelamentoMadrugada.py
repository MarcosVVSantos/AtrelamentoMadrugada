import math
import requests
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

class RecolhimentoService:
    def __init__(self, base_url: str, max_motos_por_guincho: int = 5):
        """
        Inicializa o serviço de recolhimento.
        
        :param base_url: URL base da API
        :param max_motos_por_guincho: Número máximo de motos por guincho
        """
        self.base_url = base_url
        self.max_motos = max_motos_por_guincho
    
    def haversine_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calcula a distância entre duas coordenadas geográficas (em km).
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371.0  # Raio da Terra em km
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_usuario_location(self, usuario_id: int) -> Optional[Tuple[float, float]]:
        """
        Obtém a localização do usuário através da API.
        
        :param usuario_id: ID do usuário
        :return: Tupla (latitude, longitude) ou None se falhar
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/EnderecoVirtual/usuario/{usuario_id}")
            response.raise_for_status()
            data = response.json()
            return (data['latitude'], data['longitude'])
        except Exception as e:
            print(f"Erro ao obter localização do usuário {usuario_id}: {e}")
            return None
    
    def atrelar_moto_guincho(self, veiculo_id: int, veiculo_suporte_id: int) -> bool:
        """
        Atrela uma moto a um guincho através da API.
        
        :param veiculo_id: ID da moto
        :param veiculo_suporte_id: ID do guincho
        :return: True se sucesso, False se falhar
        """
        try:
            payload = {
                "veiculoId": veiculo_id,
                "veiculoSuporteId": veiculo_suporte_id
            }
            response = requests.post(f"{self.base_url}/api/v1/EstoqueVeiculoSuporte/atrelar", json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Erro ao atrelar moto {veiculo_id} ao guincho {veiculo_suporte_id}: {e}")
            return False
    
    def criar_servico_recolhimento(self, usuario_id: int) -> bool:
        """
        Cria serviço de recolhimento para o usuário.
        
        :param usuario_id: ID do usuário
        :return: True se sucesso, False se falhar
        """
        try:
            # Primeiro cria o serviço de inadimplente
            response = requests.post(f"{self.base_url}/api/v1/Inadimplentes/servico/{usuario_id}")
            response.raise_for_status()
            
            # Depois cria o serviço de recolhimento
            response = requests.post(f"{self.base_url}/api/v1/Recolhimento/criarServicos")
            response.raise_for_status()
            
            return True
        except Exception as e:
            print(f"Erro ao criar serviço de recolhimento para usuário {usuario_id}: {e}")
            return False
    
    def otimizar_rotas(self, guinchos: List[Dict], usuarios: List[Dict]) -> Dict[str, List[int]]:
        """
        Otimiza as rotas de recolhimento e executa todas as etapas.
        
        :param guinchos: Lista de guinchos disponíveis
        :param usuarios: Lista de usuários com motos para recolher
        :return: Dicionário com as rotas atribuídas {guincho_id: [veiculo_id1, veiculo_id2, ...]}
        """
        # Obter localizações das motos
        motos_info = []
        for usuario in usuarios:
            location = self.get_usuario_location(usuario['usuarioId'])
            if location:
                motos_info.append({
                    'usuarioId': usuario['usuarioId'],
                    'veiculoId': usuario['veiculoId'],
                    'location': location
                })
        
        # Preparar dados para otimização
        guincho_locations = {g['id']: g['location'] for g in guinchos}
        moto_locations = [(m['location'][0], m['location'][1], m['veiculoId']) for m in motos_info]
        
        assigned_motos = set()
        routes = defaultdict(list)
        
        for guincho in guinchos:
            guincho_id = guincho['id']
            guincho_location = guincho['location']
            capacity = guincho.get('capacity', self.max_motos)
            
            # Filtrar motos não atribuídas
            available_motos = [
                (lat, lon, v_id) for lat, lon, v_id in moto_locations 
                if v_id not in assigned_motos
            ]
            
            if not available_motos:
                continue
            
            # Encontrar motos mais próximas
            nearest_motos = []
            for lat, lon, veiculo_id in available_motos:
                distance = self.haversine_distance(guincho_location, (lat, lon))
                nearest_motos.append((veiculo_id, distance))
            
            # Ordenar por distância
            nearest_motos.sort(key=lambda x: x[1])
            
            # Atribuir até a capacidade máxima
            for veiculo_id, _ in nearest_motos[:capacity]:
                # Atrelar moto ao guincho
                if self.atrelar_moto_guincho(veiculo_id, guincho_id):
                    routes[guincho_id].append(veiculo_id)
                    assigned_motos.add(veiculo_id)
                    
                    # Criar serviço de recolhimento
                    usuario_id = next(m['usuarioId'] for m in motos_info if m['veiculoId'] == veiculo_id)
                    if not self.criar_servico_recolhimento(usuario_id):
                        print(f"Falha ao criar serviço para o usuário {usuario_id}")
                
                if len(routes[guincho_id]) >= capacity:
                    break
        
        return dict(routes)

# Exemplo de uso
if __name__ == "__main__":
    API_BASE_URL = "https://sua-api.com"  # Substitua pela URL real da API
    
    # Dados de exemplo
    guinchos = [
        {'id': 1, 'location': (-23.5505, -46.6333), 'capacity': 3},  # São Paulo
        {'id': 2, 'location': (-22.9068, -43.1729), 'capacity': 4},  # Rio de Janeiro
    ]
    
    usuarios = [
        {'usuarioId': 101, 'veiculoId': 201},
        {'usuarioId': 102, 'veiculoId': 202},
        {'usuarioId': 103, 'veiculoId': 203},
        {'usuarioId': 104, 'veiculoId': 204},
        {'usuarioId': 105, 'veiculoId': 205},
        {'usuarioId': 106, 'veiculoId': 206},
        {'usuarioId': 107, 'veiculoId': 207},
    ]
    
    # Inicializar serviço
    service = RecolhimentoService(base_url=API_BASE_URL)
    
    # Executar otimização
    rotas_otimizadas = service.otimizar_rotas(guinchos, usuarios)
    print("Rotas otimizadas e serviços criados:", rotas_otimizadas)