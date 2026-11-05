from datetime import datetime, timezone
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(50), default='voluntario')
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Familia(db.Model):
    __tablename__ = 'familias'
    id = db.Column(db.Integer, primary_key=True)
    nome_responsavel = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    bairro = db.Column(db.String(100), default='Bairro São Pedro')
    quantidade_membros = db.Column(db.Integer, default=1)
    data_cadastro = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    ativo = db.Column(db.Boolean, default=True)

    atendimentos = db.relationship('Atendimento', backref='familia', lazy=True, order_by='desc(Atendimento.data_atendimento)')

class ItemDoacao(db.Model):
    __tablename__ = 'itens_doacao'
    id = db.Column(db.Integer, primary_key=True)
    nome_alimento = db.Column(db.String(120), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    unidade_medida = db.Column(db.String(20), default='unidades')
    data_validade = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(50), default='Não perecíveis')
    cadastrado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Atendimento(db.Model):
    __tablename__ = 'atendimentos'
    id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, db.ForeignKey('familias.id'), nullable=False)
    data_atendimento = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    tipo_beneficio = db.Column(db.String(100), default='Cesta Básica Completa')
    responsavel_entrega = db.Column(db.String(100), default='Regina de Fátima Alves')
    observacoes = db.Column(db.String(255), nullable=True)
