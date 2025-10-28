"""
Modelo de Avaliação Nine Box
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum


class CategoriaDesempenho(Enum):
    """Categoria de desempenho"""
    BAIXO = "Baixo"
    MEDIO = "Médio"
    ALTO = "Alto"


class CategoriaPotencial(Enum):
    """Categoria de potencial"""
    BAIXO = "Baixo"
    MEDIO = "Médio"
    ALTO = "Alto"


class QuadranteNineBox(Enum):
    """Quadrantes do Nine Box"""
    # Formato: (Desempenho, Potencial)
    BAIXO_BAIXO = (CategoriaDesempenho.BAIXO, CategoriaPotencial.BAIXO)
    BAIXO_MEDIO = (CategoriaDesempenho.BAIXO, CategoriaPotencial.MEDIO)
    BAIXO_ALTO = (CategoriaDesempenho.BAIXO, CategoriaPotencial.ALTO)
    MEDIO_BAIXO = (CategoriaDesempenho.MEDIO, CategoriaPotencial.BAIXO)
    MEDIO_MEDIO = (CategoriaDesempenho.MEDIO, CategoriaPotencial.MEDIO)
    MEDIO_ALTO = (CategoriaDesempenho.MEDIO, CategoriaPotencial.ALTO)
    ALTO_BAIXO = (CategoriaDesempenho.ALTO, CategoriaPotencial.BAIXO)
    ALTO_MEDIO = (CategoriaDesempenho.ALTO, CategoriaPotencial.MEDIO)
    ALTO_ALTO = (CategoriaDesempenho.ALTO, CategoriaPotencial.ALTO)


# Descrições dos quadrantes
DESCRICOES_QUADRANTES = {
    QuadranteNineBox.BAIXO_BAIXO: {
        "nome": "Necessita Melhoria Urgente",
        "acao": "Plano de Performance Imediato ou Desligamento",
        "prioridade": 1
    },
    QuadranteNineBox.BAIXO_MEDIO: {
        "nome": "Enigma",
        "acao": "Avaliar Fit e Desenvolver Performance",
        "prioridade": 2
    },
    QuadranteNineBox.BAIXO_ALTO: {
        "nome": "Diamante Bruto",
        "acao": "Mentoria Intensiva e Desenvolvimento",
        "prioridade": 3
    },
    QuadranteNineBox.MEDIO_BAIXO: {
        "nome": "Contribuidor Consistente",
        "acao": "Manter no Cargo Atual",
        "prioridade": 4
    },
    QuadranteNineBox.MEDIO_MEDIO: {
        "nome": "Profissional Sólido",
        "acao": "Desenvolvimento Gradual",
        "prioridade": 5
    },
    QuadranteNineBox.MEDIO_ALTO: {
        "nome": "Alto Potencial em Crescimento",
        "acao": "Plano de Desenvolvimento Acelerado",
        "prioridade": 7
    },
    QuadranteNineBox.ALTO_BAIXO: {
        "nome": "Especialista Experiente",
        "acao": "Manter e Aproveitar Experiência",
        "prioridade": 6
    },
    QuadranteNineBox.ALTO_MEDIO: {
        "nome": "Forte Performer",
        "acao": "Considerar Promoção Futura",
        "prioridade": 8
    },
    QuadranteNineBox.ALTO_ALTO: {
        "nome": "Talento Crítico / Sucessor",
        "acao": "Promoção Prioritária e Retenção",
        "prioridade": 9
    },
}


@dataclass
class PosicaoNineBox:
    """
    Representa a posição de uma pessoa no Nine Box

    Atributos:
        pessoa_id: ID da pessoa
        desempenho: Categoria de desempenho
        potencial: Categoria de potencial
        score_desempenho: Score numérico de desempenho (0-10)
        score_potencial: Score numérico de potencial (0-10)
        quadrante: Quadrante do Nine Box
        notas: Notas adicionais
    """
    pessoa_id: str
    desempenho: CategoriaDesempenho
    potencial: CategoriaPotencial
    score_desempenho: float
    score_potencial: float
    quadrante: QuadranteNineBox
    notas: Optional[str] = None

    def __post_init__(self):
        """Validações"""
        if not 0 <= self.score_desempenho <= 10:
            raise ValueError("Score de desempenho deve estar entre 0 e 10")
        if not 0 <= self.score_potencial <= 10:
            raise ValueError("Score de potencial deve estar entre 0 e 10")

    def obter_descricao_quadrante(self) -> Dict[str, str]:
        """Obtém descrição do quadrante"""
        return DESCRICOES_QUADRANTES.get(self.quadrante, {})

    def prioridade_desenvolvimento(self) -> int:
        """Obtém prioridade de desenvolvimento (1-9, sendo 9 o mais alto)"""
        return self.obter_descricao_quadrante().get("prioridade", 5)


@dataclass
class AvaliacaoNineBox:
    """
    Representa uma avaliação completa usando Nine Box

    Atributos:
        id: Identificador único
        periodo: Período da avaliação
        data_avaliacao: Data da avaliação
        posicoes: Lista de posições das pessoas
        criterios_desempenho: Critérios usados para avaliar desempenho
        criterios_potencial: Critérios usados para avaliar potencial
        comite_avaliadores: IDs dos avaliadores do comitê
        planos_acao: Planos de ação por pessoa
        status: Status da avaliação
    """
    id: str
    periodo: str
    data_avaliacao: datetime
    posicoes: List[PosicaoNineBox] = field(default_factory=list)
    criterios_desempenho: List[str] = field(default_factory=list)
    criterios_potencial: List[str] = field(default_factory=list)
    comite_avaliadores: List[str] = field(default_factory=list)
    planos_acao: Dict[str, str] = field(default_factory=dict)
    status: str = "CONCLUIDO"

    def adicionar_posicao(self, posicao: PosicaoNineBox):
        """Adiciona uma posição"""
        self.posicoes.append(posicao)

    def obter_por_quadrante(self, quadrante: QuadranteNineBox) -> List[PosicaoNineBox]:
        """Obtém todas as pessoas em um quadrante específico"""
        return [p for p in self.posicoes if p.quadrante == quadrante]

    def obter_talentos_criticos(self) -> List[PosicaoNineBox]:
        """Obtém talentos críticos (Alto-Alto)"""
        return self.obter_por_quadrante(QuadranteNineBox.ALTO_ALTO)

    def obter_alto_potencial(self) -> List[PosicaoNineBox]:
        """Obtém pessoas com alto potencial"""
        return [
            p for p in self.posicoes
            if p.potencial == CategoriaPotencial.ALTO
        ]

    def obter_alto_desempenho(self) -> List[PosicaoNineBox]:
        """Obtém pessoas com alto desempenho"""
        return [
            p for p in self.posicoes
            if p.desempenho == CategoriaDesempenho.ALTO
        ]

    def obter_prioridades_retencao(self) -> List[PosicaoNineBox]:
        """Obtém pessoas prioritárias para retenção (alto potencial ou alto desempenho)"""
        return [
            p for p in self.posicoes
            if p.potencial == CategoriaPotencial.ALTO or
               p.desempenho == CategoriaDesempenho.ALTO
        ]

    def obter_necessitam_atencao(self) -> List[PosicaoNineBox]:
        """Obtém pessoas que necessitam atenção (baixo desempenho)"""
        return [
            p for p in self.posicoes
            if p.desempenho == CategoriaDesempenho.BAIXO
        ]

    def classificar_por_prioridade(self) -> List[PosicaoNineBox]:
        """
        Classifica pessoas por prioridade de desenvolvimento

        Returns:
            Lista ordenada por prioridade (maior primeiro)
        """
        return sorted(
            self.posicoes,
            key=lambda p: p.prioridade_desenvolvimento(),
            reverse=True
        )

    def adicionar_plano_acao(self, pessoa_id: str, plano: str):
        """Adiciona plano de ação para uma pessoa"""
        self.planos_acao[pessoa_id] = plano

    def estatisticas(self) -> Dict:
        """Retorna estatísticas da avaliação"""
        total = len(self.posicoes)

        if total == 0:
            return {}

        # Conta por categoria
        desempenho_counts = {
            CategoriaDesempenho.BAIXO: 0,
            CategoriaDesempenho.MEDIO: 0,
            CategoriaDesempenho.ALTO: 0
        }
        potencial_counts = {
            CategoriaPotencial.BAIXO: 0,
            CategoriaPotencial.MEDIO: 0,
            CategoriaPotencial.ALTO: 0
        }

        for pos in self.posicoes:
            desempenho_counts[pos.desempenho] += 1
            potencial_counts[pos.potencial] += 1

        return {
            'total_avaliados': total,
            'distribuicao_desempenho': {
                k.value: v for k, v in desempenho_counts.items()
            },
            'distribuicao_potencial': {
                k.value: v for k, v in potencial_counts.items()
            },
            'talentos_criticos': len(self.obter_talentos_criticos()),
            'alto_potencial': len(self.obter_alto_potencial()),
            'necessitam_atencao': len(self.obter_necessitam_atencao()),
            'media_desempenho': sum(p.score_desempenho for p in self.posicoes) / total,
            'media_potencial': sum(p.score_potencial for p in self.posicoes) / total
        }

    def to_dict(self) -> dict:
        """Converte avaliação para dicionário"""
        return {
            'id': self.id,
            'periodo': self.periodo,
            'data_avaliacao': self.data_avaliacao.isoformat(),
            'status': self.status,
            'estatisticas': self.estatisticas()
        }


def calcular_categoria(score: float, thresholds: Tuple[float, float] = (6.0, 8.0)) -> Enum:
    """
    Calcula categoria (BAIXO, MEDIO, ALTO) baseado em score

    Args:
        score: Score numérico (0-10)
        thresholds: Tupla com (threshold_medio, threshold_alto)

    Returns:
        Categoria correspondente
    """
    threshold_medio, threshold_alto = thresholds

    if score < threshold_medio:
        return CategoriaDesempenho.BAIXO  # Ou CategoriaPotencial.BAIXO
    elif score < threshold_alto:
        return CategoriaDesempenho.MEDIO  # Ou CategoriaPotencial.MEDIO
    else:
        return CategoriaDesempenho.ALTO  # Ou CategoriaPotencial.ALTO


def determinar_quadrante(
    desempenho: CategoriaDesempenho,
    potencial: CategoriaPotencial
) -> QuadranteNineBox:
    """
    Determina o quadrante do Nine Box

    Args:
        desempenho: Categoria de desempenho
        potencial: Categoria de potencial

    Returns:
        Quadrante correspondente
    """
    for quadrante in QuadranteNineBox:
        desemp_quad, pot_quad = quadrante.value
        if desemp_quad == desempenho and pot_quad == potencial:
            return quadrante

    # Fallback (não deveria acontecer)
    return QuadranteNineBox.MEDIO_MEDIO
