# THUMBPRINT — FIRST ORDER PLAYBOOK
# What to do when a payment comes in
# Generated: 2026-03-25

---

## CURRENT STATE (launch day)

AUTOMATED:
- thumbprinted.com landing page ✓ (live, serving correctly)
- Intake form wizard at localhost:8765 ✓ (run intake_server.py)
- Portrait synthesis (auto-triggers when form submitted) ✓
- Analytics logging ✓
- Client lifecycle tracking (autograph_coordinator.py) ✓

MANUAL FOR FIRST FEW ORDERS (until tunnel + webhook live):
- Sending intake email after payment
- Monitoring Stripe for payments

---

## WHEN A PAYMENT COMES IN

### Step 1 — You'll get a Stripe email notification
Subject: "You have a new payment"
Or check: https://dashboard.stripe.com/payments

### Step 2 — Get their name and email from Stripe dashboard
Click the payment → see Customer Details

### Step 3 — Start intake server if not running
  cmd: C:\Python314\python.exe C:\AI\autograph\intake_server.py
  URL: http://localhost:8765 (local only until tunnel live)

  NOTE: Until Cloudflare Tunnel is configured, send them the hosted version:
  https://thumbprinted.com/intake  ← this serves the static form
  BUT: form POSTs to localhost:8765 which they can't reach externally.

  SHORT-TERM WORKAROUND (until tunnel):
  Option A — Email them a Google Form (the v2 questions, manually)
  Option B — Set up CF Tunnel now (30 min, free):
    1. winget install Cloudflare.cloudflared
    2. cloudflared tunnel login
    3. cloudflared tunnel create thumbprint
    4. Update thumbprint_tunnel.yml with the UUID
    5. Run: start_thumbprint_services.bat

### Step 4 — Send intake email
  Template: C:\AI\autograph\email_templates\purchase_receipt.txt
  Replace {name} with their first name
  Send from johndw@gmail.com (or hello@thumbprinted.com once routing live)

### Step 5 — Create client record
  C:\Python314\python.exe C:\AI\autograph\autograph_coordinator.py --new "Full Name" email@domain.com standard

### Step 6 — When they submit the intake form
  Server auto-saves JSON to: C:\AI\autograph\intakes\
  Auto-triggers synthesis: C:\AI\autograph\intake_processor.py
  Portrait written to: C:\AI\autograph\portraits\name_date.md

### Step 7 — Review and deliver portrait
  1. Read portrait: C:\AI\autograph\portraits\name_date.md
  2. Quick review (10-15 min) — check it's grounded, blind spot is accurate
  3. Render to PDF: C:\Python314\python.exe C:\AI\autograph\delivery_prep.py --latest
  4. Email portrait PDF using template: email_templates\portrait_delivery.txt
     Replace {name}, attach PDF

### Step 8 — Update client status
  C:\Python314\python.exe C:\AI\autograph\autograph_coordinator.py --status name_slug

---

## THE TUNNEL PROBLEM — PRIORITY AFTER FIRST SALE

The intake form at thumbprinted.com is static HTML that POSTs to localhost:8765.
That means the form only works if the buyer is you, on your machine.

Fix: Cloudflare Tunnel routes intake.thumbprinted.com → localhost:8765
Time: ~30 min
Cost: Free
Command sequence:
  winget install Cloudflare.cloudflared
  cloudflared tunnel login
  cloudflared tunnel create thumbprint
  (update thumbprint_tunnel.yml with UUID)
  cloudflared tunnel route dns thumbprint intake.thumbprinted.com
  cloudflared tunnel route dns thumbprint webhook.thumbprinted.com
  Run: C:\AI\automation\start_thumbprint_services.bat

After this: intake.thumbprinted.com is live, webhook.thumbprinted.com accepts Stripe events,
and the entire flow is automated end-to-end.

---

## REVENUE TARGETS

First sale ($299) → LLC filing fee ($50 MO or $45 AR) + leftover
Second sale ($299) → Business checking account, Stripe → business account
Third sale ($299) → Cloudflare Tunnel + GitHub Sponsors + buffer

The goal: system pays for itself by sale 2.

---

## JOHN'S GATES REMAINING

1. Add STRIPE_SECRET_KEY to C:\AI\.env
   Then run: C:\Python314\python.exe C:\AI\automation\stripe_setup_thumbprint.py
   (Creates products, prices, payment links, patches landing page automatically)

2. Redeploy after Stripe link patches:
   C:\AI\automation\wrangler_thumbprint_deploy.bat

3. Enable Cloudflare Email Routing in dashboard:
   dash.cloudflare.com → thumbprinted.com → Email → Enable
   (Takes 30 seconds. Then Kael can add hello@ rule via API.)

4. Cloudflare Tunnel setup (post-first-sale is fine)

5. LLC after first revenue — MO: $50 online at sos.mo.gov

---

## EVERYTHING ELSE IS LIVE

thumbprinted.com         ✓ serving
Landing page             ✓ Thumbprint branded, Stripe placeholder in place
Intake form              ✓ built, functional locally
Portrait synthesis       ✓ wired to Claude API
Client coordinator       ✓ lifecycle tracking
Round 2 generator        ✓ portrait-specific questions
Portrait Navigator       ✓ 90-day chat
Email templates          ✓ all 3 written
Analytics logging        ✓ JSONL events
Delivery PDF renderer    ✓ reportlab (install if needed: pip install reportlab)
