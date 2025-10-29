"""
Gerador de dados mockados para Avaliação por Competências
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict

from src.models import Pessoa, Genero
from .competencias import (
    Competencia,
    TipoCompetencia,
    AvaliacaoCompetencias,
    AvaliacaoCompetenciaItem
)


class MockCompetenciasGenerator:
    """Gerador de avaliações por competências mockadas"""

    def __init__(self, seed: int = 42):
        """
        Inicializa gerador

        Args:
            seed: Semente para reprodutibilidade
        """
        random.seed(seed)

    def gerar_competencias_padrao(self) -> Dict[str, Competencia]:
        """
        Gera conjunto padrão de competências

        Returns:
            Dicionário de competências
        """
        competencias = {
            'C001': Competencia(
                id='C001',
                nome='Comunicação',
                descricao='Capacidade de se comunicar de forma clara e efetiva',
                tipo=TipoCompetencia.COMPORTAMENTAL,
                peso=0.9
            ),
            'C002': Competencia(
                id='C002',
                nome='Trabalho em Equipe',
                descricao='Habilidade de colaborar e trabalhar em equipe',
                tipo=TipoCompetencia.COMPORTAMENTAL,
                peso=0.9
            ),
            'C003': Competencia(
                id='C003',
                nome='Resolução de Problemas',
                descricao='Capacidade de identificar e resolver problemas complexos',
                tipo=TipoCompetencia.TECNICA,
                peso=1.0
            ),
            'C004': Competencia(
                id='C004',
                nome='Inovação e Criatividade',
                descricao='Capacidade de propor soluções inovadoras',
                tipo=TipoCompetencia.TECNICA,
                peso=0.8
            ),
            'C005': Competencia(
                id='C005',
                nome='Liderança',
                descricao='Capacidade de liderar e inspirar pessoas',
                tipo=TipoCompetencia.LIDERANCA,
                peso=1.0
            ),
            'C006': Competencia(
                id='C006',
                nome='Visão Estratégica',
                descricao='Capacidade de pensar estrategicamente',
                tipo=TipoCompetencia.ESTRATEGICA,
                peso=0.9
            ),
            'C007': Competencia(
                id='C007',
                nome='Adaptabilidade',
                descricao='Capacidade de se adaptar a mudanças',
                tipo=TipoCompetencia.COMPORTAMENTAL,
                peso=0.8
            ),
            'C008': Competencia(
                id='C008',
                nome='Gestão de Tempo',
                descricao='Capacidade de gerenciar tempo e prioridades',
                tipo=TipoCompetencia.COMPORTAMENTAL,
                peso=0.7
            ),
            'C009': Competencia(
                id='C009',
                nome='Conhecimento Técnico',
                descricao='Domínio técnico na área de atuação',
                tipo=TipoCompetencia.TECNICA,
                peso=1.0
            ),
            'C010': Competencia(
                id='C010',
                nome='Orientação para Resultados',
                descricao='Foco em entregar resultados de qualidade',
                tipo=TipoCompetencia.COMPORTAMENTAL,
                peso=0.9
            ),
        }

        return competencias

    def gerar_avaliacoes(
        self,
        pessoas: List[Pessoa],
        periodo: str = "2024-Q1",
        introducao_vies: bool = True,
        intensidade_vies: float = 0.15
    ) -> List[AvaliacaoCompetencias]:
        """
        Gera avaliações por competências para uma lista de pessoas

        Args:
            pessoas: Lista de pessoas a serem avaliadas
            periodo: Período da avaliação
            introducao_vies: Se True, introduz viés de gênero nas avaliações
            intensidade_vies: Intensidade do viés (0-1), onde valores maiores representam mais viés

        Returns:
            Lista de avaliações geradas
        """
        avaliacoes = []
        competencias = self.gerar_competencias_padrao()

        for i, pessoa in enumerate(pessoas):
            # Gera data de avaliação
            data_avaliacao = datetime.now() - timedelta(days=random.randint(1, 90))

            # Cria avaliação
            avaliacao = AvaliacaoCompetencias(
                id=f"AVAL-COMP-{i+1:04d}",
                pessoa_id=pessoa.id,
                avaliador_id=pessoa.gestor_id or "GESTOR-001",
                periodo=periodo,
                data_avaliacao=data_avaliacao,
                competencias=competencias,
                status="CONSENSO_REALIZADO"
            )

            # Gera avaliações para cada competência
            for comp_id, competencia in competencias.items():
                # Gera notas base (simulando desempenho real similar)
                nota_base = random.uniform(6.0, 9.5)

                # Autoavaliação (geralmente um pouco mais alta)
                nota_auto = min(10.0, nota_base + random.uniform(0, 0.8))

                # Nota do gestor (aqui introduzimos o viés se configurado)
                if introducao_vies and pessoa.genero == Genero.FEMININO:
                    # Aplica viés negativo para mulheres
                    reducao = random.uniform(0, intensidade_vies * 2)  # até 0.3 se intensidade = 0.15
                    nota_gestor = max(0, nota_base - reducao)
                elif introducao_vies and pessoa.genero == Genero.MASCULINO:
                    # Aplica pequeno viés positivo para homens
                    aumento = random.uniform(0, intensidade_vies)  # até 0.15
                    nota_gestor = min(10.0, nota_base + aumento)
                else:
                    # Sem viés
                    nota_gestor = nota_base + random.uniform(-0.3, 0.3)

                # Garante que as notas estejam no intervalo válido
                nota_gestor = max(0, min(10.0, nota_gestor))
                nota_auto = max(0, min(10.0, nota_auto))

                # Nota de consenso (média ponderada)
                nota_consenso = nota_auto * 0.3 + nota_gestor * 0.7

                # Cria item de avaliação
                item = AvaliacaoCompetenciaItem(
                    competencia_id=comp_id,
                    nota_autoavaliacao=round(nota_auto, 2),
                    nota_gestor=round(nota_gestor, 2),
                    nota_consenso=round(nota_consenso, 2),
                    observacoes=None
                )

                avaliacao.adicionar_item(item)

            # Gera plano de desenvolvimento baseado nas competências baixas
            competencias_baixas = avaliacao.obter_competencias_baixo_desempenho(threshold=7.0)
            if competencias_baixas:
                nomes_comp = [competencias[c].nome for c in competencias_baixas[:3]]
                avaliacao.plano_desenvolvimento = (
                    f"Desenvolver competências: {', '.join(nomes_comp)}"
                )

            avaliacoes.append(avaliacao)

        return avaliacoes

    def gerar_avaliacao_individual(
        self,
        pessoa: Pessoa,
        avaliador_id: str,
        periodo: str = "2024-Q1"
    ) -> AvaliacaoCompetencias:
        """
        Gera uma avaliação individual

        Args:
            pessoa: Pessoa a ser avaliada
            avaliador_id: ID do avaliador
            periodo: Período da avaliação

        Returns:
            Avaliação gerada
        """
        return self.gerar_avaliacoes([pessoa], periodo)[0]
