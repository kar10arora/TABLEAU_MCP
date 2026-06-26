Wrong sort element — code was generating <sort class="computed"> which isn't valid in Tableau's DTD. The correct element is <shelf-sorts><shelf-sort-v2 .../></shelf-sorts>.

Missing manifest flags — <IntuitiveSorting/> and <IntuitiveSorting_SP2/> were absent from the template's <document-format-change-manifest>. Without them, Tableau uses an older DTD that doesn't recognize <shelf-sorts> at all.

Wrong shelf reference format — <rows> and <cols> were using raw field names like [ds].[sales]. Tableau requires column-instance names like [ds].[sum:sales:qk] when <shelf-sorts> is involved.

measure-to-sort-by is always required — even for alphabetical sorts, the <shelf-sort-v2> DTD mandates measure-to-sort-by. The initial implementation omitted it for alphabetical sort, causing a validation failure on that sheet.