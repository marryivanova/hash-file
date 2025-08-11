"""create tables users and files

Revision ID: 2cfdac5fc0c1
Revises:
Create Date: 2025-08-08 15:36:44.734649

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2cfdac5fc0c1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=80), nullable=False, unique=True),
        sa.Column("password", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    op.create_table(
        "files",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_files_user_id"),
        sa.UniqueConstraint("hash", name="uq_files_hash"),
    )

    op.create_index("idx_files_user_id", "files", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_files_user_id", table_name="files")
    op.drop_table("files")
    op.drop_table("users")
