"""Seed script to populate the database with sample data for demo/testing."""

import random
from datetime import datetime, timedelta, timezone

from .auth import hash_password
from .database import SessionLocal, init_db
from .models import Transcription, TTSRequest, User

SAMPLE_TRANSCRIPTIONS = [
    {
        "title": "Aula de Algoritmos - Aula 12",
        "text": (
            "Discussao sobre grafos direcionados e nao-direcionados, algoritmo de Dijkstra "
            "para menor caminho e aplicacoes praticas em redes e mapas. Tambem abordamos "
            "a complexidade do algoritmo e suas variantes para grafos com pesos negativos."
        ),
        "category": "Algoritmos",
        "duration": 4800,
    },
    {
        "title": "Palestra - Computacao em Nuvem",
        "text": (
            "Conceitos de cloud computing: IaaS, PaaS e SaaS. Comparacao entre os principais "
            "provedores AWS, Azure e Google Cloud Platform. Discutimos arquiteturas serverless "
            "e containers com Docker e Kubernetes."
        ),
        "category": "Cloud / Redes",
        "duration": 2700,
    },
    {
        "title": "Calculo I - Derivadas",
        "text": (
            "Regras de derivacao: produto, quociente e cadeia. Exercicios de aplicacao com "
            "funcoes trigonometricas e exponenciais. Teorema do valor medio e aplicacoes "
            "em problemas de otimizacao."
        ),
        "category": "Calculo I",
        "duration": 7200,
    },
    {
        "title": "Fisica - Mecanica Quantica Introducao",
        "text": (
            "Principios fundamentais da mecanica quantica. Dualidade onda-particula, "
            "principio da incerteza de Heisenberg. Funcao de onda e equacao de Schrodinger."
        ),
        "category": "Fisica",
        "duration": 5400,
    },
    {
        "title": "Estruturas de Dados - Arvores AVL",
        "text": (
            "Arvores binarias de busca balanceadas. Rotacoes simples e duplas para manter "
            "o balanceamento. Complexidade O(log n) para insercao, busca e remocao. "
            "Comparacao com arvores Red-Black."
        ),
        "category": "Algoritmos",
        "duration": 3600,
    },
    {
        "title": "Redes de Computadores - TCP/IP",
        "text": (
            "Modelo TCP/IP e suas camadas. Protocolo TCP vs UDP. Enderecos IP, sub-redes "
            "e roteamento. DNS e resolucao de nomes. HTTP e HTTPS."
        ),
        "category": "Cloud / Redes",
        "duration": 4200,
    },
    {
        "title": "Algebra Linear - Transformacoes Lineares",
        "text": (
            "Definicao de transformacoes lineares. Nucleo e imagem. Teorema do nucleo "
            "e da imagem. Representacao matricial de transformacoes."
        ),
        "category": "Calculo I",
        "duration": 3000,
    },
    {
        "title": "Inteligencia Artificial - Redes Neurais",
        "text": (
            "Perceptrons e redes neurais multicamada. Funcoes de ativacao: sigmoid, ReLU, "
            "tanh. Algoritmo de backpropagation. Redes convolucionais e recorrentes."
        ),
        "category": "Algoritmos",
        "duration": 5100,
    },
]

SAMPLE_TTS_TEXTS = [
    "A inteligencia artificial esta transformando a educacao ao personalizar a experiencia de aprendizagem.",
    "Algoritmos de ordenacao como QuickSort e MergeSort sao fundamentais na ciencia da computacao.",
    "Cloud computing permite escalabilidade e reducao de custos para empresas de todos os portes.",
    "A mecanica quantica desafia nossa intuicao sobre a natureza fundamental da realidade.",
    "Estruturas de dados eficientes sao a base para construir softwares de alto desempenho.",
]

VOICES = ["female_pt_br", "male_pt_br", "child_pt_br"]
SPEEDS = [0.5, 0.75, 1.0, 1.0, 1.0, 1.25, 1.5, 2.0]


def seed_database():
    """Populate the database with sample data."""
    init_db()
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_user = db.query(User).filter(User.email == "alex@gtalk.demo").first()
        if existing_user:
            print("Database already seeded. Skipping.")
            return

        # Create demo user
        user = User(
            name="Alex Demo",
            email="alex@gtalk.demo",
            hashed_password=hash_password("demo1234"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created demo user: {user.email}")

        # Create transcriptions spread over the last 30 days
        now = datetime.now(timezone.utc)
        for i, sample in enumerate(SAMPLE_TRANSCRIPTIONS):
            days_ago = random.randint(0, 29)
            hours_ago = random.randint(0, 23)
            created = now - timedelta(days=days_ago, hours=hours_ago)
            text = sample["text"]
            word_count = len(text.split())

            t = Transcription(
                user_id=user.id,
                title=sample["title"],
                transcribed_text=text,
                language="pt-BR",
                duration_seconds=sample["duration"],
                word_count=word_count,
                status="completed",
                category=sample["category"],
                created_at=created,
                completed_at=created + timedelta(seconds=random.randint(5, 30)),
            )
            db.add(t)

        # Add a few pending/failed transcriptions
        pending = Transcription(
            user_id=user.id,
            title="Aula de Banco de Dados - Normalizacao",
            language="pt-BR",
            status="pending",
            category="Algoritmos",
            created_at=now - timedelta(hours=2),
        )
        failed = Transcription(
            user_id=user.id,
            title="Gravacao com ruido - Sala 205",
            language="pt-BR",
            status="failed",
            category="Fisica",
            created_at=now - timedelta(days=3),
        )
        db.add_all([pending, failed])
        db.commit()
        print(f"Created {len(SAMPLE_TRANSCRIPTIONS) + 2} transcriptions")

        # Create TTS requests
        for i, text in enumerate(SAMPLE_TTS_TEXTS):
            for j in range(random.randint(1, 3)):
                days_ago = random.randint(0, 29)
                created = now - timedelta(days=days_ago, hours=random.randint(0, 23))
                tts = TTSRequest(
                    user_id=user.id,
                    input_text=text,
                    voice=random.choice(VOICES),
                    speed=random.choice(SPEEDS),
                    char_count=len(text),
                    status="completed",
                    created_at=created,
                    completed_at=created + timedelta(seconds=random.randint(2, 10)),
                )
                db.add(tts)

        db.commit()
        tts_count = db.query(TTSRequest).filter(TTSRequest.user_id == user.id).count()
        print(f"Created {tts_count} TTS requests")

        print("\nSeed complete!")
        print("Demo login: alex@gtalk.demo / demo1234")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
