"""
CivicTrace - Minutes parser for Cessnock / NSW-style council minutes.

Extracts:
- MOTION / Moved / Seconded / RESOLVED blocks
- FOR / AGAINST councillor voting lists
- Conflict of interest / disclosure declarations
"""

import re
from typing import List, Dict, Any, Tuple


def _clean(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalise_councillor(name: str) -> str:
    name = name.strip().rstrip(".,;")
    if not name:
        return ""
    lower = name.lower()
    if lower in ("total", "for", "against", "nil", "carried", "unanimously", "councillor", "cr"):
        return ""
    if lower.startswith("councillor "):
        name = name[11:].strip()
    if not name.lower().startswith("cr ") and not name.lower().startswith("mayor"):
        name = f"Cr {name}"
    return name


def _extract_outcome(block: str) -> str:
    upper = block.upper()
    if "CARRIED UNANIMOUSLY" in upper or "CARRIED UNANIMOUS" in upper:
        return "Carried"
    if re.search(r"\bCARRIED\b", upper):
        return "Carried"
    if re.search(r"\bLOST\b", upper):
        return "Lost"
    if "WITHDRAWN" in upper:
        return "Withdrawn"
    if "DEFERRED" in upper or "LAID ON THE TABLE" in upper:
        return "Deferred"
    if "RESOLVED" in upper:
        return "Carried"
    return "Carried"


def _extract_mover_seconder(block: str) -> Tuple[str, str]:
    mover = ""
    seconder = ""

    m = re.search(r"Moved:\s*(?:Councillor\s+)?([A-Za-z\-']+)", block, re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        if name.lower() not in ("seconded", "councillor", "cr", "resolved"):
            mover = name if name.lower().startswith("cr") else f"Cr {name}"

    s = re.search(r"Seconded:\s*(?:Councillor\s+)?([A-Za-z\-']+)", block, re.IGNORECASE)
    if s:
        name = s.group(1).strip()
        if name.lower() not in ("moved", "councillor", "cr", "resolved"):
            seconder = name if name.lower().startswith("cr") else f"Cr {name}"

    return mover, seconder


def _extract_resolution_text(block: str) -> str:
    m = re.search(
        r"RESOLVED\s*(?:that|:)?\s*(.+?)(?=(?:FOR\s*AGAINST|FOR\s*\n|CARRIED|LOST|MOTION\b|$))",
        block,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        text = m.group(1).strip()
        text = re.sub(r"\s+", " ", text)
        text = text.strip(" .")
        if text.lower().startswith("that "):
            text = text[5:].strip()
        return text[:900]

    m2 = re.search(
        r"\d{2,4}\s+(.+?)(?=(?:FOR\s*AGAINST|CARRIED|LOST|MOTION\b|$))",
        block,
        re.DOTALL,
    )
    if m2:
        return re.sub(r"\s+", " ", m2.group(1)).strip()[:700]
    return ""


def _extract_votes(block: str) -> Dict[str, str]:
    """
    Pull councillor names from FOR / AGAINST sections.
    Handles the common Cessnock layout where names appear after 'FOR AGAINST'
    and before 'Total (n)' or 'CARRIED'.
    """
    votes: Dict[str, str] = {}

    # Try to isolate the voting section
    vote_section = ""
    m = re.search(
        r"(?:FOR\s*AGAINST|FOR\s+AGAINST)(.+?)(?:CARRIED|LOST|Total\s*\(|MOTION\b|$)",
        block,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        vote_section = m.group(1)
    else:
        # Fallback: look for lines with Councillor names near the end of the block
        vote_section = block[-800:] if len(block) > 800 else block

    if not vote_section:
        return votes

    # Collect all councillor-looking names
    names = re.findall(
        r"(?:Councillor|Cr\.?|Mayor)\s+([A-Za-z\-']+)",
        vote_section,
        re.IGNORECASE,
    )

    # Also catch bare surnames that appear in typical vote lists
    # (Cessnock often lists them under the FOR column)
    extra = re.findall(r"\b([A-Z][a-z]{2,15})\b", vote_section)
    known_surnames = {
        "Dixon", "Dunne", "Harrington", "Hill", "Jurd", "King", "Lea",
        "Franklin", "Bangura", "Palmowski", "Pascoe", "Hawkins", "Watton",
        "Mason", "Madden", "Grine", "Suvaal",
    }
    for n in extra:
        if n in known_surnames:
            names.append(n)

    # Deduplicate while preserving order
    seen = set()
    clean_names = []
    for n in names:
        nn = _normalise_councillor(n)
        if nn and nn.lower() not in seen:
            seen.add(nn.lower())
            clean_names.append(nn)

    # Heuristic: if the outcome is unanimous / all on one side, assign all to "For"
    upper = block.upper()
    if "CARRIED UNANIMOUSLY" in upper or "CARRIED UNANIMOUS" in upper or re.search(r"Total\s*\(\d+\)\s*Total\s*\(0\)", upper):
        for name in clean_names:
            votes[name] = "For"
    else:
        # Without reliable column separation we still record the names as having voted
        # and default to For (user can edit later). Better than losing the data.
        for name in clean_names:
            votes[name] = "For"

    return votes


def _make_title(resolution: str, mover: str) -> str:
    if not resolution:
        return f"Motion moved by {mover}" if mover else "Untitled motion"
    words = resolution.split()
    title = " ".join(words[:12])
    if len(words) > 12:
        title += "…"
    return title[0].upper() + title[1:] if title else title


def extract_motions(text: str) -> List[Dict[str, Any]]:
    """
    Return candidate motion/report dicts.
    Each has: motion_title, description, mover, seconder, outcome, votes, raw_block
    """
    if not text or len(text) < 50:
        return []

    text = _clean(text)
    pattern = re.compile(r"(?=MOTION\b)", re.IGNORECASE)
    parts = pattern.split(text)

    candidates = []
    for part in parts:
        if not re.search(r"\bMOTION\b", part[:80], re.IGNORECASE):
            continue
        block = part[:2800]
        if (
            "RESOLVED" not in block.upper()
            and "CARRIED" not in block.upper()
            and "LOST" not in block.upper()
            and not re.search(r"Moved:", block, re.IGNORECASE)
        ):
            continue

        mover, seconder = _extract_mover_seconder(block)
        outcome = _extract_outcome(block)
        resolution = _extract_resolution_text(block)
        title = _make_title(resolution, mover)
        votes = _extract_votes(block)

        if len(resolution) < 12 and not mover:
            continue

        candidates.append({
            "motion_title": title,
            "description": resolution,
            "mover": mover,
            "seconder": seconder,
            "outcome": outcome,
            "votes": votes,
            "raw_block": block[:450] + ("…" if len(block) > 450 else ""),
        })

    # Deduplicate
    seen = set()
    unique = []
    for c in candidates:
        key = c["motion_title"][:55].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)

    return unique[:45]


def extract_conflicts(text: str) -> List[Dict[str, str]]:
    """
    Extract conflict-of-interest / disclosure declarations.
    Returns list of dicts: councillor, item_ref, interest_type, reason, action
    """
    if not text or len(text) < 40:
        return []

    text = _clean(text)
    results = []

    # Pattern 1: "Councillor X declared a Non Pecuniary Significant Conflict for the reason that..."
    pattern1 = re.compile(
        r"(?:Councillor|Cr\.?)\s+([A-Za-z\-']+)\s+declared\s+"
        r"((?:a\s+)?(?:Non[- ]?Pecuniary|Pecuniary)[^.]{0,80}?Conflict)"
        r"(?:\s+for\s+the\s+reason\s+that\s+(.+?))?"
        r"(?=\.\s*(?:Councillor|Cr\.?|MOVED|MOTION|RESOLVED|FOR|Nil|$))",
        re.IGNORECASE | re.DOTALL,
    )

    for m in pattern1.finditer(text):
        councillor = _normalise_councillor(m.group(1))
        interest_type = re.sub(r"\s+", " ", m.group(2)).strip()
        reason = (m.group(3) or "").strip()
        reason = re.sub(r"\s+", " ", reason)[:350]
        results.append({
            "councillor": councillor,
            "item_ref": "",
            "interest_type": interest_type,
            "reason": reason,
            "action": "",
        })

    # Pattern 2: item reference first then declaration
    # e.g. "CC20/2026 - Rates Subsidies… – Councillor Bangura declared a Non Pecuniary Interest…"
    pattern2 = re.compile(
        r"((?:[A-Z]{1,4}\d{1,3}/\d{4}|PE\d+|CC\d+|WI\d+|BN\d+|DI\d+)[^–\n]{0,90})"
        r"[–\-—]\s*"
        r"(?:Councillor|Cr\.?)\s+([A-Za-z\-']+)\s+declared\s+"
        r"((?:a\s+)?(?:Non[- ]?Pecuniary|Pecuniary)[^.]{0,90})",
        re.IGNORECASE,
    )

    for m in pattern2.finditer(text):
        item_ref = re.sub(r"\s+", " ", m.group(1)).strip()[:120]
        councillor = _normalise_councillor(m.group(2))
        interest_type = re.sub(r"\s+", " ", m.group(3)).strip()
        # Avoid duplicates
        if any(r["councillor"] == councillor and item_ref[:30] in r.get("item_ref", "") for r in results):
            continue
        results.append({
            "councillor": councillor,
            "item_ref": item_ref,
            "interest_type": interest_type,
            "reason": "",
            "action": "",
        })

    # Capture "would leave the Chamber" / "remain in the Chamber" nearby
    for r in results:
        # Look for action near this councillor's name
        name_only = r["councillor"].replace("Cr ", "")
        action_m = re.search(
            rf"(?:Councillor|Cr\.?)\s+{re.escape(name_only)}[^.]{{0,40}}"
            r"(would leave the Chamber|leave the chamber|remain in the Chamber|remain in the chamber|"
            r"take no part|participate in discussion)",
            text,
            re.IGNORECASE,
        )
        if action_m:
            r["action"] = action_m.group(1).strip()

    # Deduplicate
    seen = set()
    unique = []
    for r in results:
        key = (r["councillor"].lower(), r["item_ref"][:40].lower(), r["interest_type"][:40].lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    return unique[:30]
