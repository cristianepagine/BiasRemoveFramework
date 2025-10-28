"""
Modelo de Avaliação 360 Graus
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class TipoAvaliador(Enum):
    """Tipo de avaliador na avaliação 360"""
    AUTOAVALIACAO = "Autoavaliação"
    SUPERIOR = "Superior"
    PAR = "Par/Colega"
    SUBORDINADO = "Subordinado"
    CLIENTE_INTERNO = "Cliente Interno"


@dataclass
class Questao360:
    """
    Representa uma questão na avaliação 360

    Atributos:
        id: Identificador único
        texto: Texto da questão
        categoria: Categoria da questão (ex: Liderança, Comunicação)
        peso: Peso da questão
    """
    id: str
    texto: str
    categoria: str
    peso: float = 1.0

    def __post_init__(self):
        """Validações"""
        if not 0 <= self.peso <= 1:
            raise ValueError("Peso deve estar entre 0 e 1")


@dataclass
class Resposta360:
    """
    Representa uma resposta a uma questão

    Atributos:
        questao_id: ID da questão
        avaliador_id: ID do avaliador
        tipo_avaliador: Tipo do avaliador
        nota: Nota dada (0-10)
        comentario: Comentário opcional
    """
    questao_id: str
    avaliador_id: str
    tipo_avaliador: TipoAvaliador
    nota: float
    comentario: Optional[str] = None

    def __post_init__(self):
        """Validações"""
        if not 0 <= self.nota <= 10:
            raise ValueError("Nota deve estar entre 0 e 10")


@dataclass
class Avaliacao360:
    """
    Representa uma avaliação 360 graus completa

    Atributos:
        id: Identificador único
        pessoa_id: ID da pessoa avaliada
        periodo: Período da avaliação
        data_inicio: Data de início
        data_fim: Data de término
        questoes: Dicionário de questões
        respostas: Lista de respostas
        relatorio_feedback: Relatório de feedback gerado
        plano_melhoria: Plano de melhoria
        status: Status da avaliação
    """
    id: str
    pessoa_id: str
    periodo: str
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    questoes: Dict[str, Questao360] = field(default_factory=dict)
    respostas: List[Resposta360] = field(default_factory=list)
    relatorio_feedback: Optional[str] = None
    plano_melhoria: Optional[str] = None
    status: str = "EM_ANDAMENTO"  # EM_ANDAMENTO, COLETA_COMPLETA, FEEDBACK_FORNECIDO

    def adicionar_resposta(self, resposta: Resposta360):
        """Adiciona uma resposta"""
        self.respostas.append(resposta)

    def calcular_media_por_tipo_avaliador(self) -> Dict[str, float]:
        """
        Calcula média de notas por tipo de avaliador

        Returns:
            Dicionário com média por tipo de avaliador
        """
        medias = {}

        # Agrupa respostas por tipo de avaliador
        por_tipo = {}
        for resposta in self.respostas:
            tipo = resposta.tipo_avaliador.value
            if tipo not in por_tipo:
                por_tipo[tipo] = []
            por_tipo[tipo].append(resposta.nota)

        # Calcula médias
        for tipo, notas in por_tipo.items():
            medias[tipo] = sum(notas) / len(notas) if notas else 0.0

        return medias

    def calcular_media_por_categoria(self) -> Dict[str, float]:
        """
        Calcula média de notas por categoria

        Returns:
            Dicionário com média por categoria
        """
        medias = {}

        # Agrupa respostas por categoria
        por_categoria = {}
        for resposta in self.respostas:
            questao = self.questoes.get(resposta.questao_id)
            if questao is None:
                continue

            categoria = questao.categoria
            if categoria not in por_categoria:
                por_categoria[categoria] = []
            por_categoria[categoria].append(resposta.nota)

        # Calcula médias
        for categoria, notas in por_categoria.items():
            medias[categoria] = sum(notas) / len(notas) if notas else 0.0

        return medias

    def calcular_media_geral(self, ponderada: bool = True) -> float:
        """
        Calcula média geral da avaliação

        Args:
            ponderada: Se True, pondera pelas questões

        Returns:
            Média geral
        """
        if not self.respostas:
            return 0.0

        if ponderada:
            soma_notas = 0.0
            soma_pesos = 0.0

            for resposta in self.respostas:
                questao = self.questoes.get(resposta.questao_id)
                if questao is None:
                    continue

                soma_notas += resposta.nota * questao.peso
                soma_pesos += questao.peso

            return soma_notas / soma_pesos if soma_pesos > 0 else 0.0
        else:
            return sum(r.nota for r in self.respostas) / len(self.respostas)

    def comparar_autoavaliacao_com_outros(self) -> Dict[str, float]:
        """
        Compara autoavaliação com avaliação de outros

        Returns:
            Dicionário com diferenças por categoria
        """
        # Separa autoavaliação das demais
        notas_auto = {}
        notas_outros = {}

        for resposta in self.respostas:
            questao = self.questoes.get(resposta.questao_id)
            if questao is None:
                continue

            categoria = questao.categoria

            if resposta.tipo_avaliador == TipoAvaliador.AUTOAVALIACAO:
                if categoria not in notas_auto:
                    notas_auto[categoria] = []
                notas_auto[categoria].append(resposta.nota)
            else:
                if categoria not in notas_outros:
                    notas_outros[categoria] = []
                notas_outros[categoria].append(resposta.nota)

        # Calcula diferenças
        diferencas = {}
        for categoria in set(list(notas_auto.keys()) + list(notas_outros.keys())):
            media_auto = (
                sum(notas_auto.get(categoria, [])) / len(notas_auto.get(categoria, [1]))
                if notas_auto.get(categoria) else 0
            )
            media_outros = (
                sum(notas_outros.get(categoria, [])) / len(notas_outros.get(categoria, [1]))
                if notas_outros.get(categoria) else 0
            )

            diferencas[categoria] = media_auto - media_outros

        return diferencas

    def identificar_pontos_fortes(self, threshold: float = 8.0) -> List[str]:
        """
        Identifica categorias com desempenho forte

        Args:
            threshold: Nota mínima para ser considerado ponto forte

        Returns:
            Lista de categorias consideradas pontos fortes
        """
        medias_categorias = self.calcular_media_por_categoria()
        return [
            categoria
            for categoria, media in medias_categorias.items()
            if media >= threshold
        ]

    def identificar_pontos_desenvolvimento(self, threshold: float = 6.0) -> List[str]:
        """
        Identifica categorias que precisam desenvolvimento

        Args:
            threshold: Nota máxima para ser considerado ponto de desenvolvimento

        Returns:
            Lista de categorias que precisam desenvolvimento
        """
        medias_categorias = self.calcular_media_por_categoria()
        return [
            categoria
            for categoria, media in medias_categorias.items()
            if media < threshold
        ]

    def to_dict(self) -> dict:
        """Converte avaliação para dicionário"""
        return {
            'id': self.id,
            'pessoa_id': self.pessoa_id,
            'periodo': self.periodo,
            'status': self.status,
            'data_inicio': self.data_inicio.isoformat(),
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'media_geral': self.calcular_media_geral(),
            'total_respostas': len(self.respostas),
            'total_avaliadores': len(set(r.avaliador_id for r in self.respostas)),
            'pontos_fortes': self.identificar_pontos_fortes(),
            'pontos_desenvolvimento': self.identificar_pontos_desenvolvimento()
        }
