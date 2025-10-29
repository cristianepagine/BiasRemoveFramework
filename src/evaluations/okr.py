"""
Modelo de Avaliação por OKRs (Objectives and Key Results)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class StatusOKR(Enum):
    """Status de um OKR"""
    NAO_INICIADO = "Não Iniciado"
    EM_PROGRESSO = "Em Progresso"
    CONCLUIDO = "Concluído"
    ATRASADO = "Atrasado"
    CANCELADO = "Cancelado"


class NivelOKR(Enum):
    """Nível do OKR"""
    EMPRESA = "Empresa"
    DEPARTAMENTO = "Departamento"
    TIME = "Time"
    INDIVIDUAL = "Individual"


@dataclass
class ResultadoChave:
    """
    Representa um Key Result (Resultado-Chave)

    Atributos:
        id: Identificador único
        descricao: Descrição do resultado-chave
        meta_inicial: Valor inicial
        meta_final: Valor alvo
        valor_atual: Valor atual alcançado
        unidade: Unidade de medida (%, R$, unidades, etc.)
        peso: Peso do resultado-chave no objetivo (0-1)
        status: Status atual
        evidencias: Lista de evidências de progresso
    """
    id: str
    descricao: str
    meta_inicial: float
    meta_final: float
    valor_atual: float
    unidade: str
    peso: float = 1.0
    status: StatusOKR = StatusOKR.EM_PROGRESSO
    evidencias: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validações"""
        if not 0 <= self.peso <= 1:
            raise ValueError("Peso deve estar entre 0 e 1")

    def calcular_progresso(self) -> float:
        """
        Calcula percentual de progresso do resultado-chave

        Returns:
            Percentual de progresso (0-1)
        """
        if self.meta_final == self.meta_inicial:
            return 1.0 if self.valor_atual >= self.meta_final else 0.0

        progresso = (
            (self.valor_atual - self.meta_inicial) /
            (self.meta_final - self.meta_inicial)
        )

        # Limita entre 0 e 1 (mas pode exceder 1 se ultrapassar meta)
        return max(0.0, progresso)

    def calcular_score(self) -> float:
        """
        Calcula score do resultado-chave (0-1)
        Score de 0.7 ou mais é considerado sucesso em OKRs

        Returns:
            Score do resultado-chave
        """
        return min(1.0, self.calcular_progresso())

    def adicionar_evidencia(self, evidencia: str):
        """Adiciona evidência de progresso"""
        self.evidencias.append(evidencia)


@dataclass
class Objetivo:
    """
    Representa um Objective (Objetivo)

    Atributos:
        id: Identificador único
        descricao: Descrição do objetivo (qualitativa e inspiradora)
        nivel: Nível do objetivo
        resultados_chave: Lista de resultados-chave
        data_inicio: Data de início
        data_fim: Data de término
        status: Status atual
        alinhado_com: ID do objetivo superior (se houver)
    """
    id: str
    descricao: str
    nivel: NivelOKR
    resultados_chave: List[ResultadoChave] = field(default_factory=list)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    status: StatusOKR = StatusOKR.EM_PROGRESSO
    alinhado_com: Optional[str] = None

    def adicionar_resultado_chave(self, kr: ResultadoChave):
        """Adiciona um resultado-chave"""
        self.resultados_chave.append(kr)

    def calcular_progresso(self) -> float:
        """
        Calcula progresso geral do objetivo baseado nos resultados-chave

        Returns:
            Progresso geral (0-1)
        """
        if not self.resultados_chave:
            return 0.0

        soma_ponderada = sum(
            kr.calcular_progresso() * kr.peso
            for kr in self.resultados_chave
        )
        soma_pesos = sum(kr.peso for kr in self.resultados_chave)

        return soma_ponderada / soma_pesos if soma_pesos > 0 else 0.0

    def calcular_score(self) -> float:
        """
        Calcula score do objetivo (0-1)

        Returns:
            Score do objetivo
        """
        if not self.resultados_chave:
            return 0.0

        soma_ponderada = sum(
            kr.calcular_score() * kr.peso
            for kr in self.resultados_chave
        )
        soma_pesos = sum(kr.peso for kr in self.resultados_chave)

        return soma_ponderada / soma_pesos if soma_pesos > 0 else 0.0

    def esta_em_risco(self, threshold: float = 0.5) -> bool:
        """
        Verifica se o objetivo está em risco

        Args:
            threshold: Threshold de progresso mínimo esperado

        Returns:
            True se está em risco
        """
        progresso = self.calcular_progresso()

        # Calcula progresso esperado baseado no tempo
        if self.data_inicio and self.data_fim:
            tempo_total = (self.data_fim - self.data_inicio).days
            tempo_decorrido = (datetime.now() - self.data_inicio).days

            if tempo_total > 0:
                progresso_esperado = tempo_decorrido / tempo_total
                return progresso < (progresso_esperado * threshold)

        return progresso < threshold


