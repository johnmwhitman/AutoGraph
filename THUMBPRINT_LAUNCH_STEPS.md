# Thumbprint Launch Steps
# Generated: 2026-03-25
# Estimated time: ~30 minutes total

---

## STEP 1 — Stripe Payment Link (10 min)

1. Go to: https://dashboard.stripe.com/payment-links
2. Click "New payment link"
3. Add a product:
   - Name: "Thumbprint — Standard Portrait"
   - Price: $299.00 (one time)
   - Description: "Behavioral portrait based on 8 behavioral probe questions. Delivered in 5 business days."
4. Under "After payment" → set to: show confirmation page
   - Add confirmation message: "Thank you. You'll receive your intake link at your email address within 24 hours."
5. Save → copy the generated Payment Link URL
6. THEN: open C:\AI\autograph\landing_thumbprint.html
   - Find: STRIPE_PAYMENT_LINK_HERE
   - Replace with your actual Stripe link
7. Also update intake_form.html if it has any Gumroad refs (search "gumroad")

Stripe fee on $299: ~$8.87 (2.9% + $0.30)
vs Gumroad fee: ~$30 (10%)
Savings per sale: ~$21

---

## STEP 2 — Cloudflare Email Routing for hello@thumbprinted.com (10 min)

1. Go to: https://dash.cloudflare.com
2. Select the thumbprinted.com domain
3. Left sidebar → "Email" → "Email Routing"
4. Click "Get started" (or "Enable Email Routing" if first time)
5. Cloudflare will add required MX and TXT records automatically — click Confirm
6. Under "Routing rules" → click "Create address"
   - Custom address: hello@thumbprinted.com
   - Destination: johndw@gmail.com (or whatever your personal email is)
   - Save
7. Cloudflare will send a verification email to your destination address — click the link
8. Done. Any email to hello@thumbprinted.com lands in your Gmail.

Test: send a test email to hello@thumbprinted.com from another account.

---

## STEP 3 — Deploy landing_thumbprint.html to Cloudflare Pages (10 min)

1. Go to: https://dash.cloudflare.com → Pages
2. Find the yourbrief-io-v2 project (or create a new thumbprinted project)
3. Option A — Separate project for thumbprinted.com:
   - Create new Pages project → "Upload assets" (direct upload)
   - Upload landing_thumbprint.html, rename to index.html
   - After deploy, go to "Custom domains" → add thumbprinted.com
4. Option B — Same project, different domain:
   - Go to existing Pages project → Custom domains → Add thumbprinted.com
   - But you'd need to serve different content per domain... use Option A

File location: C:\AI\autograph\landing_thumbprint.html

---

## STEP 4 — Update Gumroad listing text (5 min)

The Gumroad listing copy in gumroad_listing_draft.md still says "intake form via Gumroad."
Two options:
a) Keep Gumroad as discovery + payment, use Stripe for future direct traffic
b) Drop Gumroad entirely, drive all traffic to thumbprinted.com

Recommendation: use Stripe directly. You control the customer relationship
and save $21/sale. Gumroad's discovery doesn't help a $299 service the way
it helps $9 digital products.

---

## STEP 5 — First order flow (manual until we automate it)

When a Stripe payment comes in:
1. You get a Stripe email notification
2. Copy the intake form URL: http://localhost:8765 (or deployed CF URL)
3. Send to buyer:
   "Thank you for your Thumbprint order. Here's your intake form: [URL]
    Answer at your own pace — 2-5 sentences per question works well.
    Your portrait arrives within 5 business days of receipt.
    — John"
4. Run coordinator when intake comes in:
   python C:\AI\autograph\autograph_coordinator.py --new "Name" email@domain.com standard
5. Portrait gets auto-synthesized by intake_server.py when form submits

---

## CURRENT STATUS

- landing_thumbprint.html: UPDATED (Gumroad refs removed, Stripe placeholder in place)
- intake_form.html: BUILT, Thumbprint-branded, ready
- intake_server.py: RUNNING on :8765 (start with: python C:\AI\autograph\intake_server.py)
- autograph_coordinator.py: READY
- hello@thumbprinted.com: PENDING email routing setup (Step 2 above)
- Stripe payment link: PENDING (Step 1 above)
- thumbprinted.com landing: PENDING deploy (Step 3 above)
