"""
Analyzery dla 9 teorii humoru
"""
from .base import BaseAnalyzer
from .setup_punchline import SetupPunchlineAnalyzer
from .incongruity import IncongruityAnalyzer
from .semantic_shift import SemanticShiftAnalyzer
from .timing import TimingAnalyzer
from .absurd_escalation import AbsurdEscalationAnalyzer
from .psychoanalysis import PsychoanalysisAnalyzer
from .archetype import ArchetypeAnalyzer
from .humor_atoms import HumorAtomsAnalyzer
from .reverse_engineering import ReverseEngineeringAnalyzer

__all__ = [
    'BaseAnalyzer',
    'SetupPunchlineAnalyzer',
    'IncongruityAnalyzer',
    'SemanticShiftAnalyzer',
    'TimingAnalyzer',
    'AbsurdEscalationAnalyzer',
    'PsychoanalysisAnalyzer',
    'ArchetypeAnalyzer',
    'HumorAtomsAnalyzer',
    'ReverseEngineeringAnalyzer',
]

