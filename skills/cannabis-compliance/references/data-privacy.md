# Cannabis Data Privacy & Payments

Cannabis purchase history is sensitive personal data — it reveals a federally-illegal activity. Treat it like health data even when the law doesn't force you to.

## Data minimization (default posture)

- Collect the **least** PII needed. A browsing/menu site needs almost none; a loyalty/checkout flow needs more — scope accordingly.
- Store the **result** of age/ID verification (boolean + timestamp + vendor token), not raw DOB or ID images, unless the state requires retention. If you must keep ID scans, encrypt at rest, restrict access, set a deletion schedule.
- Never build unnecessary profiles. Don't log full purchase history to analytics tools that resell data.

## Consent & privacy law

- **CCPA/CPRA (CA) and state privacy laws** apply. Provide a privacy policy, opt-out of sale/share, and honor deletion requests.
- **Do not sell or share** cannabis purchase data. Disclose any sharing explicitly.
- Cookie/tracking consent before loading non-essential trackers.
- Marketing opt-in must be explicit; SMS must be **TCPA-compliant** (clear opt-in, easy STOP).

## Analytics & pixels — careful

- Meta Pixel / Google tags on a cannabis store can (a) leak sensitive data to platforms that ban cannabis and (b) get the ad account flagged. Prefer privacy-respecting/first-party analytics (Plausible, self-hosted, server-side tagging you control).
- Never send product/SKU-level cannabis purchase events to third-party ad platforms.

## Payments (the hard part)

- **Visa/Mastercard/Amex generally prohibit cannabis transactions.** Do not integrate Stripe/standard card processing for THC sales — accounts get shut down and funds frozen.
- Real options: **cash on pickup/delivery, PIN-debit ("cashless ATM" — increasingly scrutinized), ACH/bank transfer, cannabis-specific payment providers** (e.g. Aeropay, Dutchie Pay/ACH), and cannabis-friendly banking (state-chartered banks, CDFIs).
- Ancillary/B2B and non-ingestible accessories may use normal processors — confirm the exact product.
- **Never hardcode a standard card processor** into a cannabis checkout without confirming the client's approved payment rails.

## Security baseline

- HTTPS everywhere, secure cookies, CSRF protection on state-changing routes.
- Encrypt sensitive fields at rest; least-privilege DB access.
- Rate-limit + bot-protect age gates and checkout.
- Have an incident/breach plan — a breach of cannabis buyer data is high-harm.
