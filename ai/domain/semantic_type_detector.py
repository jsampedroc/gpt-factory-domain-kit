# ai/domain/semantic_type_detector.py
"""
Semantic Type Detector

This module enriches the domain model produced by the LLM by detecting
semantic field types (email, phone, money, etc.) and converting them
into domain ValueObjects automatically.

It acts as a lightweight semantic rule engine sitting between:
LLM domain reasoning → architecture inventory generation.
"""


import re
from ai.domain.domain_knowledge_cache import update_knowledge


# ------------------------------------------------
# Primitive types that may be upgraded to VO
# ------------------------------------------------
PRIMITIVE_TYPES = {
    "string",
    "str",
    "text",
    "varchar",
    "uuid",
    "bigdecimal",
    "double",
    "float",
    "int",
    "integer",
    "long",
}

# ------------------------------------------------
# Built-in language / Java types that should NOT
# be treated as unknown domain types
# ------------------------------------------------
BUILTIN_TYPES = {
    "UUID",
    "String",
    "Integer",
    "Long",
    "Double",
    "Float",
    "BigDecimal",
    "Boolean",
    "LocalDate",
    "LocalDateTime",
    "Instant",
}


# ------------------------------------------------
# ValueObject registry
# Defines the canonical VO structure
# ------------------------------------------------
VALUE_OBJECT_REGISTRY = {
    "Email": {
        "type": "String",
        "validation": "EMAIL_REGEX",
        "description": "RFC-like email validation"
    },

    "PhoneNumber": {
        "type": "String",
        "validation": "PHONE_E164",
        "description": "International phone number validation"
    },

    "Money": {
        "type": "BigDecimal",
        "validation": "NON_NEGATIVE",
        "description": "Monetary value must be >= 0"
    },

    "Percentage": {
        "type": "BigDecimal",
        "validation": "PERCENTAGE_RANGE",
        "description": "Percentage between 0 and 100"
    },

    "CurrencyCode": {
        "type": "String",
        "validation": "ISO_CURRENCY",
        "description": "ISO-4217 currency code"
    },
    "DateRange": {
        "type": "LocalDate",
        "validation": "DATE_RANGE",
        "description": "Start date must be before end date"
    },

    "Address": {
        "type": "String",
        "validation": "NON_EMPTY",
        "description": "Postal address value object"
    },

    "GeoLocation": {
        "type": "Double",
        "validation": "LAT_LONG",
        "description": "Latitude/Longitude pair"
    }
}


# ------------------------------------------------
# Semantic detection rules (regex based)
# ------------------------------------------------
SEMANTIC_RULES = [

    (re.compile(r"email|mail", re.I), "Email"),

    (re.compile(r"phone|telephone|mobile|tel", re.I), "PhoneNumber"),

    (re.compile(r"price|amount|total|cost|fee|balance", re.I), "Money"),

    (re.compile(r"percent|percentage|rate|discount", re.I), "Percentage"),

    (re.compile(r"currency|currencycode", re.I), "CurrencyCode"),

    (re.compile(r"startdate|fromdate|begindate", re.I), "DateRange"),
    (re.compile(r"enddate|todate|finishdate", re.I), "DateRange"),

    (re.compile(r"address|street|city|postal|zipcode", re.I), "Address"),

    (re.compile(r"latitude|longitude|lat|lon|geolocation|geo", re.I), "GeoLocation"),
]


def detect_aggregate_boundaries(dm):

    graph = dm.get("domain_graph", {})
    cardinalities = graph.get("cardinalities", [])

    aggregates = {}

    for rel in cardinalities:

        if rel.get("type") == "one_to_many":

            root = rel.get("from")
            member = rel.get("to")

            if root not in aggregates:
                aggregates[root] = []

            aggregates[root].append(member)

    detected = []

    for root, members in aggregates.items():

        for m in members:
            detected.append({
                "aggregate": root,
                "member": m
            })

    dm["aggregates"] = detected

    return dm

# ------------------------------------------------
# Helpers
# ------------------------------------------------
def _normalize_type(t):
    if not t:
        return ""
    return str(t).lower()


def _is_upgradeable_type(t):
    nt = _normalize_type(t)
    return nt in PRIMITIVE_TYPES


