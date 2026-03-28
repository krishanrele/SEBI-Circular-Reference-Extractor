import sys
from pathlib import Path
from agent.extractor import extract_references, save_results
from rich.console import Console
from rich.table import Table

console = Console()

def filter_references(references: list) -> list:
    """Remove any references that are websites rather than documents."""
    return [
        ref for ref in references
        if not ref["document_title"].startswith(("www.", "http://", "https://"))
    ]

def group_references(references: list) -> list:
    """
    Group references by document title so each document appears only once,
    with all its page numbers and contexts combined.
    """
    grouped = {}
    for ref in references:
        title = ref["document_title"]
        if title not in grouped:
            grouped[title] = {
                "document_title": title,
                "document_type": ref["document_type"],
                "pages": [],
                "contexts": []
            }
        for page in ref["pages"]:
            if page not in grouped[title]["pages"]:
                grouped[title]["pages"].append(page)
        context = ref.get("context", "").strip()
        if context and context not in grouped[title]["contexts"]:
            grouped[title]["contexts"].append(context)

    return list(grouped.values())

def display_results(result: dict):
    filtered = filter_references(result["references"])
    grouped = group_references(filtered)

    console.print(f"\n[bold green]Circular:[/bold green] {result['circular_title']}")
    console.print(f"[bold]Total references found:[/bold] {len(grouped)}\n")

    table = Table(title="Referenced Documents", show_lines=True)
    table.add_column("Document Title", style="cyan", no_wrap=False, max_width=35)
    table.add_column("Type", style="magenta", max_width=12)
    table.add_column("Pages", style="green", max_width=10)
    table.add_column("Context", style="yellow", no_wrap=False, max_width=55)

    for ref in grouped:
        pages_str = ", ".join(str(p) for p in sorted(ref["pages"]))
        contexts_str = "\n\n".join(
            f"p.{i+1}: {ctx}"
            for i, ctx in enumerate(ref["contexts"])
        )
        if not contexts_str:
            contexts_str = "—"
        table.add_row(ref["document_title"], ref["document_type"], pages_str, contexts_str)

    console.print(table)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py path/to/circular.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = f"outputs/{Path(pdf_path).stem}_references.json"
    Path("outputs").mkdir(exist_ok=True)

    result = extract_references(pdf_path)
    save_results(result, output_path)
    display_results(result)