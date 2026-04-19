"""add feedback table

Revision ID: a1b2c3d4e5f6
Revises: c64fa8281228
Create Date: 2026-04-20 00:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'c64fa8281228'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create feedback table."""
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('report_id', sa.String(50), sa.ForeignKey('reports.report_id'), nullable=True),
        # ── Quantitative questions (Q1–Q14) ─────────────────────────────────
        # Q1  Accuracy – Likert 1-5
        sa.Column('q1_overall_accuracy', sa.Integer(), nullable=True),
        # Q2  Personality type accuracy – Likert 1-5
        sa.Column('q2_personality_accuracy', sa.Integer(), nullable=True),
        # Q3  Trait scores accuracy – Likert 1-5
        sa.Column('q3_trait_scores_accuracy', sa.Integer(), nullable=True),
        # Q4  Self-understanding usefulness – Likert 1-5
        sa.Column('q4_self_understanding', sa.Integer(), nullable=True),
        # Q5  Report clarity – Likert 1-5
        sa.Column('q5_report_clarity', sa.Integer(), nullable=True),
        # Q6  Trust in the test – Likert 1-5
        sa.Column('q6_trust', sa.Integer(), nullable=True),
        # Q7  Surprise / novelty – Likert 1-5
        sa.Column('q7_novelty', sa.Integer(), nullable=True),
        # Q8  Consistency: Extraversion – Yes/No  (1=Yes, 0=No)
        sa.Column('q8_ei_agreement', sa.Integer(), nullable=True),
        # Q9  Consistency: Dominant intelligence – Yes/No  (1=Yes, 0=No)
        sa.Column('q9_mi_agreement', sa.Integer(), nullable=True),
        # Q10 Consistency: Enneagram type – Yes/No  (1=Yes, 0=No)
        sa.Column('q10_enneagram_agreement', sa.Integer(), nullable=True),
        # Q11 Test length / fatigue – Likert 1-5
        sa.Column('q11_test_length', sa.Integer(), nullable=True),
        # Q12 Likelihood to recommend (NPS-style) – Likert 1-5
        sa.Column('q12_recommend', sa.Integer(), nullable=True),
        # Q13 Would take again – Yes/No  (1=Yes, 0=No)
        sa.Column('q13_retake', sa.Integer(), nullable=True),
        # Q14 Overall satisfaction – Likert 1-5
        sa.Column('q14_satisfaction', sa.Integer(), nullable=True),
        # Q15 Open-ended text
        sa.Column('q15_open_text', sa.Text(), nullable=True),
        # ── Metadata ────────────────────────────────────────────────────────
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop feedback table."""
    op.drop_table('feedback')
