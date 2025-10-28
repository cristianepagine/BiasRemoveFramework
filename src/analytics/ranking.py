"""
Classificação Automática da Pessoa Mais Apta
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from src.models import Pessoa


@dataclass
class CriterioAvaliacao:
    """
    Representa um critério de avaliação

    Atributos:
        nome: Nome do critério
        peso: Peso do critério (0-1)
        descricao: Descrição do critério
    """
    nome: str
    peso: float = 1.0
    descricao: str = ""

    def __post_init__(self):
        if not 0 <= self.peso <= 1:
            raise ValueError("Peso deve estar entre 0 e 1")


@dataclass
class ScorePessoa:
    """
    Score final de uma pessoa

    Atributos:
        pessoa_id: ID da pessoa
        scores_por_criterio: Scores individuais por critério
        score_final: Score final ponderado
        posicao: Posição no ranking
        detalhes: Detalhes adicionais
    """
    pessoa_id: str
    scores_por_criterio: Dict[str, float]
    score_final: float
    posicao: Optional[int] = None
    detalhes: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'pessoa_id': self.pessoa_id,
            'score_final': round(self.score_final, 2),
            'posicao': self.posicao,
            'scores_por_criterio': {
                k: round(v, 2) for k, v in self.scores_por_criterio.items()
            },
            'detalhes': self.detalhes
        }


@dataclass
class ResultadoRanking:
    """Resultado do ranking"""
    scores: List[ScorePessoa]
    criterios: List[CriterioAvaliacao]
    metadados: Dict[str, any] = field(default_factory=dict)

    def obter_top_n(self, n: int) -> List[ScorePessoa]:
        """Obtém top N pessoas"""
        return self.scores[:min(n, len(self.scores))]

    def obter_pessoa(self, pessoa_id: str) -> Optional[ScorePessoa]:
        """Obtém score de uma pessoa específica"""
        for score in self.scores:
            if score.pessoa_id == pessoa_id:
                return score
        return None


class RankingCalculator:
    """
    Calculador de ranking para classificação automática

    Implementa o cálculo de score final conforme o framework:
    Si = Σ(Aij) onde Aij é a avaliação ajustada da pessoa i no critério j
    """

    def __init__(self):
        """Inicializa calculador"""
        pass

    def calcular_score_final(
        self,
        pessoa_id: str,
        avaliacoes_por_criterio: Dict[str, float],
        criterios: List[CriterioAvaliacao]
    ) -> ScorePessoa:
        """
        Calcula score final de uma pessoa

        Fórmula: Si = Σ(Aij * Wj)
        Onde:
        - Si é o score final da pessoa i
        - Aij é a avaliação da pessoa i no critério j
        - Wj é o peso do critério j

        Args:
            pessoa_id: ID da pessoa
            avaliacoes_por_criterio: {nome_criterio: score}
            criterios: Lista de critérios com pesos

        Returns:
            ScorePessoa com score final calculado
        """
        # Cria mapa de pesos
        pesos = {c.nome: c.peso for c in criterios}

        # Calcula score ponderado
        soma_ponderada = 0.0
        soma_pesos = 0.0

        for nome_criterio, score in avaliacoes_por_criterio.items():
            peso = pesos.get(nome_criterio, 1.0)
            soma_ponderada += score * peso
            soma_pesos += peso

        # Score final (pode ser soma simples ou média ponderada)
        # Usando soma conforme framework
        score_final = soma_ponderada

        return ScorePessoa(
            pessoa_id=pessoa_id,
            scores_por_criterio=avaliacoes_por_criterio.copy(),
            score_final=score_final
        )

    def calcular_ranking(
        self,
        avaliacoes: Dict[str, Dict[str, float]],
        criterios: List[CriterioAvaliacao],
        pessoas: Optional[Dict[str, Pessoa]] = None
    ) -> ResultadoRanking:
        """
        Calcula ranking completo

        Args:
            avaliacoes: {pessoa_id: {criterio: score}}
            criterios: Lista de critérios
            pessoas: Dicionário opcional de pessoas para enriquecer dados

        Returns:
            Resultado do ranking ordenado
        """
        # Calcula scores para todas as pessoas
        scores = []

        for pessoa_id, avaliacoes_criterio in avaliacoes.items():
            score = self.calcular_score_final(
                pessoa_id,
                avaliacoes_criterio,
                criterios
            )

            # Adiciona informações da pessoa se disponível
            if pessoas and pessoa_id in pessoas:
                pessoa = pessoas[pessoa_id]
                score.detalhes = {
                    'nome': pessoa.nome,
                    'cargo': pessoa.cargo,
                    'nivel': pessoa.nivel_hierarquico.name,
                    'genero': pessoa.genero.value,
                    'departamento': pessoa.departamento
                }

            scores.append(score)

        # Ordena por score final (decrescente)
        scores_ordenados = sorted(
            scores,
            key=lambda x: x.score_final,
            reverse=True
        )

        # Atribui posições
        for i, score in enumerate(scores_ordenados, 1):
            score.posicao = i

        return ResultadoRanking(
            scores=scores_ordenados,
            criterios=criterios,
            metadados={
                'total_pessoas': len(scores_ordenados),
                'total_criterios': len(criterios),
                'score_maximo': scores_ordenados[0].score_final if scores_ordenados else 0,
                'score_minimo': scores_ordenados[-1].score_final if scores_ordenados else 0,
                'score_medio': np.mean([s.score_final for s in scores_ordenados]) if scores_ordenados else 0
            }
        )

    def gerar_relatorio_ranking(
        self,
        resultado: ResultadoRanking,
        top_n: int = 10
    ) -> str:
        """
        Gera relatório do ranking

        Args:
            resultado: Resultado do ranking
            top_n: Número de top pessoas a mostrar

        Returns:
            Relatório em texto
        """
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("RANKING DE CLASSIFICAÇÃO")
        relatorio.append("=" * 80)
        relatorio.append("")

        relatorio.append("CRITÉRIOS UTILIZADOS:")
        for criterio in resultado.criterios:
            relatorio.append(f"  - {criterio.nome} (Peso: {criterio.peso:.2f})")
        relatorio.append("")

        relatorio.append(f"TOP {top_n} PESSOAS:")
        relatorio.append("-" * 80)

        # Cabeçalho
        relatorio.append(
            f"{'Pos':<5} {'ID':<15} {'Nome':<25} {'Score':<10} {'Detalhes'}"
        )
        relatorio.append("-" * 80)

        # Top N pessoas
        for score in resultado.obter_top_n(top_n):
            nome = score.detalhes.get('nome', 'N/A')[:24]
            cargo = score.detalhes.get('cargo', 'N/A')
            nivel = score.detalhes.get('nivel', 'N/A')

            relatorio.append(
                f"{score.posicao:<5} "
                f"{score.pessoa_id:<15} "
                f"{nome:<25} "
                f"{score.score_final:<10.2f} "
                f"{cargo} ({nivel})"
            )

        relatorio.append("-" * 80)
        relatorio.append("")

        # Estatísticas
        relatorio.append("ESTATÍSTICAS:")
        for key, value in resultado.metadados.items():
            if isinstance(value, float):
                relatorio.append(f"  {key}: {value:.2f}")
            else:
                relatorio.append(f"  {key}: {value}")

        relatorio.append("=" * 80)

        return "\n".join(relatorio)


def combinar_avaliacoes_em_scores(
    avaliacoes_competencias: Optional[Dict[str, float]] = None,
    avaliacoes_360: Optional[Dict[str, float]] = None,
    avaliacoes_okr: Optional[Dict[str, float]] = None,
    avaliacoes_ninebox_desempenho: Optional[Dict[str, float]] = None,
    avaliacoes_ninebox_potencial: Optional[Dict[str, float]] = None,
    usar_ninebox: bool = True
) -> Tuple[Dict[str, Dict[str, float]], List[CriterioAvaliacao]]:
    """
    Combina diferentes tipos de avaliações em scores por critério

    Args:
        avaliacoes_competencias: {pessoa_id: score}
        avaliacoes_360: {pessoa_id: score}
        avaliacoes_okr: {pessoa_id: score}
        avaliacoes_ninebox_desempenho: {pessoa_id: score}
        avaliacoes_ninebox_potencial: {pessoa_id: score}
        usar_ninebox: Se True, usa Nine Box como critério principal

    Returns:
        Tupla (avaliacoes_combinadas, criterios)
    """
    # Define critérios
    criterios = []

    if usar_ninebox and avaliacoes_ninebox_desempenho:
        # Se usar Nine Box, ele tem maior peso
        criterios.append(CriterioAvaliacao(
            nome="Desempenho (Nine Box)",
            peso=1.0,
            descricao="Score de desempenho da matriz Nine Box"
        ))
        criterios.append(CriterioAvaliacao(
            nome="Potencial (Nine Box)",
            peso=1.0,
            descricao="Score de potencial da matriz Nine Box"
        ))
    else:
        # Senão, usa avaliações individuais
        if avaliacoes_competencias:
            criterios.append(CriterioAvaliacao(
                nome="Competências",
                peso=1.0,
                descricao="Avaliação por competências"
            ))

        if avaliacoes_360:
            criterios.append(CriterioAvaliacao(
                nome="360 Graus",
                peso=0.9,
                descricao="Avaliação 360 graus"
            ))

        if avaliacoes_okr:
            criterios.append(CriterioAvaliacao(
                nome="OKRs",
                peso=1.2,
                descricao="Avaliação de OKRs"
            ))

    # Combina avaliações
    todas_pessoas = set()

    if avaliacoes_competencias:
        todas_pessoas.update(avaliacoes_competencias.keys())
    if avaliacoes_360:
        todas_pessoas.update(avaliacoes_360.keys())
    if avaliacoes_okr:
        todas_pessoas.update(avaliacoes_okr.keys())
    if avaliacoes_ninebox_desempenho:
        todas_pessoas.update(avaliacoes_ninebox_desempenho.keys())

    # Monta dicionário combinado
    avaliacoes_combinadas = {}

    for pessoa_id in todas_pessoas:
        scores_pessoa = {}

        if usar_ninebox and avaliacoes_ninebox_desempenho:
            if pessoa_id in avaliacoes_ninebox_desempenho:
                scores_pessoa["Desempenho (Nine Box)"] = avaliacoes_ninebox_desempenho[pessoa_id]
            if avaliacoes_ninebox_potencial and pessoa_id in avaliacoes_ninebox_potencial:
                scores_pessoa["Potencial (Nine Box)"] = avaliacoes_ninebox_potencial[pessoa_id]
        else:
            if avaliacoes_competencias and pessoa_id in avaliacoes_competencias:
                scores_pessoa["Competências"] = avaliacoes_competencias[pessoa_id]

            if avaliacoes_360 and pessoa_id in avaliacoes_360:
                scores_pessoa["360 Graus"] = avaliacoes_360[pessoa_id]

            if avaliacoes_okr and pessoa_id in avaliacoes_okr:
                scores_pessoa["OKRs"] = avaliacoes_okr[pessoa_id]

        if scores_pessoa:  # Só adiciona se tiver pelo menos um score
            avaliacoes_combinadas[pessoa_id] = scores_pessoa

    return avaliacoes_combinadas, criterios
