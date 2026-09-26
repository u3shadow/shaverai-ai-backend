from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.rule_schema import (
    DeviceEvent,
    Rule,
    RuleCreateRequest,
    RuleEnableRequest,
)
from app.services.rule_engine import RuleEngine


router = APIRouter(prefix="/rules", tags=["Rules"])
rule_engine = RuleEngine()


@router.post(
    "",
    response_model=Rule,
    status_code=status.HTTP_201_CREATED,
)
def create_rule(request: RuleCreateRequest):
    try:
        return rule_engine.create_rule(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("", response_model=list[Rule])
def list_rules(user_id: str = Query(...)):
    try:
        return rule_engine.list_rules(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/match")
def match_event(event: DeviceEvent):
    try:
        return rule_engine.match_event(event)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{rule_id}/enabled", response_model=Rule)
def update_rule_enabled(
    rule_id: str,
    request: RuleEnableRequest,
):
    rule = rule_engine.set_enabled(
        rule_id=rule_id,
        user_id=request.user_id,
        enabled=request.enabled,
    )

    if rule is None:
        raise HTTPException(
            status_code=404,
            detail="规则不存在，或不属于该用户",
        )

    return rule


@router.delete("/{rule_id}")
def delete_rule(
    rule_id: str,
    user_id: str = Query(...),
):
    deleted = rule_engine.delete_rule(
        rule_id=rule_id,
        user_id=user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="规则不存在，或不属于该用户",
        )

    return {
        "deleted": True,
        "rule_id": rule_id,
    }