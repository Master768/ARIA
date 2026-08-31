import os
import sys
import importlib
import inspect
import logging
from typing import Dict, Any, List, Optional, Type
from agents.skills.base_skill import BaseSkill

logger = logging.getLogger("skill_registry")

class SkillRegistry:
    """
    IDE-Like Plugin Skill Registry & Dynamic Loader.
    Auto-discovers skills from agents/skills/impl/ and resolves optimal skill plugins at runtime.
    """

    def __init__(self, auto_discover: bool = True):
        self._skills: Dict[str, BaseSkill] = {}
        if auto_discover:
            self.auto_discover_skills()

    def register_skill(self, skill: BaseSkill) -> None:
        """Register a single skill instance."""
        if not isinstance(skill, BaseSkill):
            raise TypeError(f"Skill must inherit from BaseSkill, got {type(skill)}")
        self._skills[skill.name.lower()] = skill
        logger.info(f"Registered Plugin Skill: '{skill.name}' ({skill.category})")

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """Retrieve a registered skill by name."""
        return self._skills.get(name.lower())

    def list_skills(self) -> List[Dict[str, Any]]:
        """List metadata for all registered skills."""
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
                "required_libraries": skill.required_libraries
            }
            for skill in self._skills.values()
        ]

    def resolve_best_skills(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None, top_k: int = 2) -> List[BaseSkill]:
        """
        Dynamically evaluate task query against all registered skills and return the top-K matching skills.
        """
        scored_skills = []
        for name, skill in self._skills.items():
            try:
                score = skill.can_handle(query, dataset_meta)
                if score > 0.1:
                    scored_skills.append((skill, score))
            except Exception as e:
                logger.warning(f"Error evaluating skill '{name}': {e}")

        scored_skills.sort(key=lambda x: x[1], reverse=True)
        matched = [skill for skill, score in scored_skills[:top_k]]
        return matched

    def auto_discover_skills(self) -> None:
        """Dynamically load and instantiate all Skill plugins from agents/skills/impl/."""
        impl_dir = os.path.join(os.path.dirname(__file__), "impl")
        if not os.path.exists(impl_dir):
            os.makedirs(impl_dir, exist_ok=True)
            return

        for fname in os.listdir(impl_dir):
            if fname.endswith(".py") and not fname.startswith("__"):
                mod_name = f"agents.skills.impl.{fname[:-3]}"
                try:
                    module = importlib.import_module(mod_name)
                    for item_name in dir(module):
                        obj = getattr(module, item_name)
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseSkill) and 
                            obj is not BaseSkill and 
                            not inspect.isabstract(obj)):
                            try:
                                instance = obj()
                                self.register_skill(instance)
                            except Exception as inst_err:
                                logger.warning(f"Failed to instantiate skill '{item_name}': {inst_err}")
                except Exception as mod_err:
                    logger.warning(f"Failed to import skill module '{mod_name}': {mod_err}")
