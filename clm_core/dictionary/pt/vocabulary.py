from ...utils.vocabulary import BaseVocabulary


class PTVocabulary(BaseVocabulary):
    @property
    def STOPWORDS(self) -> tuple[str, ...]:
        pass

    @property
    def EPISTEMIC_KEYWORDS(self) -> dict[str, list[str]]:
        pass

    @property
    def CODE_INDICATORS(self) -> tuple[str, ...]:
        pass

    @property
    def PRONOUNS(self) -> tuple[str, ...]:
        pass

    @property
    def MODALS(self) -> tuple[str, ...]:
        pass

    @property
    def ACTION_VERBS(self) -> tuple[str, ...]:
        pass

    def __init__(self):
        super().__init__()

    @property
    def QUANTIFIER_WORDS(self) -> tuple[str, ...]:
        return ("todos", "todas", "tudo", "cada", "inteiro", "completo")

    @property
    def DEMONSTRATIVES(self) -> list[str]:
        return [
            "este",
            "esta",
            "isto",
            "esse",
            "essa",
            "isso",
            "aquele",
            "aquela",
            "aquilo",
        ]

    @property
    def COMPOUND_PHRASES(self) -> dict[str, str]:
        return {
            "suporte ao cliente": "TICKET",
            "ticket de suporte": "TICKET",
            "chamado de suporte": "TICKET",
            "mensagem de email": "EMAIL",
            "transcrição de chat": "TRANSCRIPT",
            "chamada telefônica": "CALL",
            "ligação telefônica": "CALL",
            "código fonte": "CODE",
            "plano de negócios": "PLAN",
            "descrição do produto": "DESCRIPTION",
        }

    @property
    def rank_triggers(self) -> set[str]:
        return {
            "classificar",
            "ranquear",
            "rankear",
            "ordenar",
            "ordem",
            "ordenar por",
            "classificar por",
            "priorizar",
            "topo",
            "superior",
            "primeiro",
            "inferior",
            "último",
            "fundo",
            "maior",
            "mais alto",
            "menor",
            "mais baixo",
            "melhor",
            "melhores",
            "pior",
            "piores",
        }

    @property
    def domain_candidates(self) -> dict[str, list[str]]:
        return {
            "CODE": ["bug", "erro", "segurança", "desempenho", "performance"],
            "ENTITIES": [
                "nomes",
                "datas",
                "valores",
                "quantias",
                "endereços",
                "emails",
                "telefones",
            ],
            "QA": [
                "verificação",
                "política",
                "habilidades interpessoais",
                "soft skills",
                "precisão",
                "exatidão",
                "conformidade",
                "compliance",
                "divulgações",
            ],
            "SUPPORT": [
                "problema",
                "questão",
                "sentimento",
                "ações",
                "urgência",
                "prioridade",
                "ticket",
                "caso",
                "cliente",
                "suporte",
                "chamada",
                "reclamação",
                "atendente",
                "agente",
                "chamador",
                "chat",
                "consulta",
                "solução de problemas",
            ],
            "TECHNICAL": [
                "erro",
                "bug",
                "stacktrace",
                "exceção",
                "api",
                "servidor",
                "log",
                "depurar",
                "rastreamento",
                "falha",
                "implantação",
                "backend",
            ],
            "DOCUMENT": [
                "documento",
                "artigo",
                "manual",
                "guia",
                "doc",
                "texto",
                "transcrição",
                "notas",
                "resumo",
                "instruções",
            ],
            "BUSINESS": [
                "relatório",
                "briefing",
                "análise",
                "executivo",
                "gestão",
                "dashboard",
                "kpi",
                "roi",
                "funil",
                "trimestral",
                "apresentação",
            ],
            "LEGAL": [
                "contrato",
                "política",
                "conformidade",
                "gdpr",
                "cláusula",
                "advogado",
                "acordo",
                "termos",
                "privacidade",
            ],
            "FINANCE": [
                "fatura",
                "cobrança",
                "pagamento",
                "transação",
                "reembolso",
                "despesa",
                "saldo",
                "extrato",
                "valor",
            ],
            "SECURITY": [
                "violação",
                "risco",
                "ameaça",
                "alerta",
                "malware",
                "phishing",
                "permissões",
                "controle de acesso",
                "auditoria",
            ],
            "MEDICAL": [
                "paciente",
                "diagnóstico",
                "prescrição",
                "clínico",
                "prontuário",
                "sintomas",
                "tratamento",
                "médico",
            ],
            "SALES": [
                "lead",
                "crm",
                "oportunidade",
                "pipeline",
                "gerente de contas",
                "prospecto",
                "negócio",
                "cotação",
            ],
            "EDUCATION": [
                "lição",
                "currículo",
                "professor",
                "aluno",
                "treinamento",
                "curso",
                "aprendizagem",
            ],
        }

    @property
    def CONCEPT_INDICATORS(self) -> list[str]:
        """Optional - can have sensible default"""
        return ["conceito de", "ideia de", "noção de", "princípio de"]

    @property
    def MEETING_WORDS(self) -> tuple[str, ...]:
        """Optional - can have empty default"""
        return ("reunião", "conferência", "encontro", "sessão")

    @property
    def PROPOSAL_WORDS(self) -> list[str]:
        """Optional - can have empty default"""
        return ["proposta", "proposição"]

    @property
    def ARTICLES(self) -> list[str]:
        """Optional - can have empty default"""
        return ["o", "a", "os", "as", "um", "uma", "uns", "umas"]

    @property
    def REQ_TOKENS(self) -> dict[str, list[str]]:
        return {
            "ANALYZE": [
                "analisar",
                "analise",
                "revisar",
                "examinar",
                "avaliar",
                "inspecionar",
                "verificar",
                "auditar",
                "investigar",
                "conferir",
            ],
            "MATCH": [
                "combinar",
                "comparar",
                "alinhar",
                "mapear",
                "correlacionar",
                "corresponder",
                "cruzar",
                "casar",
                "verificar contra",
            ],
            "EXTRACT": [
                "extrair",
                "retirar",
                "identificar",
                "encontrar",
                "localizar",
                "obter",
                "recuperar",
                "retornar",
                "incluir",
                "selecionar",
                "pegar",
                "buscar",
            ],
            "SELECT": [
                "selecionar",
                "escolher",
                "filtrar",
                "identificar correspondentes",
                "optar",
                "eleger",
            ],
            "GENERATE": [
                "gerar",
                "criar",
                "escrever",
                "redigir",
                "compor",
                "produzir",
                "construir",
                "desenvolver",
                "projetar",
                "elaborar",
                "fazer",
                "nomear",
                "sugerir",
                "formular",
                "formar",
                "propor",
                "transcrever",
                "montar",
            ],
            "SUMMARIZE": [
                "resumir",
                "condensar",
                "sintetizar",
                "sumarizar",
                "recapitular",
                "abreviar",
                "compendiar",
            ],
            "TRANSFORM": [
                "converter",
                "transformar",
                "mudar",
                "reescrever",
                "traduzir",
                "completar",
                "modificar",
                "adaptar",
                "ajustar",
                "reformular",
                "alterar",
                "editar",
                "adicionar",
                "parafrasear",
                "preencher",
                "remover",
                "substituir",
                "inverter",
                "trocar",
            ],
            "EXPLAIN": [
                "explicar",
                "descrever",
                "esclarecer",
                "elaborar",
                "detalhar",
                "expor",
                "ilustrar",
                "expressar",
                "contar",
                "discutir",
                "definir",
                "elucidar",
                "falar sobre",
                "me diga sobre",
            ],
            "COMPARE": [
                "comparar",
                "contrastar",
                "versus",
                "vs",
                "diferença entre",
                "diferenciar",
                "distinguir",
                "confrontar",
            ],
            "CLASSIFY": [
                "classificar",
                "categorizar",
                "ordenar",
                "agrupar",
                "rotular",
                "organizar",
                "arranjar",
                "segmentar",
                "separar por",
            ],
            "DEBUG": [
                "debugar",
                "depurar",
                "diagnosticar",
                "corrigir bug",
                "investigar bug",
                "encontrar bug",
                "rastrear",
                "identificar problema",
                "resolver erro",
            ],
            "OPTIMIZE": [
                "otimizar",
                "melhorar",
                "aprimorar",
                "refatorar",
                "acelerar",
                "simplificar",
                "maximizar",
                "minimizar",
                "reduzir",
                "aumentar",
                "aperfeiçoar",
            ],
            "VALIDATE": [
                "validar",
                "verificar",
                "checar",
                "confirmar",
                "testar",
                "garantir",
                "certificar",
                "autenticar",
                "assegurar",
            ],
            "SEARCH": [
                "buscar",
                "pesquisar",
                "procurar",
                "encontrar",
                "localizar",
                "consultar",
                "descobrir",
                "achar",
            ],
            "RANK": [
                "priorizar",
                "ordenar",
                "classificar por",
                "pontuar",
                "ranquear",
                "avaliar",
                "hierarquizar",
            ],
            "PREDICT": [
                "prever",
                "projetar",
                "estimar",
                "antecipar",
                "prognosticar",
                "extrapolar",
                "predizer",
                "vaticinar",
            ],
            "FORMAT": [
                "formatar",
                "estruturar",
                "organizar",
                "dispor",
                "arranjar",
                "layoutar",
            ],
            "DETECT": [
                "detectar",
                "identificar",
                "descobrir",
                "perceber",
                "reconhecer",
                "notar",
                "captar",
            ],
            "CALCULATE": [
                "calcular",
                "computar",
                "determinar",
                "quantificar",
                "medir",
                "contar",
                "somar",
                "totalizar",
            ],
            # Aggregation
            "AGGREGATE": [
                "agregar",
                "agrupar",
                "combinar",
                "consolidar",
                "juntar",
                "mesclar",
                "compilar",
                "coletar",
                "reunir",
            ],
            "DETERMINE": [
                "determinar",
                "decidir",
                "avaliar",
                "concluir",
                "estabelecer",
                "escolher",
                "definir",
                "resolver",
            ],
            "ROUTE": [
                "rotear",
                "atribuir",
                "direcionar",
                "encaminhar",
                "enviar para",
                "delegar",
                "alocar",
                "distribuir",
            ],
            "EXECUTE": [
                "usar",
                "aplicar",
                "implementar",
                "executar",
                "realizar",
                "empregar",
                "utilizar",
                "rodar",
            ],
            "LIST": [
                "listar",
                "enumerar",
                "itemizar",
                "delinear",
                "relacionar",
                "elencar",
            ],
        }

    @property
    def NOISE_VERBS(self) -> set[str]:
        return {
            "ser",
            "estar",
            "ter",
            "haver",
            "poder",
            "dever",
            "querer",
            "ir",
            "vir",
            "fazer",
            "ficar",
            "viver",
            "morar",
            "continuar",
            "permanecer",
            "seguir",
            "basear",
            "precisar",
            "necessitar",
            "começar",
            "iniciar",
            "tornar",
            "parecer",
            "aparecer",
            "mostrar",
            "ver",
            "saber",
            "pensar",
            "sentir",
            "dizer",
            "falar",
            "chamar",
        }

    @property
    def CONTEXT_FILTERS(self) -> dict[str, list[str]]:
        return {
            "dar": ["dado", "dando", "dê-me", "me dê"],
            "seguir": ["seguinte", "a seguir", "seguindo"],
            "basear": ["baseado em", "com base em"],
            "usar": ["útil", "usado para", "utilizado"],
        }

    @property
    def TARGET_TOKENS(self) -> dict[str, list[str]]:
        return {
            "CODE": [
                "código",
                "script",
                "programa",
                "função",
                "método",
                "classe",
                "trecho",
                "rotina",
            ],
            "DATA": [
                "dados",
                "dataset",
                "conjunto de dados",
                "banco de dados",
                "planilha",
                "tabela",
                "csv",
            ],
            "QUERY": [
                "query",
                "consulta",
                "sql",
                "consulta sql",
                "consulta de banco",
            ],
            "ENDPOINT": [
                "endpoint",
                "api",
                "ponto de acesso",
                "serviço rest",
            ],
            "COMPONENT": [
                "componente",
                "módulo",
                "pacote",
                "biblioteca",
                "lib",
            ],
            "SYSTEM": [
                "sistema",
                "aplicação",
                "app",
                "aplicativo",
                "software",
                "plataforma",
            ],
            "TEST": [
                "teste",
                "teste unitário",
                "caso de teste",
                "suíte de testes",
            ],
            "LOG": [
                "log",
                "logs",
                "arquivo de log",
                "registro",
                "histórico",
            ],
            "RECORD": [
                "registro",
                "entrada",
                "linha",
                "item",
            ],
            "STRATEGY": [
                "estratégia",
                "abordagem",
                "plano",
                "metodologia",
            ],
            "NBA_CATALOG": [
                "nba",
                "nbas",
                "próxima melhor ação",
                "próximas melhores ações",
                "ações predefinidas",
                "ações possíveis",
                "ações disponíveis",
            ],
            "DOCUMENT": [
                "documento",
                "doc",
                "arquivo",
                "relatório",
                "artigo",
                "papel",
            ],
            "EMAIL": [
                "email",
                "e-mail",
                "mensagem",
                "correspondência",
            ],
            "REPORT": [
                "relatório",
                "análise",
                "conclusões",
                "parecer",
            ],
            "TICKET": [
                "ticket",
                "chamado",
                "ocorrência",
                "caso",
                "solicitação",
            ],
            "TRANSCRIPT": [
                "transcrição",
                "conversa",
                "diálogo",
                "histórico de chat",
                "atendimento",
            ],
            "FEEDBACK": [
                "feedback",
                "comentário",
                "avaliação",
                "crítica",
                "retorno",
            ],
            "COMMENT": [
                "comentário",
                "observação",
                "nota",
                "anotação",
            ],
            "CUSTOMER_INTENT": [
                "intenção do cliente",
                "necessidade do cliente",
                "pedido do cliente",
                "objetivo do cliente",
                "problema do cliente",
            ],
            "COMPLAINT": [
                "reclamação",
                "queixa",
                "problema",
                "insatisfação",
            ],
            "REQUEST": [
                "solicitação",
                "pedido",
                "requisição",
            ],
            "INQUIRY": [
                "consulta",
                "pergunta",
                "dúvida",
                "questionamento",
            ],
            "INTERACTION": [
                "interação",
                "atendimento",
                "contato",
            ],
            "CALL": [
                "chamada",
                "ligação",
                "telefonema",
            ],
            "DESCRIPTION": [
                "descrição",
                "detalhamento",
            ],
            "SUMMARY": [
                "resumo",
                "sumário",
                "síntese",
            ],
            "PLAN": [
                "plano",
                "planejamento",
                "projeto",
            ],
            "POST": [
                "post",
                "postagem",
                "publicação",
            ],
            "PRESS_RELEASE": [
                "comunicado de imprensa",
                "release",
                "nota à imprensa",
                "anúncio",
            ],
            "INTRODUCTION": [
                "introdução",
                "apresentação",
            ],
            "CAPTION": [
                "legenda",
                "caption",
            ],
            "QUESTIONS": [
                "perguntas",
                "questões",
                "questionário",
                "faq",
            ],
            "RESPONSE": [
                "resposta",
                "réplica",
                "retorno",
                "template de resposta",
            ],
            "LOGS": [
                "logs",
                "registros",
                "históricos",
            ],
            "CORRELATION": [
                "correlação",
                "correlações",
                "relação",
                "relações",
            ],
            "TRADEOFF": [
                "trade-off",
                "compensação",
                "custo-benefício",
            ],
            "PARADIGM": [
                "paradigma",
                "paradigmas",
                "modelo",
            ],
            "PAIN_POINTS": [
                "pontos de dor",
                "dores",
                "problemas",
                "dificuldades",
            ],
            "PATTERN": [
                "padrão",
                "padrões",
                "tendência",
                "tendências",
            ],
            "CHURN": [
                "churn",
                "cancelamento",
                "evasão",
                "rotatividade",
            ],
            "FEATURES": [
                "funcionalidades",
                "recursos",
                "características",
                "features",
            ],
            "METRICS": [
                "receita",
                "métricas",
                "estatísticas",
                "números",
                "indicadores",
            ],
            "REGIONS": [
                "regiões",
                "áreas",
                "locais",
                "territórios",
            ],
            "ITEMS": [
                "itens",
                "coisas",
                "elementos",
                "lista",
                "opções",
                "escolhas",
            ],
            "CONCEPT": [
                "conceito",
                "ideia",
                "noção",
                "princípio",
                "teoria",
            ],
            "PROCEDURE": [
                "procedimento",
                "processo",
                "passos",
                "método",
                "técnica",
            ],
            "FACT": [
                "fato",
                "fatos",
                "informação",
                "informações",
                "detalhes",
            ],
            "ANSWER": [
                "resposta",
                "solução",
            ],
        }

    @property
    def EXTRACT_FIELDS(self) -> tuple[str, ...]:
        return (
            "ISSUE",
            "SENTIMENT",
            "ACTIONS",
            "NEXT_STEPS",
            "URGENCY",
            "PRIORITY",
            "NAMES",
            "DATES",
            "AMOUNTS",
            "EMAILS",
            "PHONES",
            "ADDRESSES",
            "BUGS",
            "SECURITY",
            "PERFORMANCE",
            "STYLE",
            "ERRORS",
            "WARNINGS",
            "KEYWORDS",
            "TOPICS",
            "ENTITIES",
            "FACTS",
            "DECISIONS",
            "DEADLINES",
            "REQUIREMENTS",
            "FEATURES",
            "PROBLEMS",
            "SOLUTIONS",
            "RISKS",
            "METRICS",
            "KPI",
            "SCORES",
            "RATINGS",
            "FEEDBACK",
            "COMPLAINTS",
            "OWNERS",
            "ASSIGNEES",
            "STAKEHOLDERS",
            "PARTICIPANTS",
            "TIMESTAMPS",
            "DURATIONS",
            "FREQUENCIES",
            "QUANTITIES",
            "CATEGORIES",
            "TAGS",
            "LABELS",
            "STATUS",
            "TYPE",
            "CUSTOMER_INTENT",
            "RELEVANCE_SCORE",
            "NBA_ID",
            "MATCH_CONFIDENCE",
            "SEMANTIC_SIMILARITY",
            "THRESHOLD",
        )

    @property
    def OUTPUT_FORMATS(self) -> dict[str, list[str]]:
        return {
            "JSON": ["json", "formato json"],
            "MARKDOWN": ["markdown", "md"],
            "TABLE": ["tabela", "tabular"],
            "LIST": ["lista", "tópicos", "bullet points"],
            "PLAIN": ["texto simples", "texto puro"],
            "CSV": ["csv", "separado por vírgula"],
        }

    @property
    def IMPERATIVE_PATTERNS(self) -> list[tuple[list[str], str, str]]:
        return [
            (["liste", "listar", "enumere", "enumerar", "itemize"], "LIST", "ITEMS"),
            (["nomeie", "nomear", "identifique", "identificar"], "GENERATE", "ITEMS"),
            (
                ["dê", "dar", "forneça", "fornecer", "sugira", "sugerir"],
                "GENERATE",
                "ITEMS",
            ),
            (
                [
                    "diga",
                    "dizer",
                    "explique",
                    "explicar",
                    "descreva",
                    "descrever",
                    "esclareça",
                    "esclarecer",
                    "ilustre",
                    "ilustrar",
                ],
                "EXPLAIN",
                "CONCEPT",
            ),
        ]

    @property
    def QUESTION_WORDS(self) -> list[str]:
        return [
            "o que",
            "que",
            "quem",
            "onde",
            "quando",
            "por que",
            "porque",
            "como",
            "qual",
            "quais",
        ]
