# Age Gating — compliant patterns

Age verification is the entry ticket for any cannabis/CBD site or app. A weak gate (dismissible banner, no persistence) can be treated as no gate.

## Tiers of assurance (pick per risk)

1. **Self-attestation gate (minimum).** Interstitial before ANY content: "Are you 21 or older?" Yes/No. "No" → redirect off-site (e.g. a truth-about-cannabis or a neutral page), never into the store. Persist the pass (cookie/localStorage + optional session) so it's not bypassable by reload alone, but re-verify on new sessions.
2. **Date-of-birth entry.** User enters DOB; compute age server-side. Harder to click through than yes/no. Store only the boolean result, not the DOB, if you can avoid it.
3. **Third-party age/ID verification** (Veratad, AgeChecker.net, Persona, Yoti). Required for actual sales/checkout in many states; overkill for a menu-only site. Store the verification token, minimize retained ID images.

## Rules

- Gate must appear **before** product content and be non-dismissible without answering.
- Applies to the app splash, the website root, and ideally deep links/shared product URLs.
- Do not youth-appeal the gate itself (no candy/cartoon styling).
- Combine with **geo-restriction**: if the visitor is outside a legal state, don't just gate — restrict the store.
- Log consent (timestamp) if the state requires demonstrable verification.

## Minimal self-attestation gate (React) — least code that works

```tsx
// AgeGate.tsx — wrap the app. Persists a pass for the session + 30 days.
import { useState, useEffect } from "react";

const KEY = "age_ok";
const MIN_AGE = 21; // set 18 for qualifying medical markets

export function AgeGate({ children }: { children: React.ReactNode }) {
  const [ok, setOk] = useState<boolean | null>(null);

  useEffect(() => {
    setOk(localStorage.getItem(KEY) === "1");
  }, []);

  if (ok === null) return null;           // avoid flash before check
  if (ok) return <>{children}</>;

  const pass = () => {
    localStorage.setItem(KEY, "1");
    setOk(true);
  };
  const deny = () => { window.location.href = "https://www.samhsa.gov/"; };

  return (
    <div role="dialog" aria-modal="true" aria-label="Age verification"
         style={{ position: "fixed", inset: 0, display: "grid",
                  placeItems: "center", background: "#0b0b0b", color: "#fff",
                  textAlign: "center", padding: 24, zIndex: 9999 }}>
      <div style={{ maxWidth: 420 }}>
        <h1>Are you {MIN_AGE} or older?</h1>
        <p>You must be {MIN_AGE}+ to enter this site.</p>
        <button onClick={pass}>Yes, I am {MIN_AGE}+</button>
        <button onClick={deny}>No</button>
      </div>
    </div>
  );
}
```

For DOB verification, compute age on the server and return only a boolean cookie — never trust a client-side age check for anything that gates a sale.

## DOB check (server, e.g. Next.js route) — for sales flows

```ts
export function isOfAge(dobISO: string, min = 21): boolean {
  const dob = new Date(dobISO);
  const now = new Date();
  let age = now.getFullYear() - dob.getFullYear();
  const m = now.getMonth() - dob.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < dob.getDate())) age--;
  return age >= min;
}
```

For actual purchases, escalate to a real ID-verification vendor — self-attestation and DOB entry are not sufficient for regulated sales in most states.
