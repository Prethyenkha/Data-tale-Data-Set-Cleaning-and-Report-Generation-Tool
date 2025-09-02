import os
import argparse
import json
import pandas as pd
from datetime import datetime
from autoclean.cleaner import clean_dataframe, build_audit_summary
from openai import OpenAI

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def ai_explain(audit: dict) -> str | None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    client = OpenAI()
    system = "You are a data-cleaning analyst. Explain an audit succinctly for a business audience."
    user_prompt = (
        "Turn this JSON audit into a friendly, structured summary with bullets and actionable takeaways.\n\n"
        + json.dumps(audit, indent=2)
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":system}, {"role":"user","content":user_prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content

def write_markdown_report(outdir: str, audit: dict, ai_summary: str | None = None):
    lines = []
    lines.append(f"# Data Tale Report")
    lines.append("")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append("")
    if ai_summary:
        lines.append("## Executive Summary (AI)")
        lines.append(ai_summary.strip())
        lines.append("")
    lines.append("## Dataset Overview")
    lines.append(f"- Rows before: **{audit['rows_before']}**")
    lines.append(f"- Rows after: **{audit['rows_after']}**")
    lines.append(f"- Columns: **{len(audit['columns'])}**")
    lines.append("")
    if audit.get("duplicates_removed", 0) > 0:
        lines.append(f"### Duplicates Removed: {audit['duplicates_removed']}")
        lines.append("")
    lines.append("## Column-by-Column Changes")
    for col, info in audit["column_changes"].items():
        lines.append(f"### `{col}`")
        for k,v in info.items():
            if v not in (None, 0, "", [], {}, False):
                lines.append(f"- **{k.replace('_',' ').title()}**: {v}")
        lines.append("")
    if audit["issues"]:
        lines.append("## Issues & Flags")
        for issue in audit["issues"]:
            lines.append(f"- {issue}")
        lines.append("")
    report_path = os.path.join(outdir, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return report_path

def main():
    parser = argparse.ArgumentParser(description="Data Tale (CLI)")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--outdir", default="outputs", help="Directory for cleaned.csv and report.md")
    parser.add_argument("--no-ai", action="store_true", help="Skip OpenAI summary")
    args = parser.parse_args()

    ensure_dir(args.outdir)
    df = pd.read_csv(args.input)
    cleaned, audit = clean_dataframe(df)
    cleaned.to_csv(os.path.join(args.outdir, "cleaned.csv"), index=False)

    audit_summary = build_audit_summary(audit)
    ai_summary = None if args.no_ai else ai_explain(audit_summary)
    report_path = write_markdown_report(args.outdir, audit_summary, ai_summary)

    print(f"Saved cleaned dataset to {os.path.join(args.outdir, 'cleaned.csv')}")
    print(f"Saved report to {report_path}")

if __name__ == "__main__":
    main()
