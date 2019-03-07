"""empty message

Revision ID: d8dd5daa7066
Revises: 07f45500779f
Create Date: 2019-03-07 17:05:15.197562

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8dd5daa7066'
down_revision = '07f45500779f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('single_lesson', sa.Column('date_added', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('single_lesson', 'date_added')
    # ### end Alembic commands ###
