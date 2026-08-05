# Build Scope — Grace Gems Website

**Relay ID:** GG-AD-P2-001
**Date:** 2026-08-05
**Status:** Draft — internal planning only. No spend, hiring, or deployment authorized.

---

## 1. Platform

### Recommendation: Shopify

| Option | Pros | Cons | Monthly Cost |
|--------|------|------|-------------|
| **Shopify** | Built for jewelry e-commerce, handles payments/shipping/tax, Etsy integration apps exist, strong mobile experience, scales with the business | Monthly fee, transaction fees unless using Shopify Payments, some template constraints | $39–$105/mo (Basic–Shopify plan) |
| Squarespace | Beautiful templates, simpler to manage, good for story-driven brands | Weaker e-commerce features, no native Etsy sync, limited payment options, product variant limits | $33–$65/mo |
| Custom build (Next.js / headless) | Total design control, no platform constraints | Requires developer for every change, expensive to build and maintain, overkill for current scale | Hosting ~$20/mo + dev costs |
| Etsy Pattern (Etsy's own site builder) | Direct Etsy inventory sync, no migration | Very limited design control, still looks like Etsy, doesn't solve the brand problem | $15/mo |

**Why Shopify:** Grace Gems has 1,597 products, needs payment processing, needs shipping/tax handling, and needs to run alongside Etsy. Shopify handles all of this out of the box. The Shopify theme ecosystem allows a custom-feeling design without a custom build. Etsy integration apps (like CedCommerce or LitCommerce) can sync inventory between both channels.

**Theme approach:** Start with a premium Shopify theme ($350 one-time) that supports the brand's visual direction — warm tones, serif headlines, story-driven layouts. Customize from there. Dawn (free) or Prestige ($350) are strong starting points for jewelry brands.

### Open decision for the team

Does the team have technical ability to manage a Shopify store, or would they need ongoing help? This affects whether to go with a managed theme or invest more upfront in a turnkey setup.

---

## 2. Domain

### Action needed: check availability

Priority order:
1. **gracegems.com** — ideal, clean, canonical
2. **gracegems.co** — strong alternative if .com is taken
3. **shopgracegems.com** — functional, already partially associated with the brand via Etsy search
4. **gracegems.studio** — creative but may confuse customers expecting .com

**Cost:** $12–$50/year depending on the domain. Premium domains (if someone is squatting gracegems.com) could cost $500–$5,000+.

**Action:** Someone needs to check domain availability before any build work begins. This is a blocking prerequisite.

---

## 3. Photography

This is the single most important investment. The mockups show photo placeholders — without real on-person photography, the brand direction doesn't work.

### What's needed

| Type | Purpose | Volume | Priority |
|------|---------|--------|----------|
| **On-person product shots** | Primary product imagery — jewelry being worn (hands, necks, ears) in warm natural light | 20–30 key pieces to start | Critical — launch blocker |
| **Stone portrait macros** | Close-up gemstone photography showing color, light, inclusions | 10–15 hero stones | High — supports collections pages |
| **Workshop / process shots** | Hands working, tools, stones being set — no faces | 8–12 images | Medium — supports About page |
| **Lifestyle context shots** | Pieces in real settings (a hand on a table, earring catching light) | 5–8 images | Medium — supports Stories and homepage |

### Options

**Option A: Professional jewelry photographer**
- Cost: $1,500–$4,000 for a half-day to full-day shoot
- Pros: highest quality, consistent style, one session covers most needs
- Cons: upfront cost, need to ship pieces or coordinate locally in Denver

**Option B: Skilled product photography with a phone/DSLR**
- Cost: $200–$500 (lightbox, backdrop, basic setup)
- Pros: ongoing capability, can photograph new pieces as they're made
- Cons: learning curve, may not achieve the on-person warmth the brand needs
- Note: stone macros and product-on-white can work here; on-person shots are harder

**Option C: Hybrid — professional shoot for hero images, in-house for product catalog**
- Cost: $1,000–$2,500 professional + $200–$500 setup
- Pros: best of both — polished hero imagery for homepage/stories, functional catalog photos for product pages
- Cons: two visual styles need to feel cohesive

**Recommendation:** Option C. Get 20–30 hero shots professionally done for the homepage, stories, and collection features. Build an in-house capability for ongoing product catalog photography. The hero shots set the brand standard; the catalog shots keep the store updated.

### Existing Etsy photos

The current Etsy product photos can serve as temporary catalog imagery during the transition — they're functional for showing the product, even if they don't match the new brand's visual standard. Replace them over time as new photography is produced.

---

## 4. Content Production

### Launch minimum

| Content | Quantity | Who produces | Status |
|---------|----------|-------------|--------|
| Customer stories for Stories page | 3–5 | Reach out to past customers (from Etsy reviews) for permission and quotes | Not started |
| Homepage hero story | 1 | Selected from the customer stories above | Not started |
| Collection introductions (stone family descriptions) | 5–6 (emerald, ruby, opal, tourmaline, sapphire, jade) | Can be written based on existing sourcing knowledge | Not started |
| About page copy ("The Workshop") | 1 page | Based on brand system doc — needs team input on sourcing details | Not started |
| Made for You page copy | 1 page | Drafted in mockups — needs review and refinement | Drafted |
| Product descriptions (new voice) | 20–30 priority pieces rewritten | Existing Etsy titles rewritten in brand voice; rest migrated as-is and updated over time | Not started |
| FAQ content | 1 page | Based on existing Etsy shop policies, rewritten in brand voice | Not started |
| Gemstone guide (evergreen) | 3–5 stone entries to start | Educational content, build over time | Not started — post-launch is fine |

### Customer story outreach

The most time-sensitive content task. Past customers need to be contacted, asked to participate, and their stories need to be written and approved. This takes 2–4 weeks depending on response rates.

**Approach:** Identify 8–10 customers from Etsy reviews who left detailed, emotional reviews. Reach out personally (via Etsy message) asking if they'd share their story for the new website. Aim for 5 confirmed, knowing some won't respond.

**Permission requirements:** Written consent to use their first name, general location, their quote (edited for clarity if needed), and a photo of their piece. This is a rights and attribution item — must be documented.

---

## 5. Etsy Integration Strategy

### Dual-channel approach (confirmed by AD)

Etsy stays as a discovery and sales channel. The independent site becomes the primary brand experience.

### Integration tasks

| Task | Complexity | Notes |
|------|-----------|-------|
| **Inventory sync** | Medium | Use a Shopify-Etsy sync app (CedCommerce, LitCommerce, ~$20–$30/mo). Products listed on both platforms, inventory decrements in sync. |
| **Etsy shop visual update** | Low | Update Etsy banner, profile photo, and shop announcement to reflect new brand identity. Add "Visit gracegems.com for the full experience" to shop announcement. |
| **Review migration** | Low | Manually import top 20–30 Etsy reviews as testimonials on the new site. No automated migration available. |
| **SEO transition** | Medium | Etsy listings currently hold all search equity. The new site needs its own SEO strategy — product pages, collection pages, and story content should be optimized. Don't deindex Etsy; let both rank. |
| **Order management** | Low–Medium | Decide whether both channels feed into the same fulfillment workflow, or if Etsy orders continue through Etsy's system separately. |

---

## 6. Email and Newsletter

### Tool recommendation: Klaviyo or Mailchimp

| Tool | Pros | Cons | Cost |
|------|------|------|------|
| **Klaviyo** | Built for e-commerce, native Shopify integration, powerful segmentation, abandoned cart flows | More complex, higher price at scale | Free up to 250 contacts; $20/mo for 500 |
| **Mailchimp** | Simpler, familiar, adequate for a newsletter | Weaker e-commerce integration, less powerful automation | Free up to 500 contacts; $13/mo for 500 |

**Recommendation:** Start with Klaviyo if on Shopify — the e-commerce integration is significantly better. If budget is tight, Mailchimp works for a basic newsletter and can be upgraded later.

### Launch email plan

1. Set up email capture on the new site (footer signup + popup after 30 seconds)
2. Import existing customer emails from Etsy (with permission / compliance with email marketing laws)
3. Send launch announcement to existing customers
4. Begin monthly newsletter cadence

---

## 7. Timeline

### Realistic phased timeline

| Phase | Duration | What happens |
|-------|----------|-------------|
| **Phase A: Foundations** | Weeks 1–2 | Domain acquisition, Shopify account setup, theme selection, photography planning |
| **Phase B: Content + Photography** | Weeks 2–5 | Customer story outreach, professional photo shoot, collection copy written, product descriptions started |
| **Phase C: Build** | Weeks 4–7 | Shopify theme customization, page builds (homepage, collections, Made for You, About), product migration, Etsy sync setup |
| **Phase D: Polish + Test** | Weeks 7–8 | Design refinement, mobile testing, payment/shipping configuration, soft launch to select customers for feedback |
| **Phase E: Launch** | Week 9 | Public launch, Etsy announcement, first newsletter, social media transition |
| **Phase F: Ongoing** | Week 10+ | Monthly stories, weekly social, ongoing product photography, SEO monitoring, gemstone guide build-out |

**Total to launch: ~9 weeks** from decision to go. The longest lead items are photography (scheduling + delivery) and customer story outreach (response time).

Phases overlap — content production (B) runs in parallel with early build work (C).

---

## 8. Cost Summary

### One-time costs

| Item | Low estimate | High estimate | Notes |
|------|-------------|---------------|-------|
| Domain | $12 | $5,000 | Depends on availability; premium domains cost more |
| Shopify theme | $0 (Dawn free) | $350 (Prestige) | One-time purchase |
| Professional photography | $1,000 | $4,000 | Half-day to full-day shoot |
| In-house photo setup | $200 | $500 | Lightbox, backdrop, macro lens |
| Shopify theme customization (if hiring help) | $0 (DIY) | $3,000 (freelancer) | Depends on technical comfort |
| **Total one-time** | **$1,212** | **$12,850** | |

### Monthly ongoing costs

| Item | Low estimate | High estimate | Notes |
|------|-------------|---------------|-------|
| Shopify plan | $39 | $105 | Basic or Shopify tier |
| Etsy sync app | $20 | $30 | CedCommerce or similar |
| Email tool (Klaviyo/Mailchimp) | $0 | $20 | Free tier to start |
| Domain renewal | $1 | $4 | Annual, averaged monthly |
| **Total monthly** | **$60** | **$159** | |

### What this doesn't include

- Ongoing content production labor (social media, stories, newsletter) — someone's time
- Transaction fees (Shopify Payments: 2.9% + $0.30 per transaction)
- Paid advertising (not recommended at launch — organic + existing customer base first)
- Legal review of terms/policies for the new site
- Trademark search for "Grace Gems" (recommended before major brand investment)

---

## 9. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| gracegems.com is taken or expensive | Delays launch, weakens brand | Check immediately; have .co and shopgracegems.com as fallbacks |
| Customer story outreach gets low response | Weak Stories page at launch | Start outreach early; 8–10 contacts to land 3–5; can launch with 3 |
| Photography delays | Can't launch with brand-quality imagery | Use existing Etsy photos as temporary; prioritize hero shots |
| Etsy-to-Shopify product migration is messy | Broken listings, lost data | Use a migration tool; migrate in batches; test before going live |
| SEO drop during transition | Temporary traffic loss | Don't deindex Etsy; build new site SEO in parallel; expect 3–6 month ramp |
| Content production isn't sustainable | Site goes stale after launch | Set realistic cadence (1 story/month, 2–3 social/week); batch content |
| "Made for you" inquiries overwhelm capacity | Can't deliver on the brand promise | Start with a manageable inquiry flow; set response time expectations clearly |

---

## 10. Decision checklist

Before build can begin, these decisions need to be made:

- [x] **Domain:** Acquired
- [x] **Platform:** Shopify (Basic plan, $39/mo, free Dawn theme)
- [x] **Photography:** Acquired
- [x] **Customer stories:** Use existing Etsy reviews — no separate outreach needed
- [x] **Budget:** Under $500 one-time setup (DIY with free theme)
- [x] **Timeline:** 4–6 weeks to launch
- [x] **Who builds:** Owner with AI assistance (Claude)
- [x] **Trademark:** Deferred — LLC is registered; federal trademark is a future action, not a launch blocker
- [x] **Legal:** Adapt existing Etsy policies (returns, shipping, privacy) in brand voice for Shopify site
