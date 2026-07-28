# SegmentFault Platform Profile

Platform ID: `segmentfault`

## Position

- Purpose: focused technical diagnosis and explanation in a question-and-answer community.
- Reader intent: understand why a specific technical problem occurs and how to verify a solution.
- Best fit: debugging, language or framework behavior, architecture decisions, and concise technical answers.

## Write

- Title: phrase the precise technical question or failure condition.
- Opening: provide the short answer and the smallest relevant environment description.
- Structure: symptom, minimal reproduction, root cause, solution, verification, and relevant alternatives.
- Voice: concise, analytical, and explicit about assumptions.
- Depth: show only the code and configuration needed to explain causality; link broader background rather than diluting the answer.
- Links: cite official documentation, specifications, or source code when the explanation depends on them.
- Ending: state the general rule or diagnostic heuristic readers can reuse.

## Visuals

- Prefer text, code, traces, and small diagrams; use screenshots only when UI state is part of the issue.
- Make logs and errors selectable and redact unrelated data.

## Avoid

- Restating the question for several paragraphs, listing fixes without a cause, broad product promotion, and unsupported certainty.
- Large tutorial detours that do not help resolve the stated problem.

## Platform QA

- Confirm the minimal reproduction, causal explanation, fix, and success signal agree.
- Check that alternative solutions are distinguished by conditions rather than ranked arbitrarily.
