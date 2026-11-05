import pytest
from datetime import date, timedelta
from app.services import AuthService, AtendimentoService, EstoqueService, FamiliaService
from app.models import Familia, ItemDoacao, Atendimento

def test_auth_service_hash_and_verify():
    # Arrange
    senha_plana = "SenhaForte@2026"

    # Act
    hash_gerado = AuthService.hash_password(senha_plana)

    # Assert
    assert hash_gerado != senha_plana
    assert AuthService.verify_password(hash_gerado, senha_plana) is True
    assert AuthService.verify_password(hash_gerado, "SenhaErrada") is False

def test_trava_duplicidade_mesmo_mes(app):
    with app.app_context():
        # Arrange - João Carlos já recebeu cesta no mês vigente
        joao = Familia.query.filter_by(cpf="987.654.321-11").first()

        # Act
        pode, motivo, ultimo = AtendimentoService.pode_receber_cesta(joao.id)

        # Assert
        assert pode is False
        assert "BLOQUEADO" in motivo
        assert ultimo is not None

        # Tentativa de registrar deve lançar ValueError
        with pytest.raises(ValueError, match="BLOQUEADO"):
            AtendimentoService.registrar_atendimento(joao.id)

def test_liberacao_outro_mes(app):
    with app.app_context():
        # Arrange - Maria Aparecida recebeu cesta no mês anterior, liberada para este mês
        maria = Familia.query.filter_by(cpf="123.456.789-00").first()

        # Act
        pode, motivo, ultimo = AtendimentoService.pode_receber_cesta(maria.id)

        # Assert
        assert pode is True
        assert "LIBERADA" in motivo

        # Registrar atendimento com sucesso
        novo_atend = AtendimentoService.registrar_atendimento(maria.id)
        assert novo_atend.id is not None
        assert novo_atend.familia_id == maria.id

        # Logo após registrar, deve estar bloqueada para novo registro no mesmo mês
        pode_novamente, _, _ = AtendimentoService.pode_receber_cesta(maria.id)
        assert pode_novamente is False

def test_calculo_validade_alerta_critico():
    # Arrange
    hoje = date(2026, 11, 5)
    validade_proxima = hoje + timedelta(days=5)

    # Act
    status = EstoqueService.calcular_status_validade(validade_proxima, data_referencia=hoje)

    # Assert
    assert status['codigo'] == 'critico'
    assert status['dias'] == 5
    assert 'CRÍTICO' in status['label']

def test_calculo_validade_regular_e_vencido():
    hoje = date(2026, 11, 5)
    
    # Regular (> 7 dias)
    status_regular = EstoqueService.calcular_status_validade(hoje + timedelta(days=45), data_referencia=hoje)
    assert status_regular['codigo'] == 'regular'

    # Vencido (< 0 dias)
    status_vencido = EstoqueService.calcular_status_validade(hoje - timedelta(days=3), data_referencia=hoje)
    assert status_vencido['codigo'] == 'vencido'
    assert 'VENCIDO' in status_vencido['label']
