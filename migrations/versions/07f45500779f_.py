"""empty message

Revision ID: 07f45500779f
Revises: ef62f14a31e6
Create Date: 2019-03-06 20:30:46.834508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07f45500779f'
down_revision = 'ef62f14a31e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('single_lesson', sa.Column('views', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('single_lesson', 'views')
    # ### end Alembic commands ###
