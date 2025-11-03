# prreview

Review the current branch as a pull request. Suggest improvements but don't make them.

## Instructions

1. Run `git diff $(git merge-base HEAD main)..HEAD > ./pr.diff` to create PR diff against main
2. Run `ls` to confirm the file was created
3. Read `./pr.diff` to review all changes in this branch

Then analyze in priority order:

1. **LOC (Lines of Code)**:
   - Are they concise/elegant or overly verbose?
   - Clean & readable without extra unnecessary code?
   - We prefer "cutting corners" to simplify code and align user experiences
   - OK to interpret spec in a way that simplifies implementation

2. **DRY**: Are the changes DRY with the rest of the codebase? Reuse existing functions?

3. **Non-defensive**:
   - Avoid patterns like try/except
   - Don't catch edge cases that never actually happen in the logic

4. **Regressions**: Do they introduce regressions? How do they change the business logic?

5. **SPEC alignment**: Are they aligned with the SPEC? (@CURRENT_SPEC.md)

6. **Test alignment**: Are tests aligned with docs/TEST_PATTERNS.md and ./tests/README.md?

This PR comes from an inexperienced dev. Please suggest (but do not make) critical improvements.