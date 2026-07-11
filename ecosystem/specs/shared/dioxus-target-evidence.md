# Dioxus target evidence matrix

Status date: 2026-07-11

Dioxus 0.7.9 is the preferred Libre AI application stack. This document controls support claims; framework capability or a successful compile is not sufficient evidence.

Product domains remain renderer-independent Rust crates. Portal owns Dioxus components, adaptive behavior and native-integration contracts. Wrench owns independent evidence. Gear Supply owns packaging and release artifacts.

## Claim states

- `experimental`: local build or spike only; no support claim.
- `evidence-backed`: the target matrix passes in protected CI and documented local reproduction.
- `usable`: at least one real product workflow also passes installation/deployment and rollback smoke.

## Matrix

| Target | Required evidence before `evidence-backed` |
| --- | --- |
| Web/PWA | SSR/SSG/hydration consistency; CSP, CSRF and cookie policy; keyboard and screen-reader checks; Chromium/Firefox/WebKit smoke; offline/cache behavior; WASM budget; no remote fonts or mandatory SaaS |
| Desktop — macOS | system WebView behavior; filesystem sandbox; deep links; signing/notarization plan; install/update/rollback; VoiceOver; sleep/resume; package size |
| Desktop — Windows | WebView2 availability/bootstrap; filesystem and protocol-handler boundaries; signing; install/update/rollback; Narrator; sleep/resume; package size |
| Desktop — Linux | WebKitGTK floor and packaging matrix; filesystem sandbox; deep links; install/update/rollback; AT-SPI; package size |
| Android | emulator and physical-device run; lifecycle/sleep/back navigation; permissions and deep links; offline; TalkBack; signed APK/AAB; install/upgrade/rollback |
| iOS | simulator and physical-device run; lifecycle; ATS and Keychain boundaries; deep links; offline; VoiceOver; archive/signing; install/upgrade/rollback and store constraints |
| Fullstack | auth before WebSocket upgrade; Biscuit tenant/workspace isolation; typed failures; CSRF; retention/deletion; tracing without PII; provider-free test path |
| UI system | Portal tokens only; contrast; focus; touch targets; reduced motion; responsive/adaptive navigation; visual regression and high-contrast checks |

Dioxus desktop/mobile render through native WebViews. JNI or native API access does not turn HTML controls into native widgets and does not prove platform accessibility automatically.

## Current evidence

| Target | State | Evidence / gap |
| --- | --- | --- |
| Web/PWA | `evidence-backed` for the bounded lab and Website publication path | four-engine lab evidence, accessibility/token checks, SSG, plus Wrench Pages HTML/JavaScript/WASM base-path smoke |
| Fullstack | `experimental` to partial evidence | server functions and auth paths exist, but one cross-product operational matrix is not complete |
| Desktop macOS/Windows/Linux | `experimental` | protected compile and test-build checks pass on all three OSes; no WebView runtime, package, install/update/rollback or platform-accessibility evidence |
| Android | `experimental` | no physical-device, signed-package and TalkBack evidence |
| iOS | `experimental` | no physical-device, archive/signing and VoiceOver evidence |
| UI system | `evidence-backed` on bounded web primitives | Portal now owns token-only Dioxus surfaces and adaptive navigation contracts shared through UniFFI; visual regression and real platform accessibility remain incomplete |

No README or product page may turn `experimental` into “supported”, “native”, or “available”.

## Promotion flow

```text
product need
→ Portal pattern or native-integration contract
→ Wrench lab fixture
→ protected target matrix
→ Gear Supply package + provenance
→ install/deploy/rollback smoke
→ profile and README claim update
```

Failures remain evidence. A target is not promoted by waiver unless the waiver is time-bound, owned and visible next to the claim.