# ------------------------------------------------
# Core semantic enrichment
# ------------------------------------------------
def detect_semantic_types(domain_model):
    """
    Enrich domain_model by:
    - detecting semantic field types
    - converting primitive types into ValueObjects
    - registering new ValueObjects if needed
    """

    # Some LLMs wrap the model as { "domain_model": {...} }
    dm = domain_model.get("domain_model", domain_model)

    entities = dm.get("entities", [])

    # existing VO definitions
    existing_vos = {
        vo["name"]: vo for vo in dm.get("value_objects", [])
    }

    for entity in entities:

        for field in entity.get("fields", []):

            field_name = field.get("name", "")
            field_type = field.get("type", "")

            # Normalize field name for better semantic matching
            normalized_name = (
                field_name.replace("_", "")
                .replace("-", "")
                .strip()
            )

            for pattern, vo_name in SEMANTIC_RULES:

                if not pattern.search(normalized_name):
                    continue

                # Only upgrade primitive-like types
                if not _is_upgradeable_type(field_type):
                    continue

                # Replace primitive with semantic VO
                field["type"] = vo_name

                # Register VO if not already defined
                if vo_name not in existing_vos:

                    registry_def = VALUE_OBJECT_REGISTRY.get(
                        vo_name,
                        {"type": "String"},
                    )

                    existing_vos[vo_name] = {
                        "name": vo_name,
                        "fields": [
                            {
                                "name": "value",
                                "type": registry_def["type"],
                            }
                        ],
                        "validation": registry_def.get("validation"),
                        "description": registry_def.get("description"),
                    }

                break

    # ------------------------------------------------
    # Domain pattern detection (compound concepts)
    # ------------------------------------------------
    for entity in entities:

        fields = entity.get("fields", [])
        field_names = {f.get("name", "").lower(): f for f in fields}

        # Detect MonetaryAmount (amount + currency)
        if any(k in field_names for k in ["amount", "price", "total"]) and any(
            k in field_names for k in ["currency", "currencycode"]
        ):
            existing_vos.setdefault(
                "MonetaryAmount",
                {
                    "name": "MonetaryAmount",
                    "fields": [
                        {"name": "amount", "type": "BigDecimal"},
                        {"name": "currency", "type": "CurrencyCode"},
                    ],
                    "description": "Amount with currency"
                },
            )

        # Detect GeoPoint (latitude + longitude)
        if "latitude" in field_names and "longitude" in field_names:
            existing_vos.setdefault(
                "GeoPoint",
                {
                    "name": "GeoPoint",
                    "fields": [
                        {"name": "latitude", "type": "Double"},
                        {"name": "longitude", "type": "Double"},
                    ],
                    "description": "Geographic coordinate"
                },
            )

        # Detect DateRange (start + end date pair)
        if any(k in field_names for k in ["startdate", "fromdate"]) and any(
            k in field_names for k in ["enddate", "todate"]
        ):
            existing_vos.setdefault(
                "DateRange",
                {
                    "name": "DateRange",
                    "fields": [
                        {"name": "start", "type": "LocalDate"},
                        {"name": "end", "type": "LocalDate"},
                    ],
                    "description": "Date interval"
                },
            )

    # ------------------------------------------------
    # Aggregate detection (DDD heuristic)
    # ------------------------------------------------
    aggregates = []

    entity_names = {e.get("name", "").lower(): e for e in entities}

    for entity in entities:

        name = entity.get("name", "")
        lname = name.lower()

        # Detect common aggregate patterns
        if lname.endswith("item") or lname.endswith("line"):

            root_name = lname.replace("item", "").replace("line", "").strip()

            if root_name in entity_names:
                aggregates.append({
                    "aggregate": entity_names[root_name]["name"],
                    "member": name
                })

        if lname.endswith("detail"):

            root_name = lname.replace("detail", "").strip()

            if root_name in entity_names:
                aggregates.append({
                    "aggregate": entity_names[root_name]["name"],
                    "member": name
                })

    if aggregates:
        dm.setdefault("aggregates", []).extend(aggregates)

    # ------------------------------------------------
    # Domain Event detection (DDD heuristic)
    # ------------------------------------------------
    domain_events = []

    EVENT_PATTERNS = [
        re.compile(r".*created$", re.I),
        re.compile(r".*registered$", re.I),
        re.compile(r".*paid$", re.I),
        re.compile(r".*scheduled$", re.I),
        re.compile(r".*cancelled$", re.I),
        re.compile(r".*completed$", re.I),
        re.compile(r".*failed$", re.I),
    ]

    for entity in entities:

        name = entity.get("name", "")
        lname = name.lower()

        for pattern in EVENT_PATTERNS:
            if pattern.match(lname):
                domain_events.append({
                    "event": name,
                    "description": f"Domain event {name}"
                })
                break

    if domain_events:
        dm.setdefault("domain_events", []).extend(domain_events)

    # ------------------------------------------------
    # Domain Graph Builder
    # ------------------------------------------------
    domain_graph = {
        "entities": [],
        "value_objects": [],
        "aggregates": dm.get("aggregates", []),
        "events": dm.get("domain_events", []),
        "relations": [],
        "cardinalities": []
    }

    entity_lookup = {e.get("name"): e for e in entities}

    for entity in entities:
        name = entity.get("name")
        domain_graph["entities"].append(name)

        for field in entity.get("fields", []):
            ftype = field.get("type")

            if ftype in entity_lookup:
                domain_graph["relations"].append({
                    "from": name,
                    "to": ftype,
                    "type": "entity_reference"
                })

            if ftype in existing_vos:
                domain_graph["relations"].append({
                    "from": name,
                    "to": ftype,
                    "type": "value_object"
                })

    # ------------------------------------------------
    # Relation Cardinality Detection
    # ------------------------------------------------
    for agg in dm.get("aggregates", []):
        root = agg.get("aggregate")
        member = agg.get("member")

        if root and member:
            domain_graph["cardinalities"].append({
                "from": root,
                "to": member,
                "type": "one_to_many"
            })

    # heuristic detection based on plural field names
    for entity in entities:
        name = entity.get("name")

        for field in entity.get("fields", []):
            field_name = field.get("name", "").lower()
            field_type = field.get("type")

            if field_type in entity_lookup:

                # plural hint (items, orders, children, etc.)
                if field_name.endswith("s"):
                    domain_graph["cardinalities"].append({
                        "from": name,
                        "to": field_type,
                        "type": "one_to_many"
                    })

    for vo in existing_vos.keys():
        domain_graph["value_objects"].append(vo)


    dm["domain_graph"] = domain_graph

    dm = detect_aggregate_boundaries(dm)

    # ------------------------------------------------
    # Bounded Context Detection (DDD heuristic)
    # ------------------------------------------------
    contexts = {}

    CONTEXT_HINTS = {
        "billing": ["invoice", "payment", "price", "amount", "fee", "billing"],
        "customer": ["customer", "client", "user", "account", "profile"],
        "scheduling": ["appointment", "schedule", "booking", "reservation"],
        "inventory": ["product", "item", "stock", "catalog"],
        "education": ["student", "child", "teacher", "course", "class"],
    }

    for entity in entities:
        name = entity.get("name", "")
        lname = name.lower()

        for ctx, keywords in CONTEXT_HINTS.items():
            if any(k in lname for k in keywords):
                contexts.setdefault(ctx, []).append(name)
                break

    if contexts:
        dm["bounded_contexts"] = [
            {
                "name": ctx,
                "entities": ents
            }
            for ctx, ents in contexts.items()
        ]


    # ------------------------------------------------
    # Aggregate Behavior Synthesizer
    # ------------------------------------------------
    aggregate_behaviors = []

    for agg in dm.get("aggregates", []):
        root = agg.get("aggregate")
        member = agg.get("member")

        # Collection management behaviors
        aggregate_behaviors.append({
            "aggregate": root,
            "behavior": f"add{member}",
            "description": f"Add {member} to {root}"
        })

        aggregate_behaviors.append({
            "aggregate": root,
            "behavior": f"remove{member}",
            "description": f"Remove {member} from {root}"
        })

        # Quantity update pattern
        aggregate_behaviors.append({
            "aggregate": root,
            "behavior": f"update{member}",
            "description": f"Update {member} within {root}"
        })

    # Lifecycle behaviors inferred from entity names
    LIFECYCLE_PATTERNS = [
        ("create", "Create aggregate"),
        ("update", "Update aggregate"),
        ("delete", "Delete aggregate"),
        ("cancel", "Cancel aggregate"),
        ("complete", "Complete process"),
        ("pay", "Register payment"),
    ]

    aggregate_roots = {a.get("aggregate") for a in dm.get("aggregates", [])}

    for root in aggregate_roots:
        for name, description in LIFECYCLE_PATTERNS:
            aggregate_behaviors.append({
                "aggregate": root,
                "behavior": f"{name}{root}",
                "description": f"{description} {root}"
            })

    # Event‑driven behaviors
    for event in dm.get("domain_events", []):
        event_name = event.get("event")

        for root in aggregate_roots:
            aggregate_behaviors.append({
                "aggregate": root,
                "behavior": f"on{event_name}",
                "description": f"Handle domain event {event_name}"
            })

    if aggregate_behaviors:
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for b in aggregate_behaviors:
            key = (b.get("aggregate"), b.get("behavior"))
            if key not in seen:
                seen.add(key)
                unique.append(b)

        dm["aggregate_behaviors"] = unique

    # ------------------------------------------------
    # Invariant Detection (Domain Validation Rules)
    # ------------------------------------------------
    invariants = []

    for entity in entities:
        name = entity.get("name")
        fields = entity.get("fields", [])

        field_map = {f.get("name","").lower(): f for f in fields}

        # startDate < endDate
        if "startdate" in field_map and "enddate" in field_map:
            invariants.append({
                "entity": name,
                "rule": "startDate_before_endDate",
                "description": "startDate must be before endDate"
            })

        # amount >= 0
        if any(k in field_map for k in ["amount","price","total","cost"]):
            invariants.append({
                "entity": name,
                "rule": "amount_non_negative",
                "description": "amount must be >= 0"
            })

        # percentage 0..100
        if any(k in field_map for k in ["percent","percentage","rate","discount"]):
            invariants.append({
                "entity": name,
                "rule": "percentage_range",
                "description": "percentage must be between 0 and 100"
            })

    if invariants:
        dm["invariants"] = invariants

    # ------------------------------------------------
    # Domain Consistency Validator
    # ------------------------------------------------
    consistency_issues = []

    entity_names = {e.get("name") for e in entities}

    # Entity must have Id field
    for entity in entities:
        fields = entity.get("fields", [])
        if not any(f.get("name","").lower().endswith("id") for f in fields):
            consistency_issues.append({
                "type": "missing_id",
                "entity": entity.get("name"),
                "description": "Entity has no Id field"
            })

    # Aggregate member must reference root
    for agg in dm.get("aggregates", []):
        root = agg.get("aggregate")
        member = agg.get("member")

        member_entity = next((e for e in entities if e.get("name") == member), None)

        if member_entity:
            member_fields = [f.get("type") for f in member_entity.get("fields", [])]

            if root not in member_fields:
                consistency_issues.append({
                    "type": "aggregate_reference_missing",
                    "aggregate": root,
                    "member": member,
                    "description": f"{member} does not reference aggregate root {root}"
                })

    # Entity references unknown type
    for entity in entities:
        for field in entity.get("fields", []):
            ftype = field.get("type")

            # Skip primitive and built‑in types
            if _normalize_type(ftype) in PRIMITIVE_TYPES or ftype in BUILTIN_TYPES:
                continue

            if ftype not in entity_names and ftype not in existing_vos:
                consistency_issues.append({
                    "type": "unknown_type",
                    "entity": entity.get("name"),
                    "field": field.get("name"),
                    "type_name": ftype,
                    "description": f"Unknown type {ftype}"
                })

    if consistency_issues:
        dm["consistency_issues"] = consistency_issues

    # ------------------------------------------------
    # Domain Architecture Planner
    # ------------------------------------------------
    architecture_plan = {
        "aggregate_roots": [],
        "entities": [],
        "value_objects": list(existing_vos.keys()),
        "repositories": [],
        "services": []
    }

    # Aggregate roots come from detected aggregates
    aggregate_roots = {a.get("aggregate") for a in dm.get("aggregates", [])}

    for entity in entities:
        name = entity.get("name")

        if name in aggregate_roots:
            architecture_plan["aggregate_roots"].append(name)
            architecture_plan["repositories"].append(f"{name}Repository")
            architecture_plan["services"].append(f"{name}Service")
        else:
            architecture_plan["entities"].append(name)

    dm["architecture_plan"] = architecture_plan

    # ensure deterministic order
    dm["value_objects"] = sorted(
        existing_vos.values(),
        key=lambda v: v.get("name", "")
    )

    # ------------------------------------------------
    # Learning Signal Extraction (Self‑Improving Factory)
    # ------------------------------------------------
    learning_signals = {
        "entities": [e.get("name") for e in entities],
        "value_objects": list(existing_vos.keys()),
        "aggregates": [
            (a.get("aggregate"), a.get("member"))
            for a in dm.get("aggregates", [])
        ],
        "events": [
            e.get("event") for e in dm.get("domain_events", [])
        ],
        "contexts": [
            c.get("name") for c in dm.get("bounded_contexts", [])
        ] if dm.get("bounded_contexts") else [],
        "invariants": [
            (i.get("entity"), i.get("rule"))
            for i in dm.get("invariants", [])
            if isinstance(i, dict)
        ] if dm.get("invariants") else [],
    }

    # Attach signals so the knowledge cache can learn from them
    dm["learning_signals"] = learning_signals

    # Update domain knowledge cache so the factory learns from this model
    update_knowledge(dm)

    return domain_model