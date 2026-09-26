from app.schemas.skill_schema import SkillAction, SkillDefinition


class SkillRegistry:
    def __init__(self) -> None:
        skills = [
            SkillDefinition(
                skill_id="device_control",
                name="设备控制",
                description="控制 Android 设备的音量、亮度和蓝牙。",
                requires_confirmation=False,
                actions=[
                    SkillAction(
                        name="set_volume",
                        description="设置设备音量",
                        execution_target="android",
                        parameters={
                            "level": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 15,
                            }
                        },
                    ),
                    SkillAction(
                        name="set_brightness",
                        description="设置屏幕亮度",
                        execution_target="android",
                        parameters={
                            "value": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100,
                            }
                        },
                    ),
                    SkillAction(
                        name="set_bluetooth",
                        description="开启或关闭蓝牙",
                        execution_target="android",
                        parameters={
                            "enabled": {"type": "boolean"}
                        },
                    ),
                ],
            ),
            SkillDefinition(
                skill_id="rule_management",
                name="规则管理",
                description="创建并管理自动化规则。",
                requires_confirmation=True,
                actions=[
                    SkillAction(
                        name="create_rule",
                        description="创建自动化规则",
                        execution_target="backend",
                        parameters={
                            "trigger": {"type": "object"},
                            "action": {"type": "object"},
                        },
                    ),
                ],
            ),
        ]

        self._skills = {
            skill.skill_id: skill
            for skill in skills
        }

    def list_skills(self) -> list[SkillDefinition]:
        return list(self._skills.values())

    def get_skill(self, skill_id: str) -> SkillDefinition | None:
        return self._skills.get(skill_id)

    @property
    def supported_actions(self) -> set[str]:
        return {
            action.name
            for skill in self._skills.values()
            for action in skill.actions
        }
    def find_action(
        self,
        action_name: str,
    ) -> tuple[SkillDefinition, SkillAction] | None:
        for skill in self._skills.values():
            for action in skill.actions:
                if action.name == action_name:
                    return skill, action

        return None


skill_registry = SkillRegistry()