"""
Modelo de Avaliação por Competências
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class TipoCompetencia(Enum):
    """Tipo de competência"""
    TECNICA = "Técnica"
    COMPORTAMENTAL = "Comportamental"
    LIDERANCA = "Liderança"
    ESTRATEGICA = "Estratégica"


@dataclass
class Competencia:
    """
    Representa uma competência a ser avaliada

    Atributos:
        id: Identificador único
        nome: Nome da competência
        descricao: Descrição detalhada
        tipo: Tipo da competência
        peso: Peso/importância da competência (0-1)
    """
    id: str
    nome: str
    descricao: str
    tipo: TipoCompetencia
    peso: float = 1.0

    def __post_init__(self):
        """Validações"""
        if not 0 <= self.peso <= 1:
            raise ValueError("Peso deve estar entre 0 e 1")


@dataclass
class AvaliacaoCompetenciaItem:
    """
    Representa a avaliação de uma competência específica

    Atributos:
        competencia_id: ID da competência avaliada
        nota_autoavaliacao: Nota da autoavaliação (0-10)
        nota_gestor: Nota do gestor (0-10)
        nota_consenso: Nota após consenso (0-10)
        observacoes: Observações sobre a avaliação
    """
    competencia_id: str
    nota_autoavaliacao: Optional[float] = None
    nota_gestor: Optional[float] = None
    nota_consenso: Optional[float] = None
    observacoes: Optional[str] = None

    def __post_init__(self):
        """Validações"""
        for nota in [self.nota_autoavaliacao, self.nota_gestor, self.nota_consenso]:
            if nota is not None and not 0 <= nota <= 10:
                raise ValueError("Nota deve estar entre 0 e 10")

    def calcular_consenso(self, peso_autoavaliacao: float = 0.3) -> float:
        """
        Calcula nota de consenso se não foi definida

        Args:
            peso_autoavaliacao: Peso da autoavaliação no cálculo (0-1)

        Returns:
            Nota de consenso calculada
        """
        if self.nota_consenso is not None:
            return self.nota_consenso

        if self.nota_autoavaliacao is None or self.nota_gestor is None:
            raise ValueError("Notas de autoavaliação e gestor devem estar preenchidas")

        peso_gestor = 1 - peso_autoavaliacao
        self.nota_consenso = (
            self.nota_autoavaliacao * peso_autoavaliacao +
            self.nota_gestor * peso_gestor
        )
        return self.nota_consenso


@dataclass
class AvaliacaoCompetencias:
    """
    Representa uma avaliação completa por competências

    Atributos:
        id: Identificador único da avaliação
        pessoa_id: ID da pessoa avaliada
        avaliador_id: ID do avaliador (gestor)
        periodo: Período da avaliação (ex: "2024-Q1")
        data_avaliacao: Data da avaliação
        competencias: Dicionário de competências disponíveis
        itens_avaliacao: Lista de itens avaliados
        plano_desenvolvimento: Plano de desenvolvimento
        status: Status da avaliação
    """
    id: str
    pessoa_id: str
    avaliador_id: str
    periodo: str
    data_avaliacao: datetime
    competencias: Dict[str, Competencia]
    itens_avaliacao: List[AvaliacaoCompetenciaItem] = field(default_factory=list)
    plano_desenvolvimento: Optional[str] = None
    status: str = "PENDENTE"  # PENDENTE, AUTOAVALIACAO_COMPLETA, AVALIACAO_GESTOR_COMPLETA, CONSENSO_REALIZADO

    def adicionar_item(self, item: AvaliacaoCompetenciaItem):
        """Adiciona item de avaliação"""
        self.itens_avaliacao.append(item)

    def calcular_media_final(self, usar_consenso: bool = True) -> float:
        """
        Calcula média final da avaliação

        Args:
            usar_consenso: Se True, usa nota de consenso; se False, usa média ponderada

        Returns:
            Média final ponderada pelas competências
        """
        if not self.itens_avaliacao:
            return 0.0

        soma_notas = 0.0
        soma_pesos = 0.0

        for item in self.itens_avaliacao:
            competencia = self.competencias.get(item.competencia_id)
            if competencia is None:
                continue

            if usar_consenso:
                if item.nota_consenso is None:
                    item.calcular_consenso()
                nota = item.nota_consenso
            else:
                if item.nota_gestor is not None:
                    nota = item.nota_gestor
                elif item.nota_autoavaliacao is not None:
                    nota = item.nota_autoavaliacao
                else:
                    continue

            if nota is not None:
                soma_notas += nota * competencia.peso
                soma_pesos += competencia.peso

        if soma_pesos == 0:
            return 0.0

        return soma_notas / soma_pesos

    def obter_competencias_baixo_desempenho(self, threshold: float = 6.0) -> List[str]:
        """
        Identifica competências com baixo desempenho

        Args:
            threshold: Nota mínima considerada adequada

        Returns:
            Lista de IDs de competências abaixo do threshold
        """
        competencias_baixas = []

        for item in self.itens_avaliacao:
            nota = item.nota_consenso or item.nota_gestor or item.nota_autoavaliacao

            if nota is not None and nota < threshold:
                competencias_baixas.append(item.competencia_id)

        return competencias_baixas

    def to_dict(self) -> dict:
        """Converte avaliação para dicionário"""
        return {
            'id': self.id,
            'pessoa_id': self.pessoa_id,
            'avaliador_id': self.avaliador_id,
            'periodo': self.periodo,
            'data_avaliacao': self.data_avaliacao.isoformat(),
            'status': self.status,
            'media_final': self.calcular_media_final(),
            'total_competencias': len(self.itens_avaliacao),
            'plano_desenvolvimento': self.plano_desenvolvimento
        }
