"""Map points for users

Revision ID: 7c8467fc62bf
Revises: 3a6a82a754a6
Create Date: 2024-09-11 01:13:37.917250

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7c8467fc62bf"
down_revision: Union[str, None] = "3a6a82a754a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "map_points",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("City", "Department", "Country", name="type"),
            nullable=False,
        ),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("map_point_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            None, "map_points", ["map_point_id"], ["id"]
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_column("map_point_id")

    op.drop_table("map_points")
    # ### end Alembic commands ###
