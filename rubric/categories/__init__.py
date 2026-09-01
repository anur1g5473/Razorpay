"""Rubric categories package."""

from rubric.categories.fraud import CATEGORY as FRAUD_CATEGORY
from rubric.categories.pnr import CATEGORY as PNR_CATEGORY
from rubric.categories.defective import CATEGORY as DEFECTIVE_CATEGORY
from rubric.categories.refund import CATEGORY as REFUND_CATEGORY
from rubric.categories.duplicate import CATEGORY as DUPLICATE_CATEGORY
from rubric.categories.subscription import CATEGORY as SUBSCRIPTION_CATEGORY

ALL_CATEGORIES = {
    FRAUD_CATEGORY["category_id"]: FRAUD_CATEGORY,
    PNR_CATEGORY["category_id"]: PNR_CATEGORY,
    DEFECTIVE_CATEGORY["category_id"]: DEFECTIVE_CATEGORY,
    REFUND_CATEGORY["category_id"]: REFUND_CATEGORY,
    DUPLICATE_CATEGORY["category_id"]: DUPLICATE_CATEGORY,
    SUBSCRIPTION_CATEGORY["category_id"]: SUBSCRIPTION_CATEGORY,
}
