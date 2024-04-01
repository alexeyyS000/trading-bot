"""databasecreate

Revision ID: 9f65775a6155
Revises: 
Create Date: 2024-03-28 00:55:02.985152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f65775a6155"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "futures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=9), nullable=False),
        sa.Column("dayly_volume", sa.Integer(), nullable=True),
        sa.Column("history_correlation", sa.Float(), nullable=True),
        sa.Column("current_correlation", sa.Float(), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.Column("updated", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "klines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.String(), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("qouto_asset_vol", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["symbol"],
            ["futures.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("klines")
    op.drop_table("futures")
    # ### end Alembic commands ###
