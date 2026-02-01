"""changed source to datasource.

Revision ID: 79f7a6b2b5bc
Revises: fe6e36ec75c8
Create Date: 2026-02-01 17:05:32.371389

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "79f7a6b2b5bc"
down_revision: Union[str, Sequence[str], None] = "fe6e36ec75c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
