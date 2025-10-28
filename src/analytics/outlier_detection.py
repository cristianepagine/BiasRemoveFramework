"""
Detecção e Remoção de Outliers usando método Z-score
"""
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class ResultadoOutlier:
    """Resultado da análise de outliers"""
    indices_outliers: List[int]
    z_scores: np.ndarray
    media: float
    desvio_padrao: float
    threshold: float


class OutlierDetector:
    """
    Detector de outliers usando método Z-score

    O Z-score mede quantos desvios padrão um valor está distante da média.
    Valores com |Z| > threshold são considerados outliers.
    """

    def __init__(self, threshold: float = 3.0):
        """
        Inicializa detector

        Args:
            threshold: Limite para identificação de outliers (padrão: 3.0)
                      Valores comuns: 2.5, 3.0, 3.5
        """
        self.threshold = threshold

    def detectar_outliers(self, dados: List[float]) -> ResultadoOutlier:
        """
        Detecta outliers usando Z-score

        Fórmula: Z = (X - μ) / σ
        Onde:
        - X é o valor individual
        - μ é a média
        - σ é o desvio padrão

        Args:
            dados: Lista de valores numéricos

        Returns:
            ResultadoOutlier com índices dos outliers e informações estatísticas
        """
        if not dados:
            return ResultadoOutlier(
                indices_outliers=[],
                z_scores=np.array([]),
                media=0.0,
                desvio_padrao=0.0,
                threshold=self.threshold
            )

        # Converte para numpy array
        arr = np.array(dados)

        # Calcula média e desvio padrão
        media = np.mean(arr)
        desvio_padrao = np.std(arr, ddof=1)  # ddof=1 para amostra

        # Evita divisão por zero
        if desvio_padrao == 0:
            return ResultadoOutlier(
                indices_outliers=[],
                z_scores=np.zeros_like(arr),
                media=media,
                desvio_padrao=0.0,
                threshold=self.threshold
            )

        # Calcula Z-scores
        z_scores = (arr - media) / desvio_padrao

        # Identifica outliers (|Z| > threshold)
        indices_outliers = np.where(np.abs(z_scores) > self.threshold)[0].tolist()

        return ResultadoOutlier(
            indices_outliers=indices_outliers,
            z_scores=z_scores,
            media=media,
            desvio_padrao=desvio_padrao,
            threshold=self.threshold
        )

    def remover_outliers(
        self,
        dados: List[float],
        resultado: ResultadoOutlier = None
    ) -> Tuple[List[float], List[int]]:
        """
        Remove outliers dos dados

        Args:
            dados: Lista de valores
            resultado: Resultado da detecção (opcional, será calculado se não fornecido)

        Returns:
            Tupla (dados_limpos, indices_removidos)
        """
        if resultado is None:
            resultado = self.detectar_outliers(dados)

        # Remove outliers
        dados_limpos = [
            valor for i, valor in enumerate(dados)
            if i not in resultado.indices_outliers
        ]

        return dados_limpos, resultado.indices_outliers

    def detectar_e_remover(
        self,
        dados: List[float]
    ) -> Tuple[List[float], ResultadoOutlier]:
        """
        Detecta e remove outliers em uma única operação

        Args:
            dados: Lista de valores

        Returns:
            Tupla (dados_limpos, resultado_deteccao)
        """
        resultado = self.detectar_outliers(dados)
        dados_limpos, _ = self.remover_outliers(dados, resultado)

        return dados_limpos, resultado


class OutlierDetectorMultivariado:
    """
    Detector de outliers para dados multivariados

    Útil quando temos múltiplas avaliações por pessoa e queremos
    identificar outliers considerando todas as dimensões
    """

    def __init__(self, threshold: float = 3.0):
        """
        Inicializa detector

        Args:
            threshold: Limite para Z-score
        """
        self.threshold = threshold
        self.detector = OutlierDetector(threshold)

    def detectar_outliers_por_dimensao(
        self,
        dados: np.ndarray
    ) -> Dict[int, ResultadoOutlier]:
        """
        Detecta outliers em cada dimensão separadamente

        Args:
            dados: Array 2D onde cada linha é uma observação e cada coluna uma dimensão

        Returns:
            Dicionário {dimensao_index: ResultadoOutlier}
        """
        if dados.ndim != 2:
            raise ValueError("Dados devem ser um array 2D")

        resultados = {}

        # Para cada dimensão (coluna)
        for dim in range(dados.shape[1]):
            valores_dim = dados[:, dim].tolist()
            resultado = self.detector.detectar_outliers(valores_dim)
            resultados[dim] = resultado

        return resultados

    def detectar_outliers_globais(
        self,
        dados: np.ndarray,
        min_dimensoes_outlier: int = 2
    ) -> List[int]:
        """
        Detecta observações que são outliers em múltiplas dimensões

        Args:
            dados: Array 2D
            min_dimensoes_outlier: Número mínimo de dimensões onde deve ser outlier

        Returns:
            Lista de índices de outliers globais
        """
        resultados_dim = self.detectar_outliers_por_dimensao(dados)

        # Conta em quantas dimensões cada observação é outlier
        num_obs = dados.shape[0]
        contagem_outlier = {i: 0 for i in range(num_obs)}

        for resultado in resultados_dim.values():
            for idx in resultado.indices_outliers:
                contagem_outlier[idx] += 1

        # Identifica outliers globais
        outliers_globais = [
            idx for idx, count in contagem_outlier.items()
            if count >= min_dimensoes_outlier
        ]

        return outliers_globais


def aplicar_deteccao_outliers_avaliacoes(
    avaliacoes_scores: Dict[str, float],
    threshold: float = 3.0
) -> Tuple[Dict[str, float], List[str]]:
    """
    Aplica detecção de outliers em scores de avaliações

    Args:
        avaliacoes_scores: Dicionário {pessoa_id: score}
        threshold: Limite de Z-score

    Returns:
        Tupla (scores_limpos, ids_removidos)
    """
    detector = OutlierDetector(threshold)

    # Extrai valores e IDs
    ids = list(avaliacoes_scores.keys())
    scores = list(avaliacoes_scores.values())

    # Detecta outliers
    resultado = detector.detectar_outliers(scores)

    # Remove outliers
    scores_limpos = {}
    ids_removidos = []

    for i, (pessoa_id, score) in enumerate(avaliacoes_scores.items()):
        if i in resultado.indices_outliers:
            ids_removidos.append(pessoa_id)
        else:
            scores_limpos[pessoa_id] = score

    return scores_limpos, ids_removidos
