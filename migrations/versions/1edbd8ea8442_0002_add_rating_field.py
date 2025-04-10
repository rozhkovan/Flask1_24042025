"""0002 Add rating field

Revision ID: 1edbd8ea8442
Revises: e200097c33d4
Create Date: 2025-03-30 20:27:34.740941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1edbd8ea8442'
down_revision = 'e200097c33d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating', sa.Integer(), server_default='1', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.drop_column('rating')

    # ### end Alembic commands ###
