import os, argparse
from app.llm.planner import plan_from_instruction
from app.browser.controller import BrowserController
from app.services.aggregator import search_products
from app.services.utils import save_json, save_csv, ensure_dir

def main():
    parser = argparse.ArgumentParser(description="AI Web Navigator – LLM ➜ Search ➜ Save")
    parser.add_argument("instruction", type=str, nargs="+", help="Natural language instruction")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless (default true)")
    parser.add_argument("--show", action="store_true", help="Force visible browser (overrides --headless)")
    parser.add_argument("--outdir", type=str, default="data", help="Output dir for json/csv")
    args = parser.parse_args()

    instruction = " ".join(args.instruction).strip()
    if args.show:
        os.environ["HEADLESS"] = "false"
    else:
        os.environ["HEADLESS"] = "true" if args.headless else "false"

    print(f"[LLM] Planning for: {instruction}")
    plan = plan_from_instruction(instruction)
    print("[LLM] Plan ->", plan)

    ensure_dir(args.outdir)
    with BrowserController(run_dir="runs") as bc:
        items = search_products(
            bc=bc,
            sources=plan["sources"],
            query=plan["query"],
            max_results=plan["max_results"],
            max_price=plan["max_price"],
        )

    # Save outputs
    base = f"{'+'.join(plan['sources'])}_{plan['query'].replace(' ','_')}"
    json_path = save_json(items, args.outdir, base)
    csv_path  = save_csv(items, args.outdir, base)
    print(f"[SAVE] JSON -> {json_path}")
    print(f"[SAVE] CSV  -> {csv_path}")

    # Pretty print a few
    for r in items[: min(5, len(items))]:
        print(r)

if __name__ == "__main__":
    main()
