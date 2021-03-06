"""empty message

Revision ID: aef646628979
Revises: cfaa29daf61f
Create Date: 2020-04-05 20:40:26.269097

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aef646628979'
down_revision = 'cfaa29daf61f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    #op.add_column('Artist', sa.Column('seeking_venue', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###