@dataclass
class AvaliacaoOKR:
    """
    Representa uma avaliação completa de OKRs

    Atributos:
        id: Identificador único
        pessoa_id: ID da pessoa
        periodo: Período (ex: "2024-Q1")
        objetivos: Lista de objetivos
        data_criacao: Data de criação
        data_ultima_atualizacao: Data da última atualização
        insights: Insights documentados
        proximos_passos: Próximos passos planejados
        status: Status da avaliação
    """
    id: str
    pessoa_id: str
    periodo: str
    objetivos: List[Objetivo] = field(default_factory=list)
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None
    insights: List[str] = field(default_factory=list)
    proximos_passos: Optional[str] = None
    status: str = "EM_PROGRESSO"  # EM_PROGRESSO, CONCLUIDO, REVISAO

    def adicionar_objetivo(self, objetivo: Objetivo):
        """Adiciona um objetivo"""
        self.objetivos.append(objetivo)

    def calcular_score_geral(self) -> float:
        """
        Calcula score geral da avaliação

        Returns:
            Score geral (0-1)
        """
        if not self.objetivos:
            return 0.0

        scores = [obj.calcular_score() for obj in self.objetivos]
        return sum(scores) / len(scores)

    def calcular_progresso_geral(self) -> float:
        """
        Calcula progresso geral da avaliação

        Returns:
            Progresso geral (0-1)
        """
        if not self.objetivos:
            return 0.0

        progressos = [obj.calcular_progresso() for obj in self.objetivos]
        return sum(progressos) / len(progressos)

    def obter_objetivos_em_risco(self) -> List[Objetivo]:
        """
        Obtém objetivos que estão em risco

        Returns:
            Lista de objetivos em risco
        """
        return [obj for obj in self.objetivos if obj.esta_em_risco()]

    def obter_objetivos_completos(self, threshold: float = 0.7) -> List[Objetivo]:
        """
        Obtém objetivos considerados completos

        Args:
            threshold: Score mínimo para considerar completo

        Returns:
            Lista de objetivos completos
        """
        return [
            obj for obj in self.objetivos
            if obj.calcular_score() >= threshold
        ]

    def adicionar_insight(self, insight: str):
        """Adiciona um insight"""
        self.insights.append(insight)

    def to_dict(self) -> dict:
        """Converte avaliação para dicionário"""
        return {
            'id': self.id,
            'pessoa_id': self.pessoa_id,
            'periodo': self.periodo,
            'status': self.status,
            'score_geral': self.calcular_score_geral(),
            'progresso_geral': self.calcular_progresso_geral(),
            'total_objetivos': len(self.objetivos),
            'objetivos_completos': len(self.obter_objetivos_completos()),
            'objetivos_em_risco': len(self.obter_objetivos_em_risco()),
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_ultima_atualizacao': (
                self.data_ultima_atualizacao.isoformat()
                if self.data_ultima_atualizacao else None
            )
        }
