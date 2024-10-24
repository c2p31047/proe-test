"""empty message

Revision ID: d518eede2442
Revises: 7b28a4beae72
Create Date: 2024-10-15 13:51:10.061243

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd518eede2442'
down_revision = '7b28a4beae72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=False)

    with op.batch_alter_table('stock', schema=None) as batch_op:
        batch_op.alter_column('quantity',
               existing_type=mysql.VARCHAR(length=100),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.alter_column('unit',
               existing_type=mysql.VARCHAR(length=100),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.alter_column('location',
               existing_type=mysql.VARCHAR(length=100),
               type_=sa.String(length=255),
               existing_nullable=True)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.alter_column('address',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.alter_column('work_address',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.alter_column('work_address',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=True)
        batch_op.alter_column('address',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=False)

    with op.batch_alter_table('stock', schema=None) as batch_op:
        batch_op.alter_column('location',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=100),
               existing_nullable=True)
        batch_op.alter_column('unit',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=100),
               existing_nullable=True)
        batch_op.alter_column('quantity',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=100),
               existing_nullable=True)

    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.alter_column('name',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=False)

    # ### end Alembic commands ###
