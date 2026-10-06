# Sources and settled disagreements

Read when a `UX-<n>` rule is challenged. Checked October 2026. Material 3,
Apple HIG and Polaris pages render through JavaScript; their numbers were
confirmed through secondary sources.

## Sources per rule

| Rule | Sources |
|---|---|
| UX-1 | carbondesignsystem.com/elements/spacing/overview; m3.material.io (4/8 dp grid); ui.shadcn.com/docs/theming; atlassian.design/foundations/color-new |
| UX-2 | nngroup.com/articles/ten-usability-heuristics (consistency, Jakob's law); shadcn `cva` variants |
| UX-3 | nngroup.com/articles/visual-hierarchy-ux-definition; primer.style typography (semantic headings) |
| UX-4 | baymard.com/blog/line-length-readability; design-system.service.gov.uk/styles/layout; WCAG 1.4.8 |
| UX-5 | nngroup.com/articles/f-shaped-pattern-reading-web-content; visual hierarchy |
| UX-6, UX-7 | WCAG 2.2 SC 1.4.1, 1.4.3, 1.4.11 |
| UX-8 | nngroup.com/articles/icon-usability; Carbon toolbar |
| UX-9 | WCAG 2.2 SC 2.5.8 (24 px AA), 2.5.5 (44 px AAA); Apple HIG 44 pt; Material 48 dp |
| UX-10 | Carbon data table sizes (xs 24 … md 40 default … xl 64); Primer density |
| UX-11, UX-16 | carbondesignsystem.com/components/button/usage |
| UX-12 | Carbon, Atlassian, GOV.UK button copy |
| UX-13 | nngroup.com/articles/ok-cancel-or-cancel-ok; Carbon, Atlassian, GOV.UK, Primer |
| UX-14 | GOV.UK button guidance; Primer («never disable save») |
| UX-15 | Carbon / Atlassian loading button |
| UX-17 | nngroup.com/articles/web-form-design (78% vs 42% error-free) |
| UX-18 | NN/g (asterisk); GOV.UK («(optional)»); Baymard (mark both, 32%) |
| UX-19 | WCAG 1.3.5; GOV.UK text input; Baymard mobile keyboards (54–60% wrong) |
| UX-20 | NN/g and Baymard inline validation |
| UX-21, UX-22 | GOV.UK error message and error summary |
| UX-23 | WCAG 2.2 SC 3.3.7; Baymard checkout |
| UX-24 | GOV.UK question pages; Primer saving |
| UX-25, UX-26 | nngroup.com/articles/response-times-3-important-limits; /skeleton-screens |
| UX-27 | Carbon, Material, Polaris notifications; Atlassian («never auto-dismiss critical»); Primer banners |
| UX-28 | WCAG 2.2 SC 4.1.3, 2.2.1 |
| UX-29 | no authoritative source — engineering practice |
| UX-30 | nngroup.com/articles/vertical-nav; NN/g hidden navigation (≈20% lower findability) |
| UX-31 | NN/g breadcrumbs; GOV.UK page titles |
| UX-32 | Baymard (59% of sites break Back); cloudscape.design filter persistence |
| UX-33 | NN/g modal dialogs; Carbon (no nested modals); nngroup.com/articles/bottom-sheet |
| UX-34 | w3.org/WAI/ARIA/apg/patterns/dialog-modal |
| UX-36, UX-37 | nngroup.com/articles/confirmation-dialog; Cloudscape delete patterns |
| UX-38 | WCAG 2.2 SC 2.2.1, 2.2.5, 3.3.8; DWP design system timeout |
| UX-39 | nngroup.com/articles/data-tables; baymard.com/blog/list-item-design-ecommerce |
| UX-40, UX-41 | GOV.UK table (numeric); Carbon data table |
| UX-42 | Baymard filtering (28% hide applied filters; mobile apply button) |
| UX-43 | NN/g infinite scroll; GOV.UK pagination; Baymard «Load more» |
| UX-44–UX-46 | Carbon and Primer empty states; Cloudscape (hide unavailable) |
| UX-47 | NN/g dashboards; Carbon data visualisation |
| UX-48 | web.dev/articles/vitals |
| UX-49 | NN/g scrolling and attention (57% above the fold, 74% first two screens) |
| UX-50 | baymard.com/lists/cart-abandonment-rate (extra costs 39–40%) |
| UX-51 | Baymard (account required 18–19% abandonment); WCAG 3.3.8 |
| UX-52 | NN/g onboarding tutorials |
| UX-53 | EU DSA Art. 25; GDPR, CJEU Planet49; EDPB Guidelines 03/2022; US ROSCA, FTC Junk Fees Rule; deceptive.design |
| UX-54 | EDPB; CNIL fine against Google (€150 M, one click vs five) |
| UX-55 | WCAG 1.4.4, 1.3.4; `prefers-reduced-motion` |
| UX-56 | W3C internationalisation; MDN `Intl` |
| UX-57, UX-58 | UI UX Pro Max (icon and elevation consistency, blur purpose); Material 3 elevation; Apple HIG materials |
| UX-59 | UI UX Pro Max (line height, 16 px on mobile, tabular figures); Vercel Web Interface Guidelines (typography); frontend-design (no monospace labels) |
| UX-60 | Anthropic frontend-design (generated-look clusters and typographic tells) |
| UX-61 | frontend-design (motion only with meaning); Vercel (transform/opacity, no `transition: all`, interruptible, autoplay pause); UI UX Pro Max (reduced motion, continuous animation, auto-rotation); WCAG 2.2 SC 2.2.2, 2.3.3 |
| UX-62 | UI UX Pro Max (dark-mode pairing); Vercel (dark mode and theming) |
| UX-63 | Vercel (focus states, hover); UI UX Pro Max (state clarity, read-only vs disabled); WCAG 2.4.7 |
| UX-64 | Vercel (semantics, links, skip link); UI UX Pro Max (keyboard navigation, focus on route change); WCAG 2.1.1, 2.4.1, 2.4.3 |
| UX-65 | WCAG 2.2 SC 2.4.11; Vercel (sticky elements, `scroll-margin-top`) |
| UX-66 | WCAG 1.1.1, 1.2.2; Vercel; UI UX Pro Max (icon context) |
| UX-67 | WCAG 2.2 SC 2.5.7; UI UX Pro Max; Vercel (gesture alternatives) |
| UX-68 | WCAG 2.2 SC 3.2.6 |
| UX-69 | Vercel (clickable labels, single hit target); UI UX Pro Max (field grouping, progressive disclosure); GOV.UK fieldsets |
| UX-70 | UI UX Pro Max (contextual live badge updates); WCAG 4.1.3 |
| UX-71 | UI UX Pro Max (long-token wrapping, essential text truncation, text reflow); Vercel (content handling); WCAG 1.4.4, 1.4.10, 1.4.12 |
| UX-72 | UI UX Pro Max (compact label semantics, chip reflow) |
| UX-73 | UI UX Pro Max (charts and data); Carbon data visualisation accessibility |
| UX-74 | UI UX Pro Max (layout and responsive); Vercel (safe areas and layout, overscroll) |
| UX-75 | Vercel (performance, images); UI UX Pro Max (performance); web.dev |
| UX-76 | Vercel (touch and interaction) |
| UX-77 | Vercel (locale and i18n); MDN `Intl` |
| UX-78 | Vercel (typography, adapted to Russian norms); «Справочник издателя и автора» (Мильчин) — кавычки, тире, неразрывные пробелы |
| UX-79 | frontend-design (writing in design); Vercel (content and copy) |
| UX-80 | EU AI Act, Art. 50 (transparency); UI UX Pro Max (AI disclaimer) |

## Where sources disagree and what this skill chose

| Question | Options | Chosen |
|---|---|---|
| Field marking | asterisk (NN/g) / «(optional)» (GOV.UK) / both (Baymard) | B2B «(необязательно)»; B2C both |
| Validation timing | on blur (NN/g, Baymard) / on submit only (GOV.UK) | on blur and on submit |
| Disabled buttons | almost never (GOV.UK, Primer) / with an explanation | Save/Submit never; others with a reason; permissions → hide |
| Button while loading | disabled (Carbon) / not disabled (Atlassian) | shows progress, ignores repeat presses |
| Toast auto-dismiss | 4–10 s (Material, Polaris) / never (Carbon, WCAG 2.2.1) | success only, 4–10 s; errors never auto-dismiss |
| Errors in a toast | never (Atlassian, Carbon) / short non-critical (Polaris) | never |
| Type-to-confirm word | «confirm» (Cloudscape) / «DELETE» (NN/g) / resource name (GitHub) | the object's name |
| Modals | short tasks (NN/g, Carbon) / avoid (DWP) | rare short tasks only |
| Infinite scroll | feeds (NN/g) / never (GOV.UK) / «Load more» hybrid (Baymard) | feeds only; catalogs «Показать ещё» |
| Spinner vs skeleton | spinner 2–10 s (NN/g) / skeleton in tables (Carbon, Cloudscape) | skeleton for pages and tables, spinner for small modules |
| No permission | hide (Cloudscape) / explain (Carbon) | never available → hide; later → disabled with a reason; data → explanatory state |
| Icon-only | never (NN/g) / toolbar with tooltip (Carbon) | toolbar with tooltip only |
| Target size | 24 px AA / 44 px | 24 px floor; 44 px for B2C and touch |
| Destructive styling | only in the confirmation (NN/g) / red at every step (UI UX Pro Max, Material, Apple HIG) | red at every step: secondary-weight danger control on the page, filled red in the confirmation (UX-37) |
| Motion | smooth transitions everywhere, staggers, springs (UI UX Pro Max) / sparing, meaningful motion (frontend-design) | motion only answers an action or shows a change; no staggers, springs or press-scaling (UX-61) |
| Hover timing | 150–300 ms transitions (UI UX Pro Max) / no animated hover on every card (frontend-design) | instant or within 150 ms on interactive elements; none on non-interactive cards (UX-63) |
| Placeholder | an example value ending with «…» (Vercel) / avoid (GOV.UK) | only in search fields; a format example lives in the hint (UX-17, UX-19) |
| Hint position | under the field (Material) / between label and field (GOV.UK) | between label and field (UX-19) |
| Field error announcement | `aria-live="polite"` (Vercel) / `role="alert"` | polite and tied by `aria-describedby`; `role="alert"` only for a failed operation (UX-28) |
| Focus after a failed submit | first invalid field (Vercel) / error summary (GOV.UK) | the summary; a one-field form keeps focus on the field (UX-22) |
| Autosave of long forms | drafts saved automatically (UI UX Pro Max) / explicit save (GOV.UK, Primer) | a browser draft with «Восстановить черновик»; the server only via Save (UX-24) |
| Pie charts | for proportions up to 5 parts (UI UX Pro Max) / avoid (NN/g, Carbon) | none; parts of a whole as a 100 % stacked bar (UX-47) |
| Mobile first | always (UI UX Pro Max) / by audience | desktop first for every product; the narrow width must work (UX-74) |
| Toast duration | 3–5 s (UI UX Pro Max) / 4–10 s | success only, 4–10 s (UX-27) |
| Line length | 65–75 (UI UX Pro Max) / under 80 (frontend-design) | 50–75 (UX-4) |
| Letter case and quotes | Title Case, “curly” (Vercel, English) | Russian norms: sentence case, «ёлочки» (UX-12, UX-78) |
