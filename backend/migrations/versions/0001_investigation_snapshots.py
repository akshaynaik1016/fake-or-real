"""Add investigation snapshots and execution history without changing legacy data."""
from alembic import op
from sqlalchemy import inspect
from app.models.all_models import InvestigationState, InvestigationExecution

revision = "0001_investigations"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Works after the existing create_all startup and on a pre-upgrade database.
    bind = op.get_bind()
    InvestigationState.__table__.create(bind=bind, checkfirst=True)
    InvestigationExecution.__table__.create(bind=bind, checkfirst=True)


def downgrade():
    # Explicit opt-in downgrade only: drops new investigation data, keeps scans.
    bind = op.get_bind()
    InvestigationExecution.__table__.drop(bind=bind, checkfirst=True)
    InvestigationState.__table__.drop(bind=bind, checkfirst=True)
