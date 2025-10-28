"""
Gerador de dados mockados para testes do framework
"""
import random
from datetime import datetime, timedelta
from typing import List
from faker import Faker

from src.models import Pessoa, Genero, NivelHierarquico


class MockDataGenerator:
    """Classe para gerar dados mockados"""

    def __init__(self, seed: int = 42):
        """
        Inicializa o gerador de dados

        Args:
            seed: Semente para reprodutibilidade
        """
        self.fake = Faker('pt_BR')
        Faker.seed(seed)
        random.seed(seed)

    def gerar_pessoas(
        self,
        quantidade: int = 50,
        distribuicao_genero: dict = None
    ) -> List[Pessoa]:
        """
        Gera uma lista de pessoas com dados mockados

        Args:
            quantidade: Número de pessoas a gerar
            distribuicao_genero: Dicionário com distribuição de gênero
                                Exemplo: {Genero.FEMININO: 0.5, Genero.MASCULINO: 0.5}

        Returns:
            Lista de pessoas geradas
        """
        if distribuicao_genero is None:
            distribuicao_genero = {
                Genero.FEMININO: 0.45,
                Genero.MASCULINO: 0.50,
                Genero.OUTRO: 0.03,
                Genero.NAO_INFORMADO: 0.02
            }

        pessoas = []

        # Definições de cargos por nível
        cargos_por_nivel = {
            NivelHierarquico.ESTAGIARIO: ["Estagiário"],
            NivelHierarquico.JUNIOR: ["Analista Junior", "Desenvolvedor Junior", "Assistente"],
            NivelHierarquico.PLENO: ["Analista Pleno", "Desenvolvedor Pleno", "Consultor Pleno"],
            NivelHierarquico.SENIOR: ["Analista Senior", "Desenvolvedor Senior", "Consultor Senior"],
            NivelHierarquico.ESPECIALISTA: ["Especialista", "Arquiteto", "Tech Lead"],
            NivelHierarquico.COORDENADOR: ["Coordenador"],
            NivelHierarquico.GERENTE: ["Gerente"],
            NivelHierarquico.DIRETOR: ["Diretor"],
            NivelHierarquico.VP: ["Vice-Presidente"],
            NivelHierarquico.C_LEVEL: ["CEO", "CTO", "CFO", "COO"]
        }

        departamentos = [
            "Tecnologia",
            "Recursos Humanos",
            "Financeiro",
            "Comercial",
            "Marketing",
            "Operações",
            "Produtos"
        ]

        for i in range(quantidade):
            # Determina gênero baseado na distribuição
            genero = self._escolher_genero(distribuicao_genero)

            # Gera nome baseado no gênero
            if genero == Genero.FEMININO:
                nome = self.fake.name_female()
            elif genero == Genero.MASCULINO:
                nome = self.fake.name_male()
            else:
                nome = self.fake.name()

            # Determina nível hierárquico (distribuição piramidal)
            nivel = self._escolher_nivel_hierarquico()

            # Escolhe cargo baseado no nível
            cargo = random.choice(cargos_por_nivel[nivel])

            # Gera dados temporais
            tempo_empresa = random.randint(6, 240)  # 6 meses a 20 anos
            tempo_cargo_atual = random.randint(3, min(tempo_empresa, 60))
            data_admissao = datetime.now() - timedelta(days=tempo_empresa * 30)

            # Gera salário baseado no nível
            salario_base = {
                NivelHierarquico.ESTAGIARIO: (1500, 2500),
                NivelHierarquico.JUNIOR: (3000, 5000),
                NivelHierarquico.PLENO: (5000, 8000),
                NivelHierarquico.SENIOR: (8000, 12000),
                NivelHierarquico.ESPECIALISTA: (12000, 18000),
                NivelHierarquico.COORDENADOR: (10000, 15000),
                NivelHierarquico.GERENTE: (15000, 25000),
                NivelHierarquico.DIRETOR: (25000, 40000),
                NivelHierarquico.VP: (40000, 60000),
                NivelHierarquico.C_LEVEL: (60000, 100000)
            }
            salario_min, salario_max = salario_base[nivel]
            salario = round(random.uniform(salario_min, salario_max), 2)

            # Gera idade compatível com o nível
            idade_base = {
                NivelHierarquico.ESTAGIARIO: (18, 24),
                NivelHierarquico.JUNIOR: (22, 28),
                NivelHierarquico.PLENO: (26, 35),
                NivelHierarquico.SENIOR: (30, 45),
                NivelHierarquico.ESPECIALISTA: (32, 50),
                NivelHierarquico.COORDENADOR: (30, 45),
                NivelHierarquico.GERENTE: (35, 50),
                NivelHierarquico.DIRETOR: (40, 60),
                NivelHierarquico.VP: (45, 65),
                NivelHierarquico.C_LEVEL: (45, 70)
            }
            idade_min, idade_max = idade_base[nivel]
            idade = random.randint(idade_min, idade_max)

            # Cria a pessoa
            pessoa = Pessoa(
                id=f"P{i+1:04d}",
                nome=nome,
                genero=genero,
                idade=idade,
                cargo=cargo,
                nivel_hierarquico=nivel,
                departamento=random.choice(departamentos),
                tempo_empresa=tempo_empresa,
                tempo_cargo_atual=tempo_cargo_atual,
                salario=salario,
                data_admissao=data_admissao,
                gestor_id=None,  # Pode ser preenchido posteriormente
                email=self._gerar_email(nome)
            )

            pessoas.append(pessoa)

        # Atribui gestores
        self._atribuir_gestores(pessoas)

        return pessoas

    def _escolher_genero(self, distribuicao: dict) -> Genero:
        """Escolhe gênero baseado na distribuição"""
        rand = random.random()
        acumulado = 0

        for genero, probabilidade in distribuicao.items():
            acumulado += probabilidade
            if rand <= acumulado:
                return genero

        return Genero.NAO_INFORMADO

    def _escolher_nivel_hierarquico(self) -> NivelHierarquico:
        """Escolhe nível hierárquico com distribuição piramidal"""
        # Distribuição piramidal: mais pessoas nos níveis inferiores
        niveis_pesos = {
            NivelHierarquico.ESTAGIARIO: 5,
            NivelHierarquico.JUNIOR: 20,
            NivelHierarquico.PLENO: 25,
            NivelHierarquico.SENIOR: 20,
            NivelHierarquico.ESPECIALISTA: 10,
            NivelHierarquico.COORDENADOR: 8,
            NivelHierarquico.GERENTE: 7,
            NivelHierarquico.DIRETOR: 3,
            NivelHierarquico.VP: 1,
            NivelHierarquico.C_LEVEL: 1
        }

        niveis = list(niveis_pesos.keys())
        pesos = list(niveis_pesos.values())

        return random.choices(niveis, weights=pesos)[0]

    def _gerar_email(self, nome: str) -> str:
        """Gera email baseado no nome"""
        # Remove acentos e espaços
        nome_limpo = nome.lower()
        nome_limpo = nome_limpo.replace(' ', '.')

        # Remove acentuação básica
        acentos = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i',
            'ó': 'o', 'õ': 'o', 'ô': 'o',
            'ú': 'u', 'ü': 'u',
            'ç': 'c'
        }

        for acento, letra in acentos.items():
            nome_limpo = nome_limpo.replace(acento, letra)

        return f"{nome_limpo}@empresa.com"

    def _atribuir_gestores(self, pessoas: List[Pessoa]):
        """Atribui gestores para as pessoas baseado na hierarquia"""
        # Separa pessoas por nível
        por_nivel = {}
        for pessoa in pessoas:
            nivel = pessoa.nivel_hierarquico.value
            if nivel not in por_nivel:
                por_nivel[nivel] = []
            por_nivel[nivel].append(pessoa)

        # Para cada nível, atribui gestores do nível superior
        for nivel_valor in sorted(por_nivel.keys()):
            # Procura gestores no próximo nível acima
            for nivel_gestor in range(nivel_valor + 1, 11):
                if nivel_gestor in por_nivel and len(por_nivel[nivel_gestor]) > 0:
                    # Atribui gestores aleatoriamente
                    gestores = por_nivel[nivel_gestor]
                    for pessoa in por_nivel[nivel_valor]:
                        pessoa.gestor_id = random.choice(gestores).id
                    break
