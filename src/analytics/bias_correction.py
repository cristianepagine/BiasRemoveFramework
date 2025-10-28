"""
Detecção e Correção de Viés de Gênero
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy import stats

from src.models import Genero


@dataclass
class EstatisticasDistribuicao:
    """Estatísticas de distribuição de um grupo"""
    media: float
    mediana: float
    desvio_padrao: float
    minimo: float
    maximo: float
    quartil_25: float
    quartil_75: float
    tamanho: int


@dataclass
class ResultadoAnaliseVies:
    """Resultado da análise de viés de gênero"""
    estatisticas_feminino: EstatisticasDistribuicao
    estatisticas_masculino: EstatisticasDistribuicao
    diferenca_medias: float
    diferenca_percentual: float
    p_value: float  # Teste t de Student
    vies_detectado: bool
    significancia_estatistica: bool


@dataclass
class ResultadoReponderacao:
    """Resultado da reponderação"""
    peso_ajuste_feminino: float
    peso_ajuste_masculino: float
    scores_originais: Dict[str, float]
    scores_ajustados: Dict[str, float]
    analise_pre_ajuste: ResultadoAnaliseVies
    analise_pos_ajuste: Optional[ResultadoAnaliseVies]


class BiasAnalyzer:
    """
    Analisador de viés de gênero em avaliações

    Implementa análise de distribuição para detectar viés
    """

    def __init__(self, threshold_vies: float = 0.05, alpha: float = 0.05):
        """
        Inicializa analisador

        Args:
            threshold_vies: Diferença mínima percentual para considerar viés (padrão: 5%)
            alpha: Nível de significância para testes estatísticos (padrão: 0.05)
        """
        self.threshold_vies = threshold_vies
        self.alpha = alpha

    def calcular_estatisticas(self, valores: List[float]) -> EstatisticasDistribuicao:
        """
        Calcula estatísticas descritivas

        Args:
            valores: Lista de valores

        Returns:
            Estatísticas da distribuição
        """
        if not valores:
            return EstatisticasDistribuicao(
                media=0, mediana=0, desvio_padrao=0,
                minimo=0, maximo=0, quartil_25=0, quartil_75=0,
                tamanho=0
            )

        arr = np.array(valores)

        return EstatisticasDistribuicao(
            media=float(np.mean(arr)),
            mediana=float(np.median(arr)),
            desvio_padrao=float(np.std(arr, ddof=1)),
            minimo=float(np.min(arr)),
            maximo=float(np.max(arr)),
            quartil_25=float(np.percentile(arr, 25)),
            quartil_75=float(np.percentile(arr, 75)),
            tamanho=len(valores)
        )

    def analisar_vies_genero(
        self,
        scores_por_genero: Dict[Genero, List[float]]
    ) -> ResultadoAnaliseVies:
        """
        Analisa viés de gênero comparando distribuições

        Args:
            scores_por_genero: Dicionário {Genero: [scores]}

        Returns:
            Resultado da análise de viés
        """
        # Extrai scores por gênero
        scores_f = scores_por_genero.get(Genero.FEMININO, [])
        scores_m = scores_por_genero.get(Genero.MASCULINO, [])

        # Calcula estatísticas
        stats_f = self.calcular_estatisticas(scores_f)
        stats_m = self.calcular_estatisticas(scores_m)

        # Calcula diferença nas médias
        diferenca_medias = stats_m.media - stats_f.media

        # Calcula diferença percentual
        if stats_f.media > 0:
            diferenca_percentual = (diferenca_medias / stats_f.media)
        else:
            diferenca_percentual = 0.0

        # Realiza teste t de Student para verificar significância
        if len(scores_f) > 1 and len(scores_m) > 1:
            t_statistic, p_value = stats.ttest_ind(scores_m, scores_f)
        else:
            p_value = 1.0

        # Detecta viés
        vies_detectado = abs(diferenca_percentual) > self.threshold_vies
        significancia_estatistica = p_value < self.alpha

        return ResultadoAnaliseVies(
            estatisticas_feminino=stats_f,
            estatisticas_masculino=stats_m,
            diferenca_medias=diferenca_medias,
            diferenca_percentual=diferenca_percentual,
            p_value=p_value,
            vies_detectado=vies_detectado,
            significancia_estatistica=significancia_estatistica
        )

    def gerar_relatorio_analise(
        self,
        resultado: ResultadoAnaliseVies
    ) -> str:
        """
        Gera relatório textual da análise

        Args:
            resultado: Resultado da análise

        Returns:
            Relatório em texto
        """
        relatorio = []
        relatorio.append("=" * 60)
        relatorio.append("ANÁLISE DE VIÉS DE GÊNERO")
        relatorio.append("=" * 60)
        relatorio.append("")

        relatorio.append("ESTATÍSTICAS - FEMININO:")
        relatorio.append(f"  Média: {resultado.estatisticas_feminino.media:.2f}")
        relatorio.append(f"  Mediana: {resultado.estatisticas_feminino.mediana:.2f}")
        relatorio.append(f"  Desvio Padrão: {resultado.estatisticas_feminino.desvio_padrao:.2f}")
        relatorio.append(f"  Tamanho: {resultado.estatisticas_feminino.tamanho}")
        relatorio.append("")

        relatorio.append("ESTATÍSTICAS - MASCULINO:")
        relatorio.append(f"  Média: {resultado.estatisticas_masculino.media:.2f}")
        relatorio.append(f"  Mediana: {resultado.estatisticas_masculino.mediana:.2f}")
        relatorio.append(f"  Desvio Padrão: {resultado.estatisticas_masculino.desvio_padrao:.2f}")
        relatorio.append(f"  Tamanho: {resultado.estatisticas_masculino.tamanho}")
        relatorio.append("")

        relatorio.append("ANÁLISE DE DIFERENÇA:")
        relatorio.append(f"  Diferença de Médias: {resultado.diferenca_medias:.2f}")
        relatorio.append(f"  Diferença Percentual: {resultado.diferenca_percentual*100:.2f}%")
        relatorio.append(f"  P-value: {resultado.p_value:.4f}")
        relatorio.append("")

        relatorio.append("CONCLUSÃO:")
        if resultado.vies_detectado and resultado.significancia_estatistica:
            relatorio.append("  ⚠️ VIÉS DETECTADO com significância estatística")
            if resultado.diferenca_medias > 0:
                relatorio.append("  → Homens recebem avaliações maiores que mulheres")
            else:
                relatorio.append("  → Mulheres recebem avaliações maiores que homens")
        elif resultado.vies_detectado:
            relatorio.append("  ⚠️ VIÉS DETECTADO (mas sem significância estatística)")
        else:
            relatorio.append("  ✓ Não foi detectado viés significativo")

        relatorio.append("=" * 60)

        return "\n".join(relatorio)


class BiasCorrector:
    """
    Corretor de viés usando reponderação (re-weighting)

    Implementa a técnica de reponderação descrita no framework
    """

    def __init__(self):
        """Inicializa corretor"""
        self.analyzer = BiasAnalyzer()

    def calcular_pesos_ajuste(
        self,
        scores_por_genero: Dict[Genero, List[float]]
    ) -> Tuple[float, float]:
        """
        Calcula pesos de ajuste para correção de viés

        Fórmula: Peso de Ajuste = Média dos Homens / Média das Mulheres

        Args:
            scores_por_genero: Scores agrupados por gênero

        Returns:
            Tupla (peso_feminino, peso_masculino)
        """
        scores_f = scores_por_genero.get(Genero.FEMININO, [])
        scores_m = scores_por_genero.get(Genero.MASCULINO, [])

        if not scores_f or not scores_m:
            return 1.0, 1.0

        media_f = np.mean(scores_f)
        media_m = np.mean(scores_m)

        if media_f == 0:
            return 1.0, 1.0

        # Peso de ajuste para mulheres
        peso_feminino = media_m / media_f

        # Peso para homens permanece 1.0 (baseline)
        peso_masculino = 1.0

        return peso_feminino, peso_masculino

    def aplicar_reponderacao(
        self,
        scores: Dict[str, float],
        generos: Dict[str, Genero],
        aplicar_correcao: bool = True
    ) -> ResultadoReponderacao:
        """
        Aplica reponderação para corrigir viés de gênero

        Args:
            scores: Dicionário {pessoa_id: score}
            generos: Dicionário {pessoa_id: genero}
            aplicar_correcao: Se True, aplica correção; se False, apenas analisa

        Returns:
            Resultado da reponderação
        """
        # Agrupa scores por gênero para análise
        scores_por_genero = {
            Genero.FEMININO: [],
            Genero.MASCULINO: []
        }

        for pessoa_id, score in scores.items():
            genero = generos.get(pessoa_id)
            if genero in [Genero.FEMININO, Genero.MASCULINO]:
                scores_por_genero[genero].append(score)

        # Analisa viés antes da correção
        analise_pre = self.analyzer.analisar_vies_genero(scores_por_genero)

        # Calcula pesos de ajuste
        peso_f, peso_m = self.calcular_pesos_ajuste(scores_por_genero)

        # Aplica ajuste se solicitado
        scores_ajustados = {}

        if aplicar_correcao and analise_pre.vies_detectado:
            for pessoa_id, score in scores.items():
                genero = generos.get(pessoa_id, Genero.NAO_INFORMADO)

                if genero == Genero.FEMININO:
                    # Aplica peso de ajuste
                    score_ajustado = min(10.0, score * peso_f)
                elif genero == Genero.MASCULINO:
                    score_ajustado = score * peso_m
                else:
                    # Outros gêneros não são ajustados
                    score_ajustado = score

                scores_ajustados[pessoa_id] = round(score_ajustado, 2)

            # Analisa viés após correção
            scores_por_genero_pos = {
                Genero.FEMININO: [],
                Genero.MASCULINO: []
            }

            for pessoa_id, score in scores_ajustados.items():
                genero = generos.get(pessoa_id)
                if genero in [Genero.FEMININO, Genero.MASCULINO]:
                    scores_por_genero_pos[genero].append(score)

            analise_pos = self.analyzer.analisar_vies_genero(scores_por_genero_pos)
        else:
            # Sem correção, scores permanecem iguais
            scores_ajustados = scores.copy()
            analise_pos = None

        return ResultadoReponderacao(
            peso_ajuste_feminino=peso_f,
            peso_ajuste_masculino=peso_m,
            scores_originais=scores.copy(),
            scores_ajustados=scores_ajustados,
            analise_pre_ajuste=analise_pre,
            analise_pos_ajuste=analise_pos
        )

    def gerar_relatorio_reponderacao(
        self,
        resultado: ResultadoReponderacao
    ) -> str:
        """
        Gera relatório da reponderação

        Args:
            resultado: Resultado da reponderação

        Returns:
            Relatório em texto
        """
        relatorio = []
        relatorio.append("=" * 60)
        relatorio.append("RELATÓRIO DE REPONDERAÇÃO")
        relatorio.append("=" * 60)
        relatorio.append("")

        relatorio.append("PESOS DE AJUSTE:")
        relatorio.append(f"  Feminino: {resultado.peso_ajuste_feminino:.4f}")
        relatorio.append(f"  Masculino: {resultado.peso_ajuste_masculino:.4f}")
        relatorio.append("")

        relatorio.append("ANÁLISE PRÉ-AJUSTE:")
        relatorio.append(self.analyzer.gerar_relatorio_analise(resultado.analise_pre_ajuste))
        relatorio.append("")

        if resultado.analise_pos_ajuste:
            relatorio.append("ANÁLISE PÓS-AJUSTE:")
            relatorio.append(self.analyzer.gerar_relatorio_analise(resultado.analise_pos_ajuste))
            relatorio.append("")

            # Compara resultados
            diff_pre = abs(resultado.analise_pre_ajuste.diferenca_percentual)
            diff_pos = abs(resultado.analise_pos_ajuste.diferenca_percentual)

            melhoria = (diff_pre - diff_pos) / diff_pre * 100 if diff_pre > 0 else 0

            relatorio.append("IMPACTO DA CORREÇÃO:")
            relatorio.append(f"  Redução do viés: {melhoria:.2f}%")

        return "\n".join(relatorio)
