from datetime import date, datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Familia, ItemDoacao, Atendimento

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password, method='scrypt')

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        return check_password_hash(stored_hash, password)

    @staticmethod
    def authenticate(email: str, password: str):
        user = User.query.filter_by(email=email.strip().lower()).first()
        if user and AuthService.verify_password(user.password_hash, password):
            return user
        return None

class AtendimentoService:
    @staticmethod
    def pode_receber_cesta(familia_id: int, data_referencia: date | None = None) -> tuple[bool, str, Atendimento | None]:
        if data_referencia is None:
            data_referencia = datetime.now(timezone.utc).date()

        familia = db.session.get(Familia, familia_id)
        if not familia or not familia.ativo:
            return False, "Família não encontrada ou cadastro inativo.", None

        ultimo_atendimento = (
            Atendimento.query
            .filter_by(familia_id=familia_id)
            .order_by(Atendimento.data_atendimento.desc())
            .first()
        )

        if ultimo_atendimento:
            dt_atendimento = ultimo_atendimento.data_atendimento.date()
            if dt_atendimento.year == data_referencia.year and dt_atendimento.month == data_referencia.month:
                data_formatada = dt_atendimento.strftime('%d/%m/%Y')
                return (
                    False,
                    f"BLOQUEADO: Benefício já retirado neste mês civil (em {data_formatada}).",
                    ultimo_atendimento
                )

        return True, "LIBERADA P/ RETIRADA", ultimo_atendimento

    @staticmethod
    def registrar_atendimento(familia_id: int, responsavel_entrega: str = "Regina de Fátima Alves", tipo_beneficio: str = "Cesta Básica Completa", observacoes: str = "") -> Atendimento:
        pode, motivo, ultimo = AtendimentoService.pode_receber_cesta(familia_id)
        if not pode:
            raise ValueError(motivo)

        atendimento = Atendimento(
            familia_id=familia_id,
            data_atendimento=datetime.now(timezone.utc),
            tipo_beneficio=tipo_beneficio,
            responsavel_entrega=responsavel_entrega,
            observacoes=observacoes
        )
        db.session.add(atendimento)
        db.session.commit()
        return atendimento

class EstoqueService:
    @staticmethod
    def calcular_status_validade(data_validade: date, data_referencia: date | None = None) -> dict:
        if data_referencia is None:
            data_referencia = datetime.now(timezone.utc).date()

        dias_restantes = (data_validade - data_referencia).days

        if dias_restantes < 0:
            return {
                'codigo': 'vencido',
                'label': f'VENCIDO ({abs(dias_restantes)} dias)',
                'css_badge': 'bg-danger text-white',
                'icone': 'bi-x-circle-fill',
                'dias': dias_restantes
            }
        elif dias_restantes <= 7:
            return {
                'codigo': 'critico',
                'label': f'CRÍTICO ({dias_restantes} dias)',
                'css_badge': 'bg-warning text-dark',
                'icone': 'bi-hourglass-split',
                'dias': dias_restantes
            }
        else:
            return {
                'codigo': 'regular',
                'label': f'REGULAR ({dias_restantes} dias)',
                'css_badge': 'bg-success text-white',
                'icone': 'bi-check-circle-fill',
                'dias': dias_restantes
            }

    @staticmethod
    def listar_itens_com_status(data_referencia: date | None = None) -> list[dict]:
        itens = ItemDoacao.query.order_by(ItemDoacao.data_validade.asc()).all()
        resultado = []
        for item in itens:
            status = EstoqueService.calcular_status_validade(item.data_validade, data_referencia)
            resultado.append({
                'item': item,
                'status': status
            })
        return resultado

    @staticmethod
    def cadastrar_item(nome: str, quantidade: int, unidade: str, data_validade: date, categoria: str = "Alimento") -> ItemDoacao:
        item = ItemDoacao(
            nome_alimento=nome.strip(),
            quantidade=quantidade,
            unidade_medida=unidade.strip(),
            data_validade=data_validade,
            categoria=categoria
        )
        db.session.add(item)
        db.session.commit()
        return item

class FamiliaService:
    @staticmethod
    def buscar_por_termo(termo: str) -> list[Familia]:
        termo = termo.strip()
        if not termo:
            return []
        termo_limpo_cpf = termo.replace('.', '').replace('-', '')
        return Familia.query.filter(
            (Familia.nome_responsavel.ilike(f"%{termo}%")) |
            (Familia.cpf.like(f"%{termo}%")) |
            (Familia.cpf.like(f"%{termo_limpo_cpf}%"))
        ).all()

def seed_initial_data():
    if User.query.count() == 0:
        admin = User(
            nome="Regina de Fátima Alves",
            email="regina.alves@esperancaviva.org",
            password_hash=AuthService.hash_password("Esperanca@2026"),
            perfil="coordenadora"
        )
        db.session.add(admin)

    if Familia.query.count() == 0:
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

        # Atendimento anterior de João Carlos no mês atual (para testar bloqueio)
        atend_joao = Atendimento(
            familia_id=f2.id,
            data_atendimento=datetime(hoje.year, hoje.month, 2, 10, 30, tzinfo=timezone.utc),
            tipo_beneficio="Cesta Básica Completa",
            responsavel_entrega="Regina de Fátima Alves",
            observacoes="Entrega regular realizada no início do mês"
        )
        # Atendimento anterior de Maria Aparecida no mês anterior (liberada para este mês)
        mes_ant = 12 if hoje.month == 1 else hoje.month - 1
        ano_ant = hoje.year - 1 if hoje.month == 1 else hoje.year
        atend_maria = Atendimento(
            familia_id=f1.id,
            data_atendimento=datetime(ano_ant, mes_ant, 15, 14, 0, tzinfo=timezone.utc),
            tipo_beneficio="Cesta Básica Completa",
            responsavel_entrega="Regina de Fátima Alves",
            observacoes="Entregue sem pendências"
        )
        db.session.add_all([atend_joao, atend_maria])

    if ItemDoacao.query.count() == 0:
        hoje = datetime.now(timezone.utc).date()
        item1 = ItemDoacao(
            nome_alimento="Leite Integral UHT",
            quantidade=40,
            unidade_medida="caixas",
            data_validade=hoje + timedelta(days=5),
            categoria="Laticínios"
        )
        item2 = ItemDoacao(
            nome_alimento="Arroz Branco Tipo 1",
            quantidade=60,
            unidade_medida="kg",
            data_validade=hoje + timedelta(days=90),
            categoria="Grãos"
        )
        item3 = ItemDoacao(
            nome_alimento="Feijão Carioca",
            quantidade=50,
            unidade_medida="kg",
            data_validade=hoje + timedelta(days=60),
            categoria="Grãos"
        )
        item4 = ItemDoacao(
            nome_alimento="Iogurte Natural",
            quantidade=15,
            unidade_medida="garrafas",
            data_validade=hoje - timedelta(days=2),
            categoria="Laticínios"
        )
        db.session.add_all([item1, item2, item3, item4])

    db.session.commit()
