---
name: flight-search
description: >-
  When to read: 'cheapest flight', 'find a flight', 'direct flight from X to
  Y', or a fare for a trip. Use for: searching flights for a route, date, and
  party and comparing delivered totals. Does: runs the search through the
  system flight-booking skill and Google Flights, compares total price and
  travel time, verifies baggage and check-in, and records PNR and prices.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Flight Search

Find the cheapest flight for a route, date, and party, and compare offers
by delivered total — not headline fare.

## This skill is a thin router, not a search engine

The real mechanism is the system `flight-booking` skill
(`/opt/muse/skills/flight-booking/SKILL.md`): connector flight sources
searched at once, `flights merge` into one list of trips with booking
routes, Google Flights browser read beside the connectors so airlines no
connector sells are covered. Read that skill and follow it. Do not
reinvent search, merge, or booking here.

## Inputs — collect first, never assume

Route (origin / destination airports), date(s), adults / children, cabin,
direct-only or max stops, departure time window, budget if any.

Standing defaults from Bryan's trips — verify against the current ask,
never assume they still hold:

- Home airport SIN. 1 adult, economy, unless stated otherwise.
- Shanghai exchange outbound: preferred Sun 14 Feb or Mon 15 Feb 2027,
  one-way, direct preferred, depart SIN 06:00–14:00 SGT, no red-eye.

Saved travel preferences, when they exist, live in
`~/memory/travel/PROFILE.md` (home airports, airlines, cabin, seat, stops,
loyalty). Earlier bookings live in `~/memory/travel/HISTORY.md` — when a
route repeats, follow the earlier booking. What Bryan says in this
conversation takes precedence over both files.

## Compare by delivered total

- Rank by total price for the whole party and total travel time, not the
  headline fare. A cheap fare with a paid bag and a 6-hour layover is not
  the cheapest trip.
- ShopBack and Agoda flight results are text leads with links, not offers:
  mention them under the merged list, never in it.
- **Settled decision SD-001** (`~/workspace/settled-decisions.md`): ShopBack
  estimates are NOT the stored low. ShopBack prices are partner estimates
  after cashback — they never count as a new low and never replace the
  stored low. Check settled decisions before claiming a new low.

## Verify before reporting a price

A price without baggage and check-in terms is incomplete. Verify each:

- Baggage included? Budget carriers on Bryan's bookings carry no free
  checked baggage: Jetstar 7 kg carry-on only, Scoot 10 kg carry-on only.
- Check-in opens when? Jetstar opens 48 h before departure.
- Terminal, meal included or not, change / cancellation terms.

Standing reference points (verify live, prices move):

- Shanghai tracker stored low: Spring 9C8552, 15 Feb 06:30–11:45, $311
  via Google Flights 2026-11-28 (Agoda $312 confirms; was $321).
  14 Feb is $349 Google Flights / $350 Agoda (was $400).
- Bali Dec 2026, booked: Jetstar JQ089 SIN T2→DPS, Sat 5 Dec 19:25–22:15,
  PNR FJESMY, S$104.88; Scoot TR239 DPS→SIN T1, Wed 9 Dec 16:25–19:20,
  PNR LG1KQK, S$105.30. Total S$210.18. Both economy, no meals, no free
  checked baggage. Jetstar check-in opens 3 Dec 19:25 SGT.

## Record the result

For the picked trip, record: route, date, flight number(s), times,
total price + source, baggage, and PNR once booked. Keep the record with
the trip (calendar event, tracker state, or `~/memory/travel/HISTORY.md`
as the trip's home dictates) — a price with no record is lost the next
time the fare moves.

## Booking and tracking

- Booking follows the trip's route from the merged list: a Duffel offer
  books with Muse; an airline's own fare books on the airline's website
  in a visible browser task; a link-only fare is a hand-off. Never book
  without Bryan explicitly picking the trip.
- The Shanghai flight price tracker cron runs daily ~10:54 SGT and alerts
  on a new low only. This skill is the manual search path, not the tracker
  — do not duplicate its runs, and do not report a tracker alert as a
  search result.
