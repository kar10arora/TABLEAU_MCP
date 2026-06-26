#!/usr/bin/env python3
"""
Inspect generated TWB files to verify sort and filter XML structure.
"""

from lxml import etree

FILES = {
    "Story 2.2 – Sorting": "examples/generated_workbooks/story_2_2_sorting.twb",
    "Story 2.3 – Filtering": "examples/generated_workbooks/story_2_3_filtering.twb",
}


def inspect(label, path):
    print("=" * 60)
    print(f"{label}")
    print(f"File: {path}")
    print("=" * 60)

    tree = etree.parse(path)

    for ws in tree.findall(".//worksheet"):
        name = ws.get("name")
        print(f"\n  Sheet: '{name}'")

        # column-instances
        cis = ws.findall(".//column-instance")
        if cis:
            print(f"    column-instances ({len(cis)}):")
            for ci in cis:
                print(f"      name={ci.get('name')}  derivation={ci.get('derivation')}")

        # sort elements
        sorts = ws.findall(".//shelf-sort-v2")
        if sorts:
            print(f"    shelf-sort-v2 elements ({len(sorts)}):")
            for s in sorts:
                attrs = dict(s.attrib)
                print(f"      {attrs}")
        else:
            print("    shelf-sorts: (none)")

        # filter elements
        filters = ws.findall(".//filter")
        if filters:
            print(f"    filters ({len(filters)}):")
            for f in filters:
                col = f.get("column")
                cls = f.get("class")
                members = [gf.get("member") for gf in f.findall(".//groupfilter") if gf.get("member")]
                fns     = [gf.get("function") for gf in f.findall(".//groupfilter")]
                print(f"      column={col}  class={cls}  functions={fns}  members={members}")
        else:
            print("    filters: (none)")

    print()


for label, path in FILES.items():
    inspect(label, path)
