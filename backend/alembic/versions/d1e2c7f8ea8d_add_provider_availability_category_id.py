"""add provider availability category_id

Revision ID: d1e2c7f8ea8d
Revises: 3316d7944cba
Create Date: 2026-08-10 02:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd1e2c7f8ea8d'
down_revision = '3316d7944cba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'provider_availability',
        sa.Column(
            'category_id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        )
    )
    op.create_foreign_key(
        'fk_provider_availability_category_id_categories',
        'provider_availability',
        'categories',
        ['category_id'],
        ['id'],
    )
    op.create_unique_constraint(
        'uq_provider_category_availability',
        'provider_availability',
        ['provider_id', 'category_id', 'day_of_week', 'start_time', 'end_time'],
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_provider_category_availability',
        'provider_availability',
        type_='unique',
    )
    op.drop_constraint(
        'fk_provider_availability_category_id_categories',
        'provider_availability',
        type_='foreignkey',
    )
    op.drop_column('provider_availability', 'category_id')
