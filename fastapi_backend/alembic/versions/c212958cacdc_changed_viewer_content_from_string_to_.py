"""changed viewer content from string to JSON type

Revision ID: c212958cacdc
Revises: 2e5d7b05f8f3
Create Date: 2025-06-23 11:56:08.672755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c212958cacdc'
down_revision: Union[str, None] = '2e5d7b05f8f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('ALTER TABLE viewer ALTER COLUMN content TYPE JSON USING content::json')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('ALTER TABLE viewer ALTER COLUMN content TYPE VARCHAR USING content::text')
