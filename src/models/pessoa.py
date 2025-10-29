"""
Modelo de dados para Pessoa com informações hierárquicas
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class Genero(Enum):
    """Enum para gênero"""
    MASCULINO = "Masculino"
    FEMININO = "Feminino"
    OUTRO = "Outro"
    NAO_INFORMADO = "Não Informado"


class NivelHierarquico(Enum):
    """Enum para níveis hierárquicos"""
    ESTAGIARIO = 1
    JUNIOR = 2
    PLENO = 3
    SENIOR = 4
    ESPECIALISTA = 5
    COORDENADOR = 6
    GERENTE = 7
    DIRETOR = 8
    VP = 9
    C_LEVEL = 10


@dataclass
class Pessoa:
    """
    Classe que representa uma pessoa na organização

    Atributos:
        id: Identificador único
        nome: Nome completo
        genero: Gênero da pessoa
        idade: Idade
        cargo: Cargo atual
        nivel_hierarquico: Nível na hierarquia
        departamento: Departamento/área
        tempo_empresa: Tempo de empresa em meses
        tempo_cargo_atual: Tempo no cargo atual em meses
        salario: Salário atual
        data_admissao: Data de admissão
        gestor_id: ID do gestor direto
    """
    id: str
    nome: str
    genero: Genero
    idade: int
    cargo: str
    nivel_hierarquico: NivelHierarquico
    departamento: str
    tempo_empresa: int  # em meses
    tempo_cargo_atual: int  # em meses
    salario: float
    data_admissao: datetime
    gestor_id: Optional[str] = None
    email: Optional[str] = None

    def __post_init__(self):
        """Validações após inicialização"""
        if self.tempo_cargo_atual > self.tempo_empresa:
            raise ValueError("Tempo no cargo não pode ser maior que tempo de empresa")

        if self.idade < 18:
            raise ValueError("Idade deve ser maior ou igual a 18 anos")

    def pode_ser_promovido(self, tempo_minimo_meses: int = 12) -> bool:
        """
        Verifica se a pessoa está elegível para promoção baseado no tempo no cargo

        Args:
            tempo_minimo_meses: Tempo mínimo no cargo para promoção (padrão: 12 meses)

        Returns:
            bool: True se pode ser promovido, False caso contrário
        """
        return self.tempo_cargo_atual >= tempo_minimo_meses

    def proximo_nivel(self) -> Optional[NivelHierarquico]:
        """
        Retorna o próximo nível hierárquico possível

        Returns:
            NivelHierarquico ou None se já estiver no nível máximo
        """
        nivel_atual = self.nivel_hierarquico.value

        # Encontra o próximo nível
        for nivel in NivelHierarquico:
            if nivel.value == nivel_atual + 1:
                return nivel

        return None  # Já está no nível máximo

    def to_dict(self) -> dict:
        """Converte a pessoa para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'genero': self.genero.value,
            'idade': self.idade,
            'cargo': self.cargo,
            'nivel_hierarquico': self.nivel_hierarquico.name,
            'nivel_hierarquico_valor': self.nivel_hierarquico.value,
            'departamento': self.departamento,
            'tempo_empresa': self.tempo_empresa,
            'tempo_cargo_atual': self.tempo_cargo_atual,
            'salario': self.salario,
            'data_admissao': self.data_admissao.isoformat(),
            'gestor_id': self.gestor_id,
            'email': self.email
        }
