# Ticket to Ride Botmaking Tournament

## Overview
Welcome to the inaugural Ticket to Ride Botmaking Tournament!  
Build and pit your Ticket to Ride bots against one another in a structured competition.

## Key Dates
- Make a pull request and work on your own branch with your name on it; to submit, make a merge request.  
- Bot turn-in deadline: **August 1, 2025**  
- Showing: **TBD**

## Prerequisites
- **Languages & Frameworks:** Python 3.8+

## Installation
Clone this repository:

## Where to Put Your Bot
Your bot lives under the `bots/` directory in its own folder:

```text
ticket_to_ride/
├── Interfaces/
│   ├── your bot goes here
└── maps/
```

## How to Start a Game With It
- Refer to `main.py`  
- `--rounds`: how many times each pairing plays

## Tournament Format

### Round-Robin
- Each win awards victory points based on the stage.
- At the end, the bot with the most points wins.
- Ties are resolved by having the tied players face off in additional rounds until one bot has ≥ 20% of total points.

#### Point Structure
| Stage          | Points per Win |
| -------------- | -------------- |
| 4-player stage | 1              |
| 3-player stage | 2              |
| 2-player stage | 4              |

## Scoring
- **Win** = highest average score across all rounds

## Submission Guidelines
- Send a merge request to `main` with your final bot  
- Ensure it passes local tests  
- Submit by **August 1, 2025 at 23:59 CDT**

## Rules & Regulations
- **Time Limit:** 2 seconds per move  
- **No Networking:** bots must not make external calls  
- **Fair Play:** disqualification for cheating or rule violations

## FAQs
**Q:** My bot crashes sometimes. What then?  
**A:** It will forfeit that match (0 points). Test thoroughly before submitting.  
