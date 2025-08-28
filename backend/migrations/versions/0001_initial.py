from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('market_bars',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(length=32), index=True),
        sa.Column('ts', sa.DateTime(timezone=True), index=True),
        sa.Column('open', sa.Numeric(18,8)),
        sa.Column('high', sa.Numeric(18,8)),
        sa.Column('low', sa.Numeric(18,8)),
        sa.Column('close', sa.Numeric(18,8)),
        sa.Column('volume', sa.Numeric(24,8)),
    )
    op.create_table('feature_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(length=32), index=True),
        sa.Column('ts', sa.DateTime(timezone=True), index=True),
        sa.Column('features', sa.JSON()),
    )
    op.create_table('signals',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(length=32), index=True),
        sa.Column('ts', sa.DateTime(timezone=True), index=True),
        sa.Column('strategy', sa.String(length=64), index=True),
        sa.Column('strength', sa.Numeric(18,8)),
        sa.Column('direction', sa.String(length=8)),
    )
    op.create_table('orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('client_order_id', sa.String(length=64), unique=True, index=True),
        sa.Column('symbol', sa.String(length=32), index=True),
        sa.Column('ts', sa.DateTime(timezone=True), index=True),
        sa.Column('side', sa.String(length=8)),
        sa.Column('qty', sa.Numeric(18,8)),
        sa.Column('price', sa.Numeric(18,8)),
        sa.Column('status', sa.String(length=32)),
    )
    op.create_table('executions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), index=True),
        sa.Column('symbol', sa.String(length=32), index=True),
        sa.Column('ts', sa.DateTime(timezone=True), index=True),
        sa.Column('qty', sa.Numeric(18,8)),
        sa.Column('price', sa.Numeric(18,8)),
    )
    op.create_table('positions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(length=32), unique=True, index=True),
        sa.Column('qty', sa.Numeric(18,8)),
        sa.Column('avg_price', sa.Numeric(18,8)),
    )
    op.create_table('model_versions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=64), index=True),
        sa.Column('version', sa.String(length=32), index=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )

def downgrade():
    op.drop_table('model_versions')
    op.drop_table('positions')
    op.drop_table('executions')
    op.drop_table('orders')
    op.drop_table('signals')
    op.drop_table('feature_snapshots')
    op.drop_table('market_bars')
