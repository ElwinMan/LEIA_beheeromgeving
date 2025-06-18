"""removed *_snippets suffixes

Revision ID: 18304a17575c
Revises: 00102ad97c0b
Create Date: 2025-06-17 14:19:05.908122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '18304a17575c'
down_revision: Union[str, None] = '00102ad97c0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("layer_snippet", "layer")
    op.rename_table("tool_snippet", "tool")
    op.rename_table("group_snippet", "group")
    op.rename_table("viewer_snippet", "viewer")

    op.alter_column("digital_twin_layer_association", "layer_snippet_id", new_column_name="layer_id")
    op.alter_column("digital_twin_tool_association", "tool_snippet_id", new_column_name="tool_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table("layer", "layer_snippet")
    op.rename_table("tool", "tool_snippet")
    op.rename_table("group", "group_snippet")
    op.rename_table("viewer", "viewer_snippet")

    op.alter_column("digital_twin_layer_association", "layer_id", new_column_name="layer_snippet_id")
    op.alter_column("digital_twin_tool_association", "tool_id", new_column_name="tool_snippet_id")

    
    # ### end Alembic commands ###
