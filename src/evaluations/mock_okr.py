"""
Gerador de dados mockados para Avaliação por OKRs
"""
import random
from datetime import datetime, timedelta
from typing import List

from src.models import Pessoa, Genero, NivelHierarquico
from .okr import (
    AvaliacaoOKR,
    Objetivo,
    ResultadoChave,
    StatusOKR,
    NivelOKR
)


class MockOKRGenerator:
    """Gerador de avaliações de OKR mockadas"""

    def __init__(self, seed: int = 42):
        """
        Inicializa gerador

        Args:
            seed: Semente para reprodutibilidade
        """
        random.seed(seed)

    def gerar_avaliacoes(
        self,
        pessoas: List[Pessoa],
        periodo: str = "2024-Q1",
        introducao_vies: bool = True,
        intensidade_vies: float = 0.15
    ) -> List[AvaliacaoOKR]:
        """
        Gera avaliações de OKR para uma lista de pessoas

        Args:
            pessoas: Lista de pessoas
            periodo: Período da avaliação
            introducao_vies: Se True, introduz viés
            intensidade_vies: Intensidade do viés (0-1)

        Returns:
            Lista de avaliações
        """
        avaliacoes = []

        # Define datas do período
        ano, trimestre = periodo.split('-')
        trimestre_num = int(trimestre[1])
        mes_inicio = (trimestre_num - 1) * 3 + 1

        data_inicio = datetime(int(ano), mes_inicio, 1)
        data_fim = data_inicio + timedelta(days=90)

        for i, pessoa in enumerate(pessoas):
            # Cria avaliação
            avaliacao = AvaliacaoOKR(
                id=f"AVAL-OKR-{i+1:04d}",
                pessoa_id=pessoa.id,
                periodo=periodo,
                data_criacao=data_inicio,
                data_ultima_atualizacao=datetime.now(),
                status="CONCLUIDO"
            )

            # Número de objetivos baseado no nível hierárquico
            num_objetivos = self._determinar_num_objetivos(pessoa.nivel_hierarquico)

            # Gera objetivos
            for j in range(num_objetivos):
                objetivo = self._gerar_objetivo(
                    pessoa,
                    j,
                    data_inicio,
                    data_fim,
                    introducao_vies,
                    intensidade_vies
                )
                avaliacao.adicionar_objetivo(objetivo)

            # Gera insights baseado no desempenho
            score = avaliacao.calcular_score_geral()
            if score >= 0.7:
                avaliacao.adicionar_insight("Excelente performance no período")
            elif score >= 0.5:
                avaliacao.adicionar_insight("Performance adequada, com espaço para melhoria")
            else:
                avaliacao.adicionar_insight("Performance abaixo do esperado, requer atenção")

            if avaliacao.obter_objetivos_em_risco():
                avaliacao.adicionar_insight("Alguns objetivos necessitam de ajuste de estratégia")

            # Define próximos passos
            if score < 0.7:
                avaliacao.proximos_passos = (
                    "Revisar estratégias dos objetivos com menor performance. "
                    "Alinhar recursos e prioridades."
                )
            else:
                avaliacao.proximos_passos = (
                    "Manter foco nas iniciativas atuais. "
                    "Preparar OKRs para o próximo ciclo."
                )

            avaliacoes.append(avaliacao)

        return avaliacoes

    def _determinar_num_objetivos(self, nivel: NivelHierarquico) -> int:
        """Determina número de objetivos baseado no nível"""
        if nivel.value >= 7:  # Gerente+
            return random.randint(3, 5)
        elif nivel.value >= 4:  # Senior+
            return random.randint(2, 4)
        else:
            return random.randint(1, 3)

    def _gerar_objetivo(
        self,
        pessoa: Pessoa,
        indice: int,
        data_inicio: datetime,
        data_fim: datetime,
        introducao_vies: bool,
        intensidade_vies: float
    ) -> Objetivo:
        """Gera um objetivo individual"""

        # Templates de objetivos por área
        templates_objetivos = [
            "Aumentar a eficiência operacional do time",
            "Melhorar a qualidade das entregas",
            "Expandir conhecimento técnico da equipe",
            "Fortalecer relacionamento com stakeholders",
            "Implementar processos de melhoria contínua",
            "Desenvolver soluções inovadoras",
            "Otimizar recursos e reduzir custos",
            "Aumentar satisfação do cliente interno",
        ]

        objetivo = Objetivo(
            id=f"{pessoa.id}-OBJ-{indice+1}",
            descricao=random.choice(templates_objetivos),
            nivel=self._determinar_nivel_okr(pessoa.nivel_hierarquico),
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=StatusOKR.CONCLUIDO
        )

        # Gera 2-4 resultados-chave por objetivo
        num_krs = random.randint(2, 4)
        for k in range(num_krs):
            kr = self._gerar_resultado_chave(
                objetivo.id,
                k,
                pessoa,
                introducao_vies,
                intensidade_vies
            )
            objetivo.adicionar_resultado_chave(kr)

        return objetivo

    def _gerar_resultado_chave(
        self,
        objetivo_id: str,
        indice: int,
        pessoa: Pessoa,
        introducao_vies: bool,
        intensidade_vies: float
    ) -> ResultadoChave:
        """Gera um resultado-chave"""

        # Templates de KRs
        templates_kr = [
            ("Aumentar métrica de performance de {inicial}% para {final}%", "%"),
            ("Reduzir tempo de resposta de {inicial}h para {final}h", "horas"),
            ("Completar {final} entregas de alta qualidade", "unidades"),
            ("Atingir score de satisfação de {final}%", "%"),
            ("Implementar {final} melhorias no processo", "unidades"),
            ("Reduzir custos em {final}%", "%"),
            ("Treinar {final} pessoas em novas competências", "pessoas"),
            ("Alcançar {final}% de adoção da nova ferramenta", "%"),
        ]

        template, unidade = random.choice(templates_kr)

        # Define metas baseadas na unidade
        if unidade == "%":
            meta_inicial = random.uniform(40, 70)
            meta_final = random.uniform(meta_inicial + 15, 95)
        elif unidade == "horas":
            meta_inicial = random.uniform(8, 24)
            meta_final = random.uniform(2, meta_inicial - 2)
        elif unidade == "unidades" or unidade == "pessoas":
            meta_inicial = 0
            meta_final = random.randint(5, 20)
        else:
            meta_inicial = random.uniform(50, 70)
            meta_final = random.uniform(meta_inicial + 10, 95)

        # Calcula valor atual (progresso)
        # Aqui introduzimos o viés
        progresso_base = random.uniform(0.5, 0.95)

        if introducao_vies:
            if pessoa.genero == Genero.FEMININO:
                # Mulheres tendem a reportar progresso mais conservador
                # E avaliadores podem subestimar seu progresso
                reducao = random.uniform(0, intensidade_vies)
                progresso_final = max(0.3, progresso_base - reducao)
            elif pessoa.genero == Genero.MASCULINO:
                # Homens tendem a reportar progresso mais otimista
                # E avaliadores podem superestimar
                aumento = random.uniform(0, intensidade_vies * 0.5)
                progresso_final = min(1.0, progresso_base + aumento)
            else:
                progresso_final = progresso_base
        else:
            progresso_final = progresso_base

        # Calcula valor atual baseado no progresso
        if unidade == "horas":
            # Para horas, menos é melhor
            valor_atual = meta_inicial - (meta_inicial - meta_final) * progresso_final
        else:
            valor_atual = meta_inicial + (meta_final - meta_inicial) * progresso_final

        # Formata descrição
        descricao = template.format(
            inicial=int(meta_inicial),
            final=int(meta_final)
        )

        # Determina status
        if progresso_final >= 0.7:
            status = StatusOKR.CONCLUIDO
        elif progresso_final >= 0.4:
            status = StatusOKR.EM_PROGRESSO
        else:
            status = StatusOKR.ATRASADO

        kr = ResultadoChave(
            id=f"{objetivo_id}-KR-{indice+1}",
            descricao=descricao,
            meta_inicial=round(meta_inicial, 2),
            meta_final=round(meta_final, 2),
            valor_atual=round(valor_atual, 2),
            unidade=unidade,
            peso=1.0,
            status=status
        )

        # Adiciona algumas evidências
        if progresso_final > 0.5:
            kr.adicionar_evidencia(f"Check-in mensal mostrando progresso")
            if progresso_final > 0.7:
                kr.adicionar_evidencia(f"Objetivo alcançado conforme planejado")

        return kr

    def _determinar_nivel_okr(self, nivel_hierarquico: NivelHierarquico) -> NivelOKR:
        """Determina nível do OKR baseado no nível hierárquico"""
        if nivel_hierarquico.value >= 8:  # Diretor+
            return NivelOKR.EMPRESA
        elif nivel_hierarquico.value >= 6:  # Coordenador+
            return NivelOKR.DEPARTAMENTO
        elif nivel_hierarquico.value >= 4:  # Senior+
            return NivelOKR.TIME
        else:
            return NivelOKR.INDIVIDUAL
