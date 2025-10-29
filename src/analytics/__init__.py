"""
Módulo de analytics - detecção de outliers, correção de viés e ranking
"""
from .outlier_detection import (
    OutlierDetector,
    OutlierDetectorMultivariado,
    ResultadoOutlier,
    aplicar_deteccao_outliers_avaliacoes
)
from .bias_correction import (
    BiasAnalyzer,
    BiasCorrector,
    ResultadoAnaliseVies,
    ResultadoReponderacao,
    EstatisticasDistribuicao
)
from .ranking import (
    RankingCalculator,
    ResultadoRanking,
    ScorePessoa,
    CriterioAvaliacao,
    combinar_avaliacoes_em_scores
)

__all__ = [
    'OutlierDetector',
    'OutlierDetectorMultivariado',
    'ResultadoOutlier',
    'aplicar_deteccao_outliers_avaliacoes',
    'BiasAnalyzer',
    'BiasCorrector',
    'ResultadoAnaliseVies',
    'ResultadoReponderacao',
    'EstatisticasDistribuicao',
    'RankingCalculator',
    'ResultadoRanking',
    'ScorePessoa',
    'CriterioAvaliacao',
    'combinar_avaliacoes_em_scores'
]
