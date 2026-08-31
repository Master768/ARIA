import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("consistency_validator")

class CrossNodeConsistencyValidator:
    """
    Layer 7: Validates cross-node state consistency and flags unstated metric contradictions.
    Ensures downstream nodes do not report contradicting facts without explicitly declaring filters.
    """

    @classmethod
    def validate(cls, node_outputs: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        issues = []
        score = 1.0

        if not isinstance(node_outputs, dict) or len(node_outputs) <= 1:
            return True, 1.0, []

        # Extract numerical claims from node outputs
        node_claims: Dict[str, List[Tuple[str, float]]] = {}
        for nid, nres in node_outputs.items():
            text = nres.get("output", "") if isinstance(nres, dict) else str(nres)
            
            # Find numbers associated with 'score', 'max', 'top', 'mean', 'total'
            matches = re.findall(r"\b(score|max|top|mean|total|rating)\b\s*[:=]?\s*([0-9]+\.?[0-9]*)", text, re.IGNORECASE)
            claims = []
            for metric, val_str in matches:
                try:
                    claims.append((metric.lower(), float(val_str)))
                except ValueError:
                    pass
            node_claims[nid] = claims

        # Check for unstated contradictions between nodes
        nids = list(node_outputs.keys())
        for i in range(len(nids) - 1):
            nid_a = nids[i]
            nid_b = nids[i+1]
            text_b = node_outputs[nid_b].get("output", "") if isinstance(node_outputs[nid_b], dict) else str(node_outputs[nid_b])

            # If Node B reports a smaller maximum score than Node A without explaining filtering
            claims_a = dict(node_claims.get(nid_a, []))
            claims_b = dict(node_claims.get(nid_b, []))

            if "score" in claims_a and "score" in claims_b:
                val_a = claims_a["score"]
                val_b = claims_b["score"]
                if val_b < val_a and not any(kw in text_b.lower() for kw in ["filter", "where", "position", "group", "subset", "only"]):
                    issues.append(
                        f"Cross-node inconsistency: `{nid_b}` reported a smaller top score ({val_b}) than prior `{nid_a}` ({val_a}) "
                        f"without explicitly declaring a filter or subset transformation."
                    )
                    score -= 0.4

        passed = score >= 0.75 and len(issues) == 0
        return passed, max(0.0, score), issues
