import sys
from pathlib import Path
import json

# Ensure project root is on PYTHONPATH when running the test directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.domain.semantic_type_detector import detect_semantic_types


domain_model = {
    "entities": [
        {
            "name": "Order",
            "fields": [
                {"name": "orderId", "type": "UUID"},
                {"name": "email", "type": "String"},
                {"name": "amount", "type": "BigDecimal"},
                {"name": "currency", "type": "String"},
                {"name": "startDate", "type": "LocalDate"},
                {"name": "endDate", "type": "LocalDate"}
            ]
        },
        {
            "name": "OrderItem",
            "fields": [
                {"name": "orderItemId", "type": "UUID"},
                {"name": "price", "type": "BigDecimal"},
                {"name": "quantity", "type": "Integer"}
            ]
        },
        {
            "name": "InvoicePaid",
            "fields": [
                {"name": "invoiceId", "type": "UUID"},
                {"name": "amount", "type": "BigDecimal"}
            ]
        }
    ]
}

result = detect_semantic_types(domain_model)

print(json.dumps(result, indent=2))
