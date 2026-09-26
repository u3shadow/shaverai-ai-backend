from fastapi import APIRouter, HTTPException

from app.schemas.skill_schema import SkillDefinition
from app.services.skill_registry import skill_registry


router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("", response_model=list[SkillDefinition])
def list_skills():
    return skill_registry.list_skills()


@router.get("/{skill_id}", response_model=SkillDefinition)
def get_skill(skill_id: str):
    skill = skill_registry.get_skill(skill_id)

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail=f"Skill '{skill_id}' not found",
        )

    return skill