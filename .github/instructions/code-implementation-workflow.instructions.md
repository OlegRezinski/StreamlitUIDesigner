# Milestone Workflow

This workflow applies to each milestone to ensure quality, maintainability, and steady progress.

## 1. Plan and Implement (Software Engineer)
- Review milestone scope and acceptance criteria.
- Break the milestone into small, testable tasks.
- Implement core logic first (models, registry, codegen), then UI wiring.
- Keep changes modular and aligned with architecture boundaries.
- Update or add minimal documentation if behavior changes.

## 2. Test Design and Execution (Software Tester)
- Create or update test cases for new or changed behavior.
- Run unit tests for core logic and code generation.
- Add integration or smoke tests for milestone-level flows.
- Report failures with clear reproduction steps and expected vs actual results.
- Return issues to the Software Engineer for fixes.

## 3. Code Review (Code Reviewer)
- Review for correctness, regressions, and edge-case failures.
- Flag antipatterns, risky constructs, and maintainability issues.
- Check alignment with architecture and milestone acceptance criteria.
- Recommend missing tests or validation improvements.
- Pass findings to Software Engineer and Software Tester.

## 4. Iterate Until Clean
- Software Engineer fixes issues and refactors as needed.
- Software Tester updates or adds tests and re-runs them.
- Code Reviewer re-checks changes and clears findings.
- Repeat steps 2–4 until tests pass and review feedback is resolved.

## Done Criteria
- All milestone acceptance criteria are met.
- Tests pass without retries or manual fixes.
- Code reviewer has no remaining findings.
- Documentation updates (if any) are complete and accurate.

