# -*- coding: utf-8 -*-
from backend.api.auth import auth_bp
from backend.api.diagnosis import diagnosis_bp
from backend.api.patient import patient_bp
from backend.api.user import user_bp
from backend.api.system import system_bp
from backend.api.llm import llm_bp

all_blueprints = [auth_bp, diagnosis_bp, patient_bp, user_bp, system_bp, llm_bp]
