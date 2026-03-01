"""
Multi-agent pipeline for premium site generation.

Agents:
  - DesignDirector: Creates a Design Brief (layout, color direction, typography, copy voice, animations)
  - AnimationChoreographer: Maps GSAP effects to each section/element
  - QualityReviewer: Validates generated HTML against the Design Brief
"""

from app.services.agents.design_director import DesignDirector
from app.services.agents.animation_choreographer import AnimationChoreographer
from app.services.agents.quality_reviewer import QualityReviewer

__all__ = ["DesignDirector", "AnimationChoreographer", "QualityReviewer"]
