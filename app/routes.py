from functools import wraps
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session
)
from . import db
from .models import Familia, Atendimento, ItemDoacao
from .services import AuthService, AtendimentoService, EstoqueService, FamiliaService

main_bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Por favor, realize login para acessar o sistema.", "warning")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.atendimento'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        user = AuthService.authenticate(email, password)
        if user:
            session.clear()
            session['user_id'] = user.id
            session['user_nome'] = user.nome
            session['user_perfil'] = user.perfil
            flash(f"Bem-vinda(o), {user.nome}! Sessão iniciada com segurança.", "success")
            return redirect(url_for('main.atendimento'))
        else:
            flash("E-mail ou senha incorretos. Verifique suas credenciais.", "danger")

    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    flash("Sessão finalizada com sucesso.", "info")
    return redirect(url_for('main.login'))

@main_bp.route('/atendimento', methods=['GET'])
@login_required
def atendimento():
    termo = request.args.get('busca', '').strip()
    familia_selecionada = None
    status_retirada = None
    ultimo_atendimento = None
    pode_retirar = False

    if termo:
        resultados = FamiliaService.buscar_por_termo(termo)
        if resultados:
            familia_selecionada = resultados[0]
            pode_retirar, status_retirada, ultimo_atendimento = (
                AtendimentoService.pode_receber_cesta(familia_selecionada.id)
            )
        else:
            flash(f"Nenhum beneficiário encontrado com o termo '{termo}'.", "warning")

    return render_template(
        'atendimento.html',
        termo=termo,
        familia=familia_selecionada,
        pode_retirar=pode_retirar,
        status_retirada=status_retirada,
        ultimo_atendimento=ultimo_atendimento
    )

@main_bp.route('/atendimento/<int:familia_id>/registrar', methods=['POST'])
@login_required
def registrar_entrega(familia_id):
    responsavel = session.get('user_nome', 'Regina de Fátima Alves')
    observacoes = request.form.get('observacoes', 'Entrega regular no balcão')

    try:
        atendimento_novo = AtendimentoService.registrar_atendimento(
            familia_id=familia_id,
            responsavel_entrega=responsavel,
            observacoes=observacoes
        )
        flash(
            f"Entrega de Cesta Básica confirmada com sucesso para a família (Registro #{atendimento_novo.id})!",
            "success"
        )
    except ValueError as e:
        flash(str(e), "danger")

    familia = db.session.get(Familia, familia_id)
    termo_busca = familia.cpf if familia else ""
    return redirect(url_for('main.atendimento', busca=termo_busca))

@main_bp.route('/estoque', methods=['GET'])
@login_required
def estoque():
    itens_status = EstoqueService.listar_itens_com_status()
    total_itens = sum(item_data['item'].quantidade for item_data in itens_status)
    criticos_count = sum(1 for item_data in itens_status if item_data['status']['codigo'] in ['critico', 'vencido'])

    return render_template(
        'estoque.html',
        itens_status=itens_status,
        total_itens=total_itens,
        criticos_count=criticos_count
    )

@main_bp.route('/estoque/novo', methods=['POST'])
@login_required
def cadastrar_doacao():
    nome = request.form.get('nome_alimento', '')
    quantidade = int(request.form.get('quantidade', 0))
    unidade = request.form.get('unidade_medida', 'unidades')
    data_val_str = request.form.get('data_validade', '')
    categoria = request.form.get('categoria', 'Alimento')

    try:
        data_validade = datetime.strptime(data_val_str, '%Y-%m-%d').date()
        EstoqueService.cadastrar_item(
            nome=nome,
            quantidade=quantidade,
            unidade=unidade,
            data_validade=data_validade,
            categoria=categoria
        )
        flash(f"Lote de '{nome}' ({quantidade} {unidade}) cadastrado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao cadastrar doação: {str(e)}", "danger")

    return redirect(url_for('main.estoque'))
