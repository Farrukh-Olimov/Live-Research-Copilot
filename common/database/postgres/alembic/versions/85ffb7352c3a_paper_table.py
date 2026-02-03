"""paper_table.

Revision ID: 85ffb7352c3a
Revises: 79f7a6b2b5bc
Create Date: 2026-02-03 23:25:11.485831

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "85ffb7352c3a"
down_revision: Union[str, Sequence[str], None] = "79f7a6b2b5bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
