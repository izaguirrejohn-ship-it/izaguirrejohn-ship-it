# Lisbon field note: local time is not yet a timestamp

**Research date: 15 September 2026.** A small public-source case study for Signal Atlas Data Quality 1.0.0. These are actual event listings; this is not an audit of Signal Atlas's production feed.

## The question

What must happen between reading an event page and storing an event that a city guide can safely reason about?

We manually transcribed the date, local start time and venue from three public listings, with two source records per event. Our intermediate import preserves the displayed clock times without adding an offset. The checker flags those incomplete timestamps. We then explicitly interpret these reviewed Lisbon dates using Python's `Europe/Lisbon` time-zone data and run the same checks again.

These findings concern **our import representation**, not mistakes by the event organizers. No errors were planted in the real-source fixtures, and no disagreement between the selected source start times was found.

## Records reviewed

| Listing | Local start | Reviewed UTC start | Venue | Sources |
| --- | --- | --- | --- | --- |
| A Hard Day’s Night (1964) | 19 September 2026, 17:00 | 19 September, 16:00Z | Grande Auditório, Fundação Calouste Gulbenkian | [Event page](https://gulbenkian.pt/agenda/a-hard-days-night-1964/) · [Gulbenkian agenda on homepage](https://gulbenkian.pt/) |
| Don’t Look Back (1967) | 19 September 2026, 20:00 | 19 September, 19:00Z | Grande Auditório, Fundação Calouste Gulbenkian | [Event page](https://gulbenkian.pt/agenda/dont-look-back-1967/) · [Gulbenkian agenda on homepage](https://gulbenkian.pt/) |
| Sinfonia n.º 5 de Beethoven — OML e Steven Isserlis | 27 September 2026, 17:00 | 27 September, 16:00Z | Grande Auditório, Centro Cultural de Belém | [CCB programme on homepage](https://www.ccb.pt/) · [Promoter's BOL listing](https://ccb.bol.pt/Comprar/Bilhetes/179735-sinfonia_no_5_de_beethoven_oml_e_steven_isserlis-ccb/) |

The UTC offset is **our explicit geographic/date interpretation**: Lisbon uses `+01:00` on these dates. It is not a quoted field from the source pages. The converter is narrowly scoped to this case's dates; it is not a general solution for ambiguous daylight-saving times.

The two Gulbenkian pages and their homepage are the same publisher, not independent corroboration. The CCB homepage and its linked promoter ticket listing are also related sources. Agreement improves consistency evidence, not source independence.

## Reproducible result

| Representation | Events | Source records | Errors | Warnings | Result |
| --- | --- | --- | --- | --- | --- |
| Local clock times as collected | 3 | 6 | 9 | 0 | Fail: missing UTC offsets |
| Explicitly normalized times | 3 | 6 | 0 | 0 | Pass: configured field checks |

The nine findings correspond to three event starts and six source starts. Normalization changes only those timestamps. Titles, venues, source URLs and recorded review times remain the same.

From the project directory:

```bash
python3 check_events.py case-study/collected-local-times.json --as-of 2026-09-15T14:44:41Z
python3 case-study/normalize.py
python3 check_events.py case-study/normalized-events.json --as-of 2026-09-15T14:44:41Z
```

The first command returns exit code `1`. The second prints the reviewed normalized feed. The third returns `0`. Both checker runs use a seven-day example source-age limit.

[Collected input](collected-local-times.json) · [Normalized input](normalized-events.json) · [Before report](before-report.md) · [After report](after-report.md) · [Source ledger](sources.json)

## What still needs human judgement

**A film's running time is not the full session.** The film pages describe an introduction as well as a screening. We leave event end times absent rather than infer a session end by adding the film duration. Similarly, the concert listing includes a separate pre-concert conversation; its time is not the concert start. The [promoter listing](https://ccb.bol.pt/Comprar/Bilhetes/179735-sinfonia_no_5_de_beethoven_oml_e_steven_isserlis-ccb/) distinguishes the 16:30 conversation from the 17:00 session.

**Flattened page text can misrepresent status.** Web text extraction included both cancellation and sold-out labels around the film times. Direct browser inspection of the first film's rendered page showed the ordinary Saturday 17:00 listing, without those status labels in the visible event block. We did not convert hidden/template text into a claim that either film was cancelled or sold out. Ticket availability remains unverified.

**Freshness describes this review.** `checked_at` records the research batch snapshot at 14:44:41 UTC on 15 September. It is not the publisher's last-updated time or evidence of a background monitor. Homepages are mutable; recheck the linked event pages before relying on this dated dataset.

**A pass is a bounded result.** It verifies the configured structure and consistency checks. It does not authenticate the sources, confirm availability, guarantee that an event will occur or authorize publishing a recommendation. This case establishes a repeatable import review, not a measured production improvement or user outcome.
