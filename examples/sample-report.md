# Skill collision check

**Roots:** `fixtures/skills`  
**Skills scanned:** 8  **Threshold:** 0.30  **Near-dup ratio:** 0.85

**Disposition:** 3 KEEP, 3 TUNE, 2 COLLISION

| Status | Skill | Detail |
|---|---|---|
| COLLISION | note-taker | collides with quick-capture (shared: 'capture an idea', capture, idea, later, quick, triage; jaccard 0.59) |
| COLLISION | quick-capture | collides with note-taker (shared: 'capture an idea', capture, idea, later, quick, triage; jaccard 0.59) |
| TUNE | daily-standup | narrow daily-standup's trigger; it is shadowed by standup-recap |
| TUNE | set-reminder | narrow set-reminder's trigger; it is shadowed by broad-reminder |
| TUNE | standup-recap | when-to-use wording is 94% similar to daily-standup; add a disambiguating clause |
| KEEP | broad-reminder | - |
| KEEP | changelog-writer | - |
| KEEP | deploy-checklist | - |

## Collision pairs (1)

- **note-taker <-> quick-capture** (score 0.59)  
  shared trigger phrases: 'capture an idea'  
  shared keywords: capture, idea, later, quick, triage

## Shadowed skills (2)

- **set-reminder** is shadowed by **broad-reminder**  
  suggestion: narrow set-reminder's trigger; it is shadowed by broad-reminder
- **daily-standup** is shadowed by **standup-recap**  
  suggestion: narrow daily-standup's trigger; it is shadowed by standup-recap

## Near-duplicate when-to-use wording (1)

- **daily-standup <-> standup-recap** - text-similarity ratio 0.94