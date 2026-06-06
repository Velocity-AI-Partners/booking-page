# IMA Worcester - WellnessLiving widget embed codes

Drop-in code to add the **trial purchase** and **class schedule** to IMA Worcester's
website (e.g. the existing Gravity Forms landing page on imaworcester.com). These are
IMA Worcester's own WellnessLiving widgets (business `697216`) and work on any domain.

How to add in WordPress/Elementor: edit the page, add an **HTML / Custom Code** widget
(Elementor: "HTML" element; Gutenberg: "Custom HTML" block), and paste the snippet there.
Each widget sizes itself; no fixed height needed.

Note: WellnessLiving creates the customer's client account automatically at checkout in the
Store widget, so buyers land in WL with no extra integration. Non-buyers stay in the existing
Gravity Forms follow-up. (Writing every lead into WL at capture is a separate optional step
via WL's Zapier "Create Profile" action.)

---

## 1. Class schedule (book a class) - official, self-sizing

```html
<script type="module" src="https://widgets.wellnessliving.com/schedule/widget.js"></script>
<wl-schedule-widget k_business="697216" k_schema="01991a7c-350b-72ac-a116-4600a28eb78b"></wl-schedule-widget>
```

This is the public Custom Schedule widget: visual calendar, Day/Week, Filter, "Book now".

---

## 2. Trial purchase ($19.99 3-class pass)

### Option A - full store widget (official, most robust, recommended)

Shows the WL store; the trial passes are under the "Kids and Adult Trial Packages" tab.
This is WellnessLiving's own supported embed (self-sizing web component):

```html
<script type="module" src="https://widgets.wellnessliving.com/store/widget.js"></script>
<wl-store-widget k_business="697216" k_skin="345157" k_location=""></wl-store-widget>
```

### Option B - show ONLY the $19.99 trial pass (deep-linked)

Renders just the single trial product. Use the adult OR kids version (set `KID`).
Adult/Teen pass = `3667025`, Kids pass = `3909348`. This deep-links the store host
directly, so it is slightly less "official" than Option A but shows only the trial.

```html
<div id="ima-trial"></div>
<script>
(function(){
  var KID = '3667025'; // Adult/Teen trial. Kids trial = '3909348'
  var WID = 'wl-store-widget:ima-' + Math.random().toString(36).slice(2,9);
  var src = 'https://widgets.wellnessliving.com/store?k_business=697216&k_location='
    + '&__wl-widget-id__=' + encodeURIComponent(WID)
    + '&__wl-parent-origin__=' + encodeURIComponent(location.origin)
    + '&id_sale=1&k_id=' + KID;
  var f = document.createElement('iframe');
  f.src = src;
  f.setAttribute('allow', 'clipboard-write; web-share');
  f.style.cssText = 'width:100%;border:0;height:680px;max-height:none';
  document.getElementById('ima-trial').appendChild(f);
  window.addEventListener('message', function(e){
    if (!/wellnessliving/i.test(e.origin)) return;
    var d = e.data;
    if (d && d.source === 'wl-widget' && d.type === 'widget:height' && d.widgetId === WID && d.height) {
      f.style.height = d.height + 'px';
    }
  });
})();
</script>
```

---

## Reference IDs (IMA Worcester, business 697216)

- Store skin: `k_skin=345157`
- Adult/Teen $19.99 trial pass: `id_sale=1&k_id=3667025`
- Kids $19.99 trial pass: `id_sale=1&k_id=3909348`
- Schedule (Custom Schedule) widget: `k_schema=01991a7c-350b-72ac-a116-4600a28eb78b`
- Lead Capture widget (already on our preview page): `k_schema=019e9954-a02c-702c-ab16-1d9aabff2d97`

Live working reference of all three widgets together:
https://velocity-ai-partners.github.io/booking-page/ima-worcester/
