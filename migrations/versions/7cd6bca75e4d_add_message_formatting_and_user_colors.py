"""Add message formatting and user colors

Revision ID: 7cd6bca75e4d
Revises: 
Create Date: 2025-08-17 01:21:46.886785

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7cd6bca75e4d'
down_revision = None   # if you already have prior migrations, set this properly
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('message_type', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('user_color', sa.String(length=7), nullable=True))


def downgrade():
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_column('user_color')
        batch_op.drop_column('message_type')
