# My Personal AI Playbook

A one-page guide to how I work with AI coding tools, based on my experience across the
AI-Assisted Coding course (building the Task Tracker, the mid-course project, and the final
release-readiness work).

## When I reach for AI first

- Explaining things I don't fully understand yet, and drafting documentation.
- Repetitive or boilerplate work, like the frontend CSS and rendering, where AI is faster
  than writing it by hand.
- Setting up config files I don't know well (CI, Docker), as long as I verify them by running.

## When I do not reach for AI first

- When I actually need to learn something myself. If I let AI do it, I don't learn it, so
  I slow down and work through it on my own first.
- When a change touches the core app logic or business rules that I'm responsible for owning.

## My non-negotiables

- I always run and test AI's code myself before trusting it. I don't accept output because
  it looks right.
- I never paste real secrets, credentials, .env values, or tokens into an AI tool. Only
  placeholder config like PORT=8000.
- I don't submit a line, command, or config I can't explain.

## My review rules

- I run the command myself to prove it works. In this project that meant running pytest,
  building and running the Docker container, and checking /health returned 200 before
  trusting any of it.
- I grade each AI suggestion Useful, Noise, or Wrong (or Valid / False Positive / Noise for
  security findings), with a written reason. I reject the ones that sound reasonable but
  would break a correct decision.
- I compare what the AI says against the real files, not against how confident it sounds.

## What I am still figuring out

- How much to rely on AI versus learning things myself. AI makes it easy to move fast, but
  moving fast is not the same as understanding, and I'm still finding the right balance.

## Decision Card

- For a new feature I reach for: general chat, for reasoning and drafting, then I verify
  against the real code myself.
- For code review I reach for: grading each comment Useful / Noise / Wrong, the way I did in
  this project.
- For debugging I reach for: breaking the code on purpose to prove the fix works, the way I
  did in the debugging log.
- For infrastructure I reach for: following the exact course prompts, then verifying by
  actually building and running it.
- I will never paste: real secrets, credentials, .env values, or tokens into an AI tool.
- My one rule is: always run and test AI's work myself before I trust it.

## Re-read reminder

I will re-read this playbook 30 days from today to check whether these rules still match how
I actually work.
