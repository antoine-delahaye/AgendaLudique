"""empty message

Revision ID: 6d8ae8cfe827
Revises: 2e8fc54d09c2
Create Date: 2021-01-17 03:07:31.879304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d8ae8cfe827'
down_revision = '2e8fc54d09c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('statistics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('avg_complexity', sa.Integer(), nullable=True),
    sa.Column('avg_playtime', sa.Integer(), nullable=True),
    sa.Column('avg_nb_players', sa.Integer(), nullable=True),
    sa.Column('frequency', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('users', sa.Column('statistics_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'statistics', ['statistics_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'statistics_id')
    op.drop_table('statistics')
    # ### end Alembic commands ###