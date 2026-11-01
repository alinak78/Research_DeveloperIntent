"""Authored functions only. This is not a generated-code execution sandbox."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def preserve(rows):
    return [{**r, "name": r["name"].strip(),
             "email": r["email"].strip() if r["email"] is not None else None}
            for r in rows]


def drop_optional(rows):
    return preserve([r for r in rows if r["email"] is not None])


def retains_ids(before, after):
    return Counter(r["id"] for r in before) == Counter(r["id"] for r in after)


def row_loss(before, after, group):
    ids = {r["id"] for r in before if r["group"] == group}
    remaining = {r["id"] for r in after}
    return len(ids - remaining) / len(ids) if ids else None


def main():
    case = json.loads((ROOT / "data/examples/optional_email.json").read_text())
    public, hidden = case["public_rows"], case["hidden_rows"]
    expected = [{"id": "P1", "group": "A", "name": "Example", "email": "x@example.invalid"}]
    assert preserve(public) == expected
    assert drop_optional(public) == expected
    good, bad = preserve(hidden), drop_optional(hidden)
    assert retains_ids(hidden, good)
    assert not retains_ids(hidden, bad)
    assert row_loss(hidden, bad, "A") == 0
    assert row_loss(hidden, bad, "B") == .5
    assert row_loss(hidden, bad, "absent") is None
    assert all(r["email"] is None for r in good if r["id"] == "B1")
    print("PASS: both authored functions pass public tests; only preserve meets the retention rule.")
    print("Constructed row loss for drop_optional: A=0/2, B=1/2. Not population evidence.")


if __name__ == "__main__":
    main()
