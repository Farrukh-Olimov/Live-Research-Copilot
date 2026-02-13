"""rename sources to datasources and update papers.

Revision ID: 221b80d2b098
Revises: fe6e36ec75c8
Create Date: 2026-02-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "221b80d2b098"
down_revision: Union[str, Sequence[str], None] = "fe6e36ec75c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- 1. Rename sources → datasources
    op.rename_table("sources", "datasources")
    op.create_unique_constraint("uq_datasources_name", "datasources", ["name"])

    # --- 2. Domains: add datasource_id FK
    op.add_column(
        "domains",
        sa.Column("datasource_id", sa.UUID(), nullable=False),
    )
    op.create_index("ix_domains_datasource_id", "domains", ["datasource_id"])
    op.create_foreign_key(
        "fk_domains_datasource",
        "domains",
        "datasources",
        ["datasource_id"],
        ["id"],
    )

    # --- 3. Papers: rename source_id → datasource_id
    op.drop_constraint("papers_source_id_fkey", "papers", type_="foreignkey")
    op.alter_column("papers", "source_id", new_column_name="datasource_id")
    op.create_foreign_key(
        "fk_papers_datasource",
        "papers",
        "datasources",
        ["datasource_id"],
        ["id"],
    )

    # --- 4. Rename url → paper_identifier
    op.drop_constraint("papers_url_key", "papers", type_="unique")
    op.alter_column("papers", "url", new_column_name="paper_identifier")
    op.create_unique_constraint(
        "uq_papers_paper_identifier", "papers", ["paper_identifier"]
    )

    # --- 5. Add abstract column
    op.add_column(
        "papers",
        sa.Column("abstract", sa.Text(), nullable=False),
    )

    # --- 6. Title: VARCHAR → TEXT
    op.alter_column(
        "papers",
        "title",
        existing_type=sa.VARCHAR(),
        type_=sa.Text(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # --- 1. Revert title
    op.alter_column(
        "papers",
        "title",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(),
        nullable=False,
    )

    # --- 2. Drop abstract
    op.drop_column("papers", "abstract")

    # --- 3. Rename paper_identifier → url
    op.drop_constraint("uq_papers_paper_identifier", "papers", type_="unique")
    op.alter_column("papers", "paper_identifier", new_column_name="url")
    op.create_unique_constraint("papers_url_key", "papers", ["url"])

    # --- 4. Rename datasource_id → source_id
    op.drop_constraint("fk_papers_datasource", "papers", type_="foreignkey")
    op.alter_column("papers", "datasource_id", new_column_name="source_id")
    op.create_foreign_key(
        "papers_source_id_fkey",
        "papers",
        "datasources",
        ["source_id"],
        ["id"],
    )

    # --- 5. Domains cleanup
    op.drop_constraint("fk_domains_datasource", "domains", type_="foreignkey")
    op.drop_index("ix_domains_datasource_id", table_name="domains")
    op.drop_column("domains", "datasource_id")

    # --- 6. Rename datasources → sources
    op.drop_constraint("uq_datasources_name", "datasources", type_="unique")
    op.rename_table("datasources", "sources")
