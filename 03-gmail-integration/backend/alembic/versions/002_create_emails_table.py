"""create emails table

Revision ID: 002
Revises: 001
Create Date: 2023-08-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'emails',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('gmail_id', sa.String(255), nullable=False),
        sa.Column('thread_id', sa.String(255), nullable=True),
        sa.Column('subject', sa.String(1000), nullable=True),
        sa.Column('sender', sa.String(500), nullable=False),
        sa.Column('recipient', sa.String(500), nullable=True),
        sa.Column('content', sa.Text, nullable=True),
        sa.Column('snippet', sa.String(500), nullable=True),
        sa.Column('received_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('labels', JSON, nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('is_spam', sa.Boolean, default=False, nullable=False),
        sa.Column('cluster_id', sa.Integer, nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes
    op.create_index('idx_email_user_gmail', 'emails', ['user_id', 'gmail_id'], unique=True)
    op.create_index('idx_email_user_received', 'emails', ['user_id', 'received_date'])
    op.create_index('idx_email_sender_category', 'emails', ['sender', 'category'])
    op.create_index('idx_email_spam_processed', 'emails', ['is_spam', 'processed_at'])
    op.create_index('idx_email_subject', 'emails', ['subject'])
    op.create_index('idx_email_category', 'emails', ['category'])
    op.create_index('idx_email_thread_id', 'emails', ['thread_id'])
    
    # Add full-text search indexes for PostgreSQL
    op.execute(
        """
        CREATE INDEX idx_email_content_fts ON emails 
        USING gin(to_tsvector('english', content));
        """
    )
    
    op.execute(
        """
        CREATE INDEX idx_email_subject_fts ON emails 
        USING gin(to_tsvector('english', subject));
        """
    )


def downgrade():
    # Drop full-text search indexes first
    op.execute("DROP INDEX IF EXISTS idx_email_content_fts;")
    op.execute("DROP INDEX IF EXISTS idx_email_subject_fts;")
    
    # Drop regular indexes
    op.drop_index('idx_email_thread_id', table_name='emails')
    op.drop_index('idx_email_category', table_name='emails')
    op.drop_index('idx_email_subject', table_name='emails')
    op.drop_index('idx_email_spam_processed', table_name='emails')
    op.drop_index('idx_email_sender_category', table_name='emails')
    op.drop_index('idx_email_user_received', table_name='emails')
    op.drop_index('idx_email_user_gmail', table_name='emails')
    
    # Drop table
    op.drop_table('emails')