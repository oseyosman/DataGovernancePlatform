"""Add rag_chunks and rag_query_logs

Revision ID: b7c1d2e3f4a5
Revises: 9a3202c19019
Create Date: 2026-10-18 12:45:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7c1d2e3f4a5'
down_revision = '9a3202c19019'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rag_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('annual_report_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('page', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['annual_report_id'], ['annual_reports.id']),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('rag_chunks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_rag_chunks_annual_report_id'), ['annual_report_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_rag_chunks_company_id'), ['company_id'], unique=False)

    op.create_table(
        'rag_query_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('question', sa.String(length=500), nullable=False),
        sa.Column('abstained', sa.Boolean(), nullable=False),
        sa.Column('abstain_reason', sa.String(length=100), nullable=True),
        sa.Column('num_passages', sa.Integer(), nullable=False),
        sa.Column('filtered_passages', sa.Integer(), nullable=False),
        sa.Column('top_score', sa.Float(), nullable=True),
        sa.Column('coverage', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=False),
        sa.Column('output_tokens', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('rag_query_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_rag_query_logs_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_rag_query_logs_user_id'), ['user_id'], unique=False)


def downgrade():
    with op.batch_alter_table('rag_query_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rag_query_logs_user_id'))
        batch_op.drop_index(batch_op.f('ix_rag_query_logs_created_at'))
    op.drop_table('rag_query_logs')
    with op.batch_alter_table('rag_chunks', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rag_chunks_company_id'))
        batch_op.drop_index(batch_op.f('ix_rag_chunks_annual_report_id'))
    op.drop_table('rag_chunks')
