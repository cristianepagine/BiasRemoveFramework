"""
Gerador de dados mockados para Nine Box
"""
import random
from datetime import datetime
from typing import List, Dict, Optional

from src.models import Pessoa, Genero, NivelHierarquico
from .nine_box import (
    AvaliacaoNineBox,
    PosicaoNineBox,
    CategoriaDesempenho,
    CategoriaPotencial,
    calcular_categoria,
    determinar_quadrante,
    DESCRICOES_QUADRANTES
)
from .competencias import AvaliacaoCompetencias
from .avaliacao_360 import Avaliacao360
from .okr import AvaliacaoOKR


class MockNineBoxGenerator:
    """Gerador de avaliações Nine Box mockadas"""

    def __init__(self, seed: int = 42):
        """
        Inicializa gerador

        Args:
            seed: Semente para reprodutibilidade
        """
        random.seed(seed)

    def gerar_avaliacao(
        self,
        pessoas: List[Pessoa],
        periodo: str = "2024-Q1",
        avaliacoes_competencias: Optional[List[AvaliacaoCompetencias]] = None,
        avaliacoes_360: Optional[List[Avaliacao360]] = None,
        avaliacoes_okr: Optional[List[AvaliacaoOKR]] = None,
        introducao_vies: bool = True,
        intensidade_vies: float = 0.10
    ) -> AvaliacaoNineBox:
        """
        Gera avaliação Nine Box baseada em outras avaliações

        Args:
            pessoas: Lista de pessoas
            periodo: Período da avaliação
            avaliacoes_competencias: Avaliações de competências (opcional)
            avaliacoes_360: Avaliações 360 (opcional)
            avaliacoes_okr: Avaliações OKR (opcional)
            introducao_vies: Se True, introduz viés
            intensidade_vies: Intensidade do viés

        Returns:
            Avaliação Nine Box
        """
        # Cria dicionários de lookup para as avaliações
        comp_dict = {}
        if avaliacoes_competencias:
            comp_dict = {av.pessoa_id: av for av in avaliacoes_competencias}

        av360_dict = {}
        if avaliacoes_360:
            av360_dict = {av.pessoa_id: av for av in avaliacoes_360}

        okr_dict = {}
        if avaliacoes_okr:
            okr_dict = {av.pessoa_id: av for av in avaliacoes_okr}

        # Cria avaliação Nine Box
        avaliacao = AvaliacaoNineBox(
            id=f"AVAL-9BOX-{periodo}",
            periodo=periodo,
            data_avaliacao=datetime.now(),
            criterios_desempenho=[
                "Resultados de OKRs",
                "Avaliação de Competências",
                "Feedback 360 Graus",
                "Entregas e Qualidade"
            ],
            criterios_potencial=[
                "Capacidade de Aprendizado",
                "Adaptabilidade",
                "Liderança Demonstrada",
                "Visão Estratégica",
                "Potencial de Crescimento"
            ],
            comite_avaliadores=["COMITE-001", "COMITE-002", "COMITE-003"],
            status="CONCLUIDO"
        )

        # Gera posição para cada pessoa
        for pessoa in pessoas:
            # Calcula score de desempenho baseado nas avaliações disponíveis
            score_desempenho = self._calcular_score_desempenho(
                pessoa,
                comp_dict.get(pessoa.id),
                av360_dict.get(pessoa.id),
                okr_dict.get(pessoa.id)
            )

            # Calcula score de potencial
            score_potencial = self._calcular_score_potencial(
                pessoa,
                comp_dict.get(pessoa.id),
                av360_dict.get(pessoa.id),
                okr_dict.get(pessoa.id)
            )

            # Introduz viés se configurado
            if introducao_vies:
                if pessoa.genero == Genero.FEMININO:
                    # Viés negativo no potencial (mais comum em avaliações de potencial)
                    reducao_potencial = random.uniform(0, intensidade_vies * 3)
                    score_potencial = max(0, score_potencial - reducao_potencial)

                    # Leve viés negativo no desempenho também
                    reducao_desempenho = random.uniform(0, intensidade_vies)
                    score_desempenho = max(0, score_desempenho - reducao_desempenho)

                elif pessoa.genero == Genero.MASCULINO:
                    # Viés positivo leve
                    aumento_potencial = random.uniform(0, intensidade_vies * 1.5)
                    score_potencial = min(10.0, score_potencial + aumento_potencial)

            # Garante limites
            score_desempenho = max(0, min(10.0, score_desempenho))
            score_potencial = max(0, min(10.0, score_potencial))

            # Determina categorias
            cat_desempenho = calcular_categoria(score_desempenho, (6.0, 8.0))
            cat_potencial = calcular_categoria(score_potencial, (6.0, 8.0))

            # Converte para tipos corretos
            if cat_desempenho.value == "Baixo":
                cat_desempenho = CategoriaDesempenho.BAIXO
            elif cat_desempenho.value == "Médio":
                cat_desempenho = CategoriaDesempenho.MEDIO
            else:
                cat_desempenho = CategoriaDesempenho.ALTO

            if cat_potencial.value == "Baixo":
                cat_potencial = CategoriaPotencial.BAIXO
            elif cat_potencial.value == "Médio":
                cat_potencial = CategoriaPotencial.MEDIO
            else:
                cat_potencial = CategoriaPotencial.ALTO

            # Determina quadrante
            quadrante = determinar_quadrante(cat_desempenho, cat_potencial)

            # Cria posição
            posicao = PosicaoNineBox(
                pessoa_id=pessoa.id,
                desempenho=cat_desempenho,
                potencial=cat_potencial,
                score_desempenho=round(score_desempenho, 2),
                score_potencial=round(score_potencial, 2),
                quadrante=quadrante,
                notas=f"Avaliado em {periodo}"
            )

            avaliacao.adicionar_posicao(posicao)

            # Gera plano de ação baseado no quadrante
            desc_quadrante = DESCRICOES_QUADRANTES.get(quadrante, {})
            plano = desc_quadrante.get("acao", "Manter desenvolvimento contínuo")
            avaliacao.adicionar_plano_acao(pessoa.id, plano)

        return avaliacao

    def _calcular_score_desempenho(
        self,
        pessoa: Pessoa,
        aval_comp: Optional[AvaliacaoCompetencias],
        aval_360: Optional[Avaliacao360],
        aval_okr: Optional[AvaliacaoOKR]
    ) -> float:
        """
        Calcula score de desempenho baseado nas avaliações disponíveis

        Args:
            pessoa: Pessoa avaliada
            aval_comp: Avaliação de competências
            aval_360: Avaliação 360
            aval_okr: Avaliação OKR

        Returns:
            Score de desempenho (0-10)
        """
        scores = []
        pesos = []

        # Avaliação de Competências (peso 1.0)
        if aval_comp:
            score = aval_comp.calcular_media_final()
            scores.append(score)
            pesos.append(1.0)

        # Avaliação 360 (peso 0.9)
        if aval_360:
            score = aval_360.calcular_media_geral()
            scores.append(score)
            pesos.append(0.9)

        # OKR (peso 1.2 - mais importante)
        if aval_okr:
            score = aval_okr.calcular_score_geral() * 10  # Converte de 0-1 para 0-10
            scores.append(score)
            pesos.append(1.2)

        # Se não houver avaliações, gera score aleatório
        if not scores:
            return random.uniform(6.0, 9.0)

        # Calcula média ponderada
        soma_ponderada = sum(s * p for s, p in zip(scores, pesos))
        soma_pesos = sum(pesos)

        return soma_ponderada / soma_pesos

    def _calcular_score_potencial(
        self,
        pessoa: Pessoa,
        aval_comp: Optional[AvaliacaoCompetencias],
        aval_360: Optional[Avaliacao360],
        aval_okr: Optional[AvaliacaoOKR]
    ) -> float:
        """
        Calcula score de potencial

        O potencial é baseado em:
        - Competências comportamentais e de liderança
        - Feedback 360 em categorias de liderança e visão
        - Capacidade de atingir OKRs desafiadores
        - Fatores como tempo na empresa, idade, nível hierárquico

        Args:
            pessoa: Pessoa avaliada
            aval_comp: Avaliação de competências
            aval_360: Avaliação 360
            aval_okr: Avaliação OKR

        Returns:
            Score de potencial (0-10)
        """
        score_base = random.uniform(6.0, 8.5)

        # Ajusta baseado no nível hierárquico
        # Pessoas em níveis mais baixos têm mais "potencial" de crescimento
        if pessoa.nivel_hierarquico.value <= 3:  # Junior/Pleno
            score_base += random.uniform(0, 1.0)
        elif pessoa.nivel_hierarquico.value >= 7:  # Gerente+
            score_base -= random.uniform(0, 0.5)

        # Ajusta baseado na idade (mais jovem = mais potencial percebido)
        if pessoa.idade < 30:
            score_base += random.uniform(0, 0.8)
        elif pessoa.idade > 50:
            score_base -= random.uniform(0, 0.8)

        # Ajusta baseado no tempo no cargo (menos tempo = mais potencial de mudança)
        if pessoa.tempo_cargo_atual < 18:  # Menos de 1.5 anos
            score_base += random.uniform(0, 0.5)

        # Se houver avaliação 360, usa categorias de liderança e visão
        if aval_360:
            medias_cat = aval_360.calcular_media_por_categoria()
            categorias_potencial = ['Liderança', 'Visão Estratégica', 'Adaptabilidade']

            scores_potencial = [
                medias_cat.get(cat, 7.0)
                for cat in categorias_potencial
                if cat in medias_cat
            ]

            if scores_potencial:
                media_potencial = sum(scores_potencial) / len(scores_potencial)
                score_base = score_base * 0.6 + media_potencial * 0.4

        # Se houver avaliação de competências, usa competências de liderança
        if aval_comp:
            # Procura competências relacionadas a liderança e estratégia
            competencias_lideranca = ['C005', 'C006']  # Liderança e Visão Estratégica
            scores_comp = []

            for item in aval_comp.itens_avaliacao:
                if item.competencia_id in competencias_lideranca:
                    nota = item.nota_consenso or item.nota_gestor or item.nota_autoavaliacao
                    if nota:
                        scores_comp.append(nota)

            if scores_comp:
                media_comp = sum(scores_comp) / len(scores_comp)
                score_base = score_base * 0.7 + media_comp * 0.3

        # Garante limites
        return max(0, min(10.0, score_base))
