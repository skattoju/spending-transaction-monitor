"""merge upstream and location heads

Revision ID: c2241f95e582
Revises: 5b7ab65a1fe2, location_distance_func
Create Date: 2025-09-23 18:03:11.162146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2241f95e582'
down_revision = ('5b7ab65a1fe2', 'location_distance_func')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
