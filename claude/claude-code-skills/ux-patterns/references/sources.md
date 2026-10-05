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
