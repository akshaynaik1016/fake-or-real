"""Add cases, sources, cited claims, cross-source findings and revision snapshots."""
from alembic import op
from app.models.all_models import InvestigationCase,InvestigationSource,ExtractedClaim,CrossSourceFinding,CaseAssessmentRevision
revision='0002_multi_source_cases'
down_revision='0001_investigations'
branch_labels=None
depends_on=None
TABLES=[InvestigationCase,InvestigationSource,ExtractedClaim,CrossSourceFinding,CaseAssessmentRevision]
def upgrade():
    for model in TABLES:model.__table__.create(bind=op.get_bind(),checkfirst=True)
def downgrade():
    for model in reversed(TABLES):model.__table__.drop(bind=op.get_bind(),checkfirst=True)
