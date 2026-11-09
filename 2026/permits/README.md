# Long-term employment permit charts

Five self-contained charts from the FoI response (1 January to 22 October 2026). Each file has no dependencies apart from Google Fonts and a transparent background, so it takes the colour of the page it sits on.

1-outcomes-waffle.html: all 1,000 applications, one square each
2-sectors.html: outcomes by sector
3-out-of-policy.html: in-policy vs out-of-policy, as shares
4-top-roles.html: roles with 19 or more applications
5-rejections.html: all nine refusals

## Embedding

Each chart posts its height to the parent page, so the iframe can size itself on any screen width. Add this once per article (a Ghost HTML card is fine), then one iframe per chart:

```html
<script>
window.addEventListener('message', function (e) {
  if (!e.data || e.data.type !== 'quarry-chart-height') return;
  var f = document.querySelector('iframe[data-chart="' + e.data.id + '"]');
  if (f) f.style.height = e.data.height + 'px';
});
</script>

<iframe data-chart="1-outcomes-waffle" src="https://graphics.thequarry.media/2026/permits/1-outcomes-waffle.html"
  style="width:100%;border:0;height:720px" loading="lazy" title="Permit application outcomes"></iframe>
```

The `data-chart` value must match the file name without `.html`. The inline height is only a fallback before the script runs.

## Editing

The figures live in `build.py`. Change them there and run `python3 build.py` to regenerate all five files; the script checks that the sector rows still add up to the FoI totals.
