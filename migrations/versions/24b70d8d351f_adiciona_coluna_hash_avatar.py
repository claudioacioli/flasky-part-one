"""Adiciona coluna hash avatar

Revision ID: 24b70d8d351f
Revises: b6eb1b17b147
Create Date: 2019-08-29 06:48:33.139900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24b70d8d351f'
down_revision = 'b6eb1b17b147'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('avatar_hash', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'avatar_hash')
    # ### end Alembic commands ###
