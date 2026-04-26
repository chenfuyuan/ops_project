"""create outline generation tables

The schema keeps one active skeleton and one aggregate outline per seed, while
volumes and chapters use cascade deletes so regenerated skeletons do not leave
orphaned outline fragments behind.
"""

from alembic import op
import sqlalchemy as sa

revision = "20260426_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create outline generation tables in dependency order."""
    # Seed stores user-authored creative inputs; application logs must not emit these columns.
    op.create_table(
        "outline_seeds",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("genre", sa.String(length=50), nullable=False),
        sa.Column("protagonist", sa.Text(), nullable=False),
        sa.Column("core_conflict", sa.Text(), nullable=False),
        sa.Column("story_direction", sa.Text(), nullable=False),
        sa.Column("additional_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    # Unique seed_id enforces the service rule that a seed has one current skeleton.
    op.create_table(
        "outline_skeletons",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("seed_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["seed_id"], ["outline_seeds.id"]),
        sa.UniqueConstraint("seed_id"),
    )
    # Volumes are owned by skeletons and are removed when a skeleton is regenerated.
    op.create_table(
        "outline_skeleton_volumes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("skeleton_id", sa.String(length=36), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("turning_point", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["skeleton_id"], ["outline_skeletons.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("skeleton_id", "sequence"),
    )
    # Chapter summaries are replaceable per volume; stale flags preserve author-visible history after edits.
    op.create_table(
        "outline_chapter_summaries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("volume_id", sa.String(length=36), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["volume_id"], ["outline_skeleton_volumes.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("volume_id", "sequence"),
    )
    # Outline is the seed-level aggregate status persisted for fast retrieval.
    op.create_table(
        "outlines",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("seed_id", sa.String(length=36), nullable=False),
        sa.Column("skeleton_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["seed_id"], ["outline_seeds.id"]),
        sa.ForeignKeyConstraint(["skeleton_id"], ["outline_skeletons.id"]),
        sa.UniqueConstraint("seed_id"),
    )


def downgrade() -> None:
    """Drop outline generation tables in reverse dependency order."""
    # Drop in reverse dependency order to satisfy foreign key constraints.
    op.drop_table("outlines")
    op.drop_table("outline_chapter_summaries")
    op.drop_table("outline_skeleton_volumes")
    op.drop_table("outline_skeletons")
    op.drop_table("outline_seeds")
