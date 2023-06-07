"""change cols

Revision ID: 5938540aeff8
Revises: 0edd3f3c8a41
Create Date: 2023-06-02 14:34:23.473406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5938540aeff8'
down_revision = '0edd3f3c8a41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('Artist', 'website')
    op.add_column('Venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'website_link')
    op.add_column('Artist', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###