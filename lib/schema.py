"""Estruturas de dados usadas em todo o pipeline de análise dos relatórios."""

from dataclasses import dataclass, field


@dataclass
class Pendencia:
    codigo: str
    severidade: str  # "critica" | "aviso"
    descricao: str


@dataclass
class ResultadoValidacao:
    valido: bool
    score: float  # 0.0 a 1.0
    motivos: list = field(default_factory=list)  # list[str], razões do score


@dataclass
class RelatorioTutor:
    arquivo_origem: str
    pasta_origem: str  # código do curso/polo (nome da subpasta no zip, ex. "C10", "EQ")

    validacao: ResultadoValidacao

    nome: str = ""
    cpf: str = ""
    curso: str = ""
    polo: str = ""
    mes: str = ""
    ano: str = ""

    assinado: bool = False

    respostas: dict = field(default_factory=dict)  # chave -> {"valor": str, "justificativa": str}

    pendencias: list = field(default_factory=list)  # list[Pendencia]

    @property
    def tem_pendencia_critica(self) -> bool:
        return any(p.severidade == "critica" for p in self.pendencias)
