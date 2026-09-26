from collections.abc import Iterator
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

from app.schemas.rule_schema import Rule


class RuleRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        # 默认位置：项目根目录/data/rules.db
        project_root = Path(__file__).resolve().parents[2]
        self.db_path = (
            Path(db_path)
            if db_path is not None
            else project_root / "data" / "rules.db"
        )

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """创建并管理一次 SQLite 连接。正常结束时提交，异常时回滚。"""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        """首次使用时创建规则表和用户索引。"""
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS rules (
                    rule_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    trigger_json TEXT NOT NULL,
                    action_json TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1
                        CHECK (enabled IN (0, 1)),
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_rules_user_created
                ON rules (user_id, created_at)
                """
            )

    def create(self, rule: Rule) -> Rule:
        """保存一条规则。rule_id 由上层 RuleEngine 生成。"""
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO rules (
                    rule_id,
                    user_id,
                    name,
                    trigger_json,
                    action_json,
                    enabled,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rule.rule_id,
                    rule.user_id,
                    rule.name,
                    json.dumps(rule.trigger, ensure_ascii=False),
                    json.dumps(rule.action, ensure_ascii=False),
                    int(rule.enabled),
                    rule.created_at.isoformat(),
                ),
            )

        return rule

    def get(self, rule_id: str, user_id: str) -> Rule | None:
        """按规则 ID 和用户 ID 查询，避免跨用户读取。"""
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM rules
                WHERE rule_id = ? AND user_id = ?
                """,
                (rule_id, user_id),
            ).fetchone()

        return self._row_to_rule(row) if row else None

    def list_by_user(self, user_id: str) -> list[Rule]:
        """查询某个用户的全部规则，最近创建的排在前面。"""
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM rules
                WHERE user_id = ?
                ORDER BY created_at DESC, rule_id
                """,
                (user_id,),
            ).fetchall()

        return [self._row_to_rule(row) for row in rows]

    def update(self, rule: Rule) -> Rule | None:
        """更新规则内容；只有该用户自己的规则才会被更新。"""
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE rules
                SET name = ?,
                    trigger_json = ?,
                    action_json = ?,
                    enabled = ?,
                    created_at = ?
                WHERE rule_id = ? AND user_id = ?
                """,
                (
                    rule.name,
                    json.dumps(rule.trigger, ensure_ascii=False),
                    json.dumps(rule.action, ensure_ascii=False),
                    int(rule.enabled),
                    rule.created_at.isoformat(),
                    rule.rule_id,
                    rule.user_id,
                ),
            )

        return rule if cursor.rowcount == 1 else None

    def update_enabled(
        self,
        rule_id: str,
        user_id: str,
        enabled: bool,
    ) -> Rule | None:
        """启用或禁用规则，并返回更新后的规则。"""
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE rules
                SET enabled = ?
                WHERE rule_id = ? AND user_id = ?
                """,
                (int(enabled), rule_id, user_id),
            )

            if cursor.rowcount != 1:
                return None

            row = connection.execute(
                """
                SELECT *
                FROM rules
                WHERE rule_id = ? AND user_id = ?
                """,
                (rule_id, user_id),
            ).fetchone()

        return self._row_to_rule(row) if row else None

    def delete(self, rule_id: str, user_id: str) -> bool:
        """删除规则；只允许删除指定用户自己的规则。"""
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM rules
                WHERE rule_id = ? AND user_id = ?
                """,
                (rule_id, user_id),
            )

        return cursor.rowcount == 1

    @staticmethod
    def _row_to_rule(row: sqlite3.Row) -> Rule:
        """把 SQLite 行还原成 Pydantic Rule 模型。"""
        return Rule(
            rule_id=row["rule_id"],
            user_id=row["user_id"],
            name=row["name"],
            trigger=json.loads(row["trigger_json"]),
            action=json.loads(row["action_json"]),
            enabled=bool(row["enabled"]),
            created_at=row["created_at"],
        )