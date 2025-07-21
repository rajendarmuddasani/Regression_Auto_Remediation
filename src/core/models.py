"""
Database models for Regression Auto-Remediation System

Author: Rajendar Muddasani
Date: July 21, 2025
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.dialects.oracle import CLOB, NUMBER
from src.core.database import Base

class RegressionDaily(Base):
    """Model for REGRESSION_DAILY table - Test programs enabled for daily regression"""
    __tablename__ = "REGRESSION_DAILY"
    
    id = Column(NUMBER, primary_key=True, autoincrement=True)
    test_program_name = Column(String(255), nullable=False)
    module_name = Column(String(100), nullable=False)
    baseline_version = Column(String(50), nullable=True)
    enabled_flag = Column(String(1), default='Y', nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RegressionDaily(id={self.id}, program='{self.test_program_name}', module='{self.module_name}')>"

class RegressionResults(Base):
    """Model for REGRESSION_RESULTS table - Daily regression results and analysis"""
    __tablename__ = "REGRESSION_RESULTS"
    
    id = Column(NUMBER, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    test_program_name = Column(String(255), nullable=False)
    execution_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(20), nullable=False)  # PASS/FAIL/ERROR
    error_message = Column(CLOB, nullable=True)
    log_file_path = Column(String(500), nullable=True)
    analysis_results = Column(CLOB, nullable=True)  # JSON format
    
    def __repr__(self):
        return f"<RegressionResults(id={self.id}, session='{self.session_id}', status='{self.status}')>"

class LearnedPatterns(Base):
    """Model for LEARNED_PATTERNS table - ML model learned patterns (stored as JSON)"""
    __tablename__ = "LEARNED_PATTERNS"
    
    id = Column(NUMBER, primary_key=True, autoincrement=True)
    pattern_name = Column(String(255), nullable=False)
    issue_type = Column(String(100), nullable=False)
    solution_type = Column(String(100), nullable=False)
    pattern_data = Column(CLOB, nullable=False)  # JSON format
    confidence_score = Column(Float, nullable=False, default=0.0)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<LearnedPatterns(id={self.id}, pattern='{self.pattern_name}', confidence={self.confidence_score})>"

class AppliedSolutions(Base):
    """Model for APPLIED_SOLUTIONS table - History of automatically applied solutions"""
    __tablename__ = "APPLIED_SOLUTIONS"
    
    id = Column(NUMBER, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    issue_pattern_id = Column(Integer, nullable=False)  # FK to LEARNED_PATTERNS
    solution_applied = Column(CLOB, nullable=False)
    application_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    validation_status = Column(String(20), nullable=False)  # SUCCESS/FAILED/PENDING
    validation_results = Column(CLOB, nullable=True)
    
    def __repr__(self):
        return f"<AppliedSolutions(id={self.id}, session='{self.session_id}', status='{self.validation_status}')>"

class BaselineChanges(Base):
    """Model for BASELINE_CHANGES table - Baseline change tracking"""
    __tablename__ = "BASELINE_CHANGES"
    
    id = Column(NUMBER, primary_key=True, autoincrement=True)
    test_program_name = Column(String(255), nullable=False)
    old_baseline = Column(String(50), nullable=True)
    new_baseline = Column(String(50), nullable=False)
    change_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    change_description = Column(Text, nullable=True)
    impact_analysis = Column(CLOB, nullable=True)  # JSON format
    
    def __repr__(self):
        return f"<BaselineChanges(id={self.id}, program='{self.test_program_name}', baseline='{self.new_baseline}')>"
