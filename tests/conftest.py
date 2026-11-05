import pytest
from datetime import datetime, date, timezone, timedelta
from app import create_app, db
from app.models import User, Familia, ItemDoacao, Atendimento
from app.services import AuthService

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    with app.app_context():
        db.create_all()
        # Seed test data
        admin = User(
            nome="Regina de Fátima Alves",
            email="regina.alves@esperancaviva.org",
            password_hash=AuthService.hash_password("Esperanca@2026"),
            perfil="coordenadora"
        )
        db.session.add(admin)

        hoje = datetime.now(timezone.utc).date()
        f1 = Familia(
            nome_responsavel="Maria Aparecida da Silva",
            cpf="123.456.789-00",
            bairro="Bairro São Pedro",
            quantidade_membros=4,
            data_cadastro=date(2026, 3, 10),
            ativo=True
        )
        f2 = Familia(
            nome_responsavel="João Carlos dos Santos",
            cpf="987.654.321-11",
            bairro="Bairro São Pedro",
            quantidade_membros=3,
            data_cadastro=date(2026, 4, 15),
            ativo=True
        )
        db.session.add_all([f1, f2])
        db.session.commit()

        # Atendimento no mês atual para João Carlos
        atend_joao = Atendimento(
            familia_id=f2.id,
            data_atendimento=datetime(hoje.year, hoje.month, 1, 10, 0, tzinfo=timezone.utc),
            tipo_beneficio="Cesta Básica Completa",
            responsavel_entrega="Regina de Fátima Alves"
        )
        # Atendimento no mês anterior para Maria Aparecida
        mes_ant = 12 if hoje.month == 1 else hoje.month - 1
        ano_ant = hoje.year - 1 if hoje.month == 1 else hoje.year
        atend_maria = Atendimento(
            familia_id=f1.id,
            data_atendimento=datetime(ano_ant, mes_ant, 15, 14, 0, tzinfo=timezone.utc),
            tipo_beneficio="Cesta Básica Completa",
            responsavel_entrega="Regina de Fátima Alves"
        )
        db.session.add_all([atend_joao, atend_maria])

        # Itens de estoque
        item1 = ItemDoacao(
            nome_alimento="Leite Integral UHT",
            quantidade=40,
            unidade_medida="caixas",
            data_validade=hoje + timedelta(days=5),
            categoria="Laticínios"
        )
        db.session.add(item1)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_nome'] = 'Regina de Fátima Alves'
        sess['user_perfil'] = 'coordenadora'
    return client
