"""
Gerador de dados mockados para Avaliação 360 Graus
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict

from src.models import Pessoa, Genero
from .avaliacao_360 import (
    Questao360,
    Resposta360,
    Avaliacao360,
    TipoAvaliador
)


class Mock360Generator:
    """Gerador de avaliações 360 graus mockadas"""

    def __init__(self, seed: int = 42):
        """
        Inicializa gerador

        Args:
            seed: Semente para reprodutibilidade
        """
        random.seed(seed)

    def gerar_questoes_padrao(self) -> Dict[str, Questao360]:
        """
        Gera conjunto padrão de questões

        Returns:
            Dicionário de questões
        """
        questoes = {
            'Q001': Questao360(
                id='Q001',
                texto='Demonstra habilidades eficazes de comunicação',
                categoria='Comunicação',
                peso=1.0
            ),
            'Q002': Questao360(
                id='Q002',
                texto='Escuta ativamente e considera diferentes perspectivas',
                categoria='Comunicação',
                peso=0.9
            ),
            'Q003': Questao360(
                id='Q003',
                texto='Trabalha bem em equipe e colabora com colegas',
                categoria='Trabalho em Equipe',
                peso=1.0
            ),
            'Q004': Questao360(
                id='Q004',
                texto='Apoia e motiva membros da equipe',
                categoria='Trabalho em Equipe',
                peso=0.9
            ),
            'Q005': Questao360(
                id='Q005',
                texto='Demonstra capacidade de liderança',
                categoria='Liderança',
                peso=1.0
            ),
            'Q006': Questao360(
                id='Q006',
                texto='Toma decisões eficazes e assume responsabilidade',
                categoria='Liderança',
                peso=1.0
            ),
            'Q007': Questao360(
                id='Q007',
                texto='Resolve problemas de forma criativa e eficaz',
                categoria='Resolução de Problemas',
                peso=1.0
            ),
            'Q008': Questao360(
                id='Q008',
                texto='Adapta-se bem a mudanças e novos desafios',
                categoria='Adaptabilidade',
                peso=0.8
            ),
            'Q009': Questao360(
                id='Q009',
                texto='Demonstra integridade e comportamento ético',
                categoria='Ética e Valores',
                peso=1.0
            ),
            'Q010': Questao360(
                id='Q010',
                texto='Foca em resultados e entrega com qualidade',
                categoria='Orientação para Resultados',
                peso=1.0
            ),
            'Q011': Questao360(
                id='Q011',
                texto='Gerencia tempo e prioridades efetivamente',
                categoria='Gestão',
                peso=0.8
            ),
            'Q012': Questao360(
                id='Q012',
                texto='Demonstra visão estratégica e pensamento a longo prazo',
                categoria='Visão Estratégica',
                peso=0.9
            ),
        }

        return questoes

    def gerar_avaliacoes(
        self,
        pessoas: List[Pessoa],
        todas_pessoas: List[Pessoa],
        periodo: str = "2024-Q1",
        introducao_vies: bool = True,
        intensidade_vies: float = 0.20
    ) -> List[Avaliacao360]:
        """
        Gera avaliações 360 graus para uma lista de pessoas

        Args:
            pessoas: Lista de pessoas a serem avaliadas
            todas_pessoas: Lista completa de pessoas (para selecionar avaliadores)
            periodo: Período da avaliação
            introducao_vies: Se True, introduz viés de gênero
            intensidade_vies: Intensidade do viés (0-1)

        Returns:
            Lista de avaliações geradas
        """
        avaliacoes = []
        questoes = self.gerar_questoes_padrao()

        for i, pessoa in enumerate(pessoas):
            # Gera datas
            data_inicio = datetime.now() - timedelta(days=random.randint(30, 120))
            data_fim = data_inicio + timedelta(days=random.randint(15, 30))

            # Cria avaliação
            avaliacao = Avaliacao360(
                id=f"AVAL-360-{i+1:04d}",
                pessoa_id=pessoa.id,
                periodo=periodo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                questoes=questoes,
                status="FEEDBACK_FORNECIDO"
            )

            # Seleciona avaliadores
            avaliadores = self._selecionar_avaliadores(pessoa, todas_pessoas)

            # Gera respostas para cada questão de cada avaliador
            for questao_id in questoes.keys():
                # Autoavaliação
                nota_auto = random.uniform(7.0, 9.5)
                avaliacao.adicionar_resposta(
                    Resposta360(
                        questao_id=questao_id,
                        avaliador_id=pessoa.id,
                        tipo_avaliador=TipoAvaliador.AUTOAVALIACAO,
                        nota=round(nota_auto, 2),
                        comentario=None
                    )
                )

                # Respostas dos outros avaliadores
                for avaliador_id, tipo_avaliador in avaliadores:
                    nota_base = random.uniform(6.0, 9.0)

                    # Introduz viés se configurado
                    if introducao_vies:
                        if pessoa.genero == Genero.FEMININO:
                            # Viés negativo para mulheres
                            # O viés é mais forte em categorias de liderança
                            categoria = questoes[questao_id].categoria
                            if categoria in ['Liderança', 'Visão Estratégica']:
                                reducao = random.uniform(0, intensidade_vies * 3)
                            else:
                                reducao = random.uniform(0, intensidade_vies * 1.5)
                            nota_final = max(0, nota_base - reducao)

                        elif pessoa.genero == Genero.MASCULINO:
                            # Viés positivo leve para homens
                            aumento = random.uniform(0, intensidade_vies)
                            nota_final = min(10.0, nota_base + aumento)
                        else:
                            nota_final = nota_base
                    else:
                        nota_final = nota_base

                    # Garante intervalo válido
                    nota_final = max(0, min(10.0, nota_final))

                    avaliacao.adicionar_resposta(
                        Resposta360(
                            questao_id=questao_id,
                            avaliador_id=avaliador_id,
                            tipo_avaliador=tipo_avaliador,
                            nota=round(nota_final, 2),
                            comentario=None
                        )
                    )

            # Gera relatório de feedback
            pontos_fortes = avaliacao.identificar_pontos_fortes()
            pontos_dev = avaliacao.identificar_pontos_desenvolvimento()

            avaliacao.relatorio_feedback = (
                f"Pontos Fortes: {', '.join(pontos_fortes[:3]) if pontos_fortes else 'N/A'}\n"
                f"Desenvolvimento: {', '.join(pontos_dev[:3]) if pontos_dev else 'N/A'}"
            )

            if pontos_dev:
                avaliacao.plano_melhoria = (
                    f"Focar no desenvolvimento de: {', '.join(pontos_dev[:2])}"
                )

            avaliacoes.append(avaliacao)

        return avaliacoes

    def _selecionar_avaliadores(
        self,
        pessoa: Pessoa,
        todas_pessoas: List[Pessoa]
    ) -> List[tuple]:
        """
        Seleciona avaliadores para uma pessoa

        Args:
            pessoa: Pessoa a ser avaliada
            todas_pessoas: Lista completa de pessoas

        Returns:
            Lista de tuplas (avaliador_id, tipo_avaliador)
        """
        avaliadores = []

        # Filtra pessoas elegíveis
        elegíveis = [p for p in todas_pessoas if p.id != pessoa.id]

        if not elegíveis:
            # Se não há outras pessoas, usa pessoa genérica
            return [("AVALIADOR-001", TipoAvaliador.SUPERIOR)]

        # Superior (gestor)
        if pessoa.gestor_id:
            avaliadores.append((pessoa.gestor_id, TipoAvaliador.SUPERIOR))
        else:
            # Seleciona alguém de nível superior
            superiores = [
                p for p in elegíveis
                if p.nivel_hierarquico.value > pessoa.nivel_hierarquico.value
            ]
            if superiores:
                superior = random.choice(superiores)
                avaliadores.append((superior.id, TipoAvaliador.SUPERIOR))

        # Pares (2-3 colegas do mesmo nível)
        pares = [
            p for p in elegíveis
            if p.nivel_hierarquico == pessoa.nivel_hierarquico
            and p.departamento == pessoa.departamento
        ]
        num_pares = min(3, len(pares))
        if num_pares > 0:
            pares_selecionados = random.sample(pares, num_pares)
            avaliadores.extend([
                (p.id, TipoAvaliador.PAR) for p in pares_selecionados
            ])

        # Subordinados (se aplicável)
        subordinados = [
            p for p in elegíveis
            if p.gestor_id == pessoa.id
        ]
        num_subordinados = min(2, len(subordinados))
        if num_subordinados > 0:
            subordinados_selecionados = random.sample(subordinados, num_subordinados)
            avaliadores.extend([
                (p.id, TipoAvaliador.SUBORDINADO) for p in subordinados_selecionados
            ])

        # Cliente interno (1-2 pessoas de outros departamentos)
        clientes = [
            p for p in elegíveis
            if p.departamento != pessoa.departamento
        ]
        num_clientes = min(2, len(clientes))
        if num_clientes > 0:
            clientes_selecionados = random.sample(clientes, num_clientes)
            avaliadores.extend([
                (p.id, TipoAvaliador.CLIENTE_INTERNO) for p in clientes_selecionados
            ])

        # Garante pelo menos alguns avaliadores
        if len(avaliadores) < 3:
            adicionais_necessarios = 3 - len(avaliadores)
            disponiveis = [
                p for p in elegíveis
                if p.id not in [a[0] for a in avaliadores]
            ]
            if disponiveis:
                num_adicionais = min(adicionais_necessarios, len(disponiveis))
                adicionais = random.sample(disponiveis, num_adicionais)
                avaliadores.extend([
                    (p.id, TipoAvaliador.PAR) for p in adicionais
                ])

        return avaliadores
