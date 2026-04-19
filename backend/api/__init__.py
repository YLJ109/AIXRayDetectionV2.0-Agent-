"""API蓝图注册"""
from api.auth import auth_bp
from api.users import users_bp
from api.patients import patients_bp
from api.diagnose import diagnose_bp
from api.reports import reports_bp
from api.batch import batch_bp
from api.triage import triage_bp
from api.chat import chat_bp
from api.model_weights import model_weights_bp
from api.llm_configs import llm_configs_bp
from api.llm import llm_bp
from api.audit import audit_bp
from api.settings import settings_bp
from api.dashboard import dashboard_bp
from api.approvals import approvals_bp

all_blueprints = [
    auth_bp, users_bp, patients_bp, diagnose_bp,
    reports_bp, batch_bp, triage_bp, chat_bp,
    model_weights_bp, llm_configs_bp, llm_bp, audit_bp,
    settings_bp, dashboard_bp, approvals_bp,
]
