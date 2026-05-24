"""Initial schema — users, wardrobe_items, outfit_recommendations

Revision ID: 001_initial
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


def upgrade():
    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("style_archetype", sa.String, nullable=True),
        sa.Column("body_type", sa.String, nullable=True),
        sa.Column("skin_tone", sa.String, nullable=True),
        sa.Column("gender_expression", sa.String, nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("city", sa.String, nullable=True),
        sa.Column("preferences", JSON, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── wardrobe_items ──────────────────────────────────────────────────────
    op.create_table(
        "wardrobe_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category", sa.String, nullable=False),
        sa.Column("subcategory", sa.String, nullable=True),
        sa.Column("colors", JSON, default=[]),
        sa.Column("attributes", JSON, default={}),
        sa.Column("style_tags", JSON, default=[]),
        sa.Column("season", JSON, default=[]),
        sa.Column("formality_score", sa.Float, default=0.5),
        sa.Column("warmth_score", sa.Float, default=0.5),
        sa.Column("image_url", sa.String, nullable=False),
        sa.Column("thumbnail_url", sa.String, nullable=True),
        sa.Column("qdrant_id", sa.String, unique=True, nullable=True),
        sa.Column("brand", sa.String, nullable=True),
        sa.Column("purchase_price", sa.Float, nullable=True),
        sa.Column("notes", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("times_worn", sa.Integer, default=0),
        sa.Column("last_worn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_wardrobe_items_user_id", "wardrobe_items", ["user_id"])

    # ── outfit_recommendations ──────────────────────────────────────────────
    op.create_table(
        "outfit_recommendations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_ids", JSON, nullable=False),
        sa.Column("item_roles", JSON, default={}),
        sa.Column("confidence_score", sa.Float, default=0.0),
        sa.Column("weather_comfort_score", sa.Float, default=0.0),
        sa.Column("trend_score", sa.Float, default=0.0),
        sa.Column("mood_match_score", sa.Float, default=0.0),
        sa.Column("context", JSON, default={}),
        sa.Column("style_explanation", sa.String, nullable=True),
        sa.Column("color_palette", JSON, default=[]),
        sa.Column("feedback", sa.String, nullable=True),
        sa.Column("feedback_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_recommendations_user_id", "outfit_recommendations", ["user_id"])


def downgrade():
    op.drop_table("outfit_recommendations")
    op.drop_table("wardrobe_items")
    op.drop_table("users")
