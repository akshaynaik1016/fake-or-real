"""Transparent log-odds updates, heuristic unless calibrated likelihoods are supplied."""
import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FusionConfig:
    prior: float = 0.25
    likelihood_ratios: dict[str, float] = field(default_factory=dict)
    calibration_reference: str | None = None

    def __post_init__(self):
        if not 0 < self.prior < 1:
            raise ValueError("Prior must be between zero and one")
        if any(not math.isfinite(v) or v <= 0 for v in self.likelihood_ratios.values()):
            raise ValueError("Likelihood ratios must be positive and finite")
        if self.likelihood_ratios and not self.calibration_reference:
            raise ValueError("Calibrated likelihoods require a calibration reference")


HEURISTIC_RATIOS = {"critical": 8.0, "high": 3.0, "moderate": 1.6, "low": 1.1, "verified": 0.8}


def fuse_evidence(evidence: list[dict], checks: list[dict], config: FusionConfig | None = None) -> dict:
    config = config or FusionConfig()
    # Independently safe even when callers have not normalized duplicate rows.
    evidence = list({e["id"]: e for e in evidence}.values())
    completed = sum(c.get("completed", False) for c in checks)
    coverage = round(100 * completed / len(checks)) if checks else 0
    unknowns = [c["name"] + ": " + c.get("reason", "not completed") for c in checks if not c.get("completed")]
    eligible = [e for e in evidence if e.get("origin") not in {
        "SYNTHETIC", "EXTERNAL_SOURCE", "AI_INTERPRETATION"} and
        e.get("verification_status") not in {"UNAVAILABLE", "UNKNOWN", "SYNTHETIC"}]
    bayesian = bool(eligible and config.likelihood_ratios) and all(
        e["category"] in config.likelihood_ratios for e in eligible)
    mode = "BAYESIAN" if bayesian else "HEURISTIC"
    def ratio(e):
        if bayesian:
            return config.likelihood_ratios[e["category"]]
        # Confidence is a heuristic reliability weight, not a statistical likelihood.
        return HEURISTIC_RATIOS.get(e["severity"], 1.0) ** e.get("confidence", 0.5)
    groups: dict[str, list[dict]] = {}
    for e in eligible:
        groups.setdefault(e["correlation_group"], []).append(e)
    selected = {max(rows, key=lambda e: (abs(math.log(ratio(e))), e["id"]))["id"] for rows in groups.values()}
    log_odds = math.log(config.prior / (1 - config.prior))
    updates = []
    for e in evidence:
        used = e["id"] in selected
        lr = ratio(e) if used else 1.0
        before = 100 / (1 + math.exp(-max(-40, min(40, log_odds))))
        log_odds += math.log(lr)
        after = 100 / (1 + math.exp(-max(-40, min(40, log_odds))))
        updates.append({"evidence_id": e["id"], "correlation_group": e["correlation_group"],
            "included": used, "likelihood_ratio" if bayesian else "heuristic_multiplier": round(lr, 6),
            "before": round(before, 2), "after": round(after, 2),
            "reason": "Strongest observation in correlation group" if used else
                "Excluded: correlated, synthetic, unavailable or unverified external interpretation"})
    score = round(100 / (1 + math.exp(-max(-40, min(40, log_odds)))))
    sufficient = len(groups) >= 2 or any(e["severity"] in {"critical", "high"} for e in eligible)
    level = "INSUFFICIENT_INFORMATION" if not sufficient else (
        "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MODERATE" if score >= 35 else "LOW")
    contradiction = any(any(r["severity"] == "verified" for r in rows) and
                        any(r["severity"] in {"high", "critical"} for r in rows) for rows in groups.values())
    reliability = sum(e.get("confidence", 0) for e in eligible if e["id"] in selected) / max(1, len(groups))
    confidence = round(min(95, len(groups) * 18) * reliability * (0.7 if contradiction else 1))
    if contradiction:
        unknowns.append("Conflicting observations in the same correlation group require independent verification")
    return {"assessment_mode": mode, "risk_level": level, "risk_score": score if eligible else None,
        "confidence": confidence, "evidence_coverage": coverage,
        "prior": config.prior, "calibration_reference": config.calibration_reference,
        "evidence_updates": updates,
        "supporting_evidence": [e["id"] for e in eligible if ratio(e) > 1],
        "contradicting_evidence": [e["id"] for e in eligible if ratio(e) < 1],
        "unknowns": unknowns, "explanation": [
            "Log odds begin at the configured prior; only one observation per correlation group contributes.",
            "Heuristic risk score and evidence confidence are not calibrated probabilities." if not bayesian else
            "Likelihoods supplied by caller; validity depends on the cited calibration dataset.",
            "Missing checks and search silence never count as safety evidence."]}
