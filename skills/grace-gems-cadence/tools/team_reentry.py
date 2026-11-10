"""Read-only team handoff projection. Evidence files are private agent captures."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import team_contributions as team


def read_context(brief_path, receipt_path, state_path, owner, at=None):
    try:
        paths = [Path(p) for p in (brief_path, receipt_path, state_path)]
        if any(not p.is_absolute() for p in paths):
            raise ValueError("Explicit absolute private inputs required")
        brief, receipt, state = [json.loads(p.read_text(encoding="utf-8-sig")) for p in paths]
        return team.reentry(brief, receipt, state, owner, at or datetime.now(timezone.utc).isoformat())
    except (OSError, ValueError, TypeError):
        return {"items": [], "limitation": "Team evidence unavailable; continue personal orientation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--current-state", required=True)
    parser.add_argument("--owner", choices=["mira", "hannah", "jon"], required=True)
    args = parser.parse_args()
    print(json.dumps(read_context(args.brief, args.receipt, args.current_state, args.owner), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
