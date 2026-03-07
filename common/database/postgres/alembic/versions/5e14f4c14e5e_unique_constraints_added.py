"""unique_constraints_added.

Revision ID: 5e14f4c14e5e
Revises: 9d3bdbde9b69
Create Date: 2026-03-07 20:15:20.205640

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "5e14f4c14e5e"
down_revision: Union[str, Sequence[str], None] = "9d3bdbde9b69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
