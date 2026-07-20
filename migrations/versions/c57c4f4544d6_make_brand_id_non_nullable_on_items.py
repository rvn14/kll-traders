"""make_brand_id_non_nullable_on_items

Revision ID: c57c4f4544d6
Revises: a34bb365012d
Create Date: 2026-07-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c57c4f4544d6'
down_revision: Union[str, Sequence[str], None] = 'a34bb365012d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure "No Brand" exists
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT id FROM brands WHERE name = 'No brand'")).first()
    if not result:
        connection.execute(sa.text("INSERT INTO brands (name, is_active, created_at) VALUES ('No brand', true, NOW())"))
        result = connection.execute(sa.text("SELECT id FROM brands WHERE name = 'No brand'")).first()
    
    no_brand_id = result[0]
    
    # Update existing items with null brand_id
    connection.execute(sa.text(f"UPDATE items SET brand_id = {no_brand_id} WHERE brand_id IS NULL"))

    op.alter_column('items', 'brand_id',
               existing_type=sa.INTEGER(),
               nullable=False)


def downgrade() -> None:
    op.alter_column('items', 'brand_id',
               existing_type=sa.INTEGER(),
               nullable=True)
