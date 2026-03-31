# Upgrading from v1

Migration guide from v1 (with CEO department) to v2.

## Auto-Detection

When you run `/company`, it detects the existence of `.company/ceo/` and suggests an upgrade.

```
> /company

Secretary: I've detected an existing organization (v1). Would you like to upgrade to v2?

      Changes:
      - CEO department → Removed (secretary handles routing directly)
      - Review department → Removed (secretary manages this)
      - Active departments → Carried over as-is
      - Empty departments → Deleted

      Shall I proceed with the upgrade?
```

## What Changes

| v1 | v2 |
|----|-----|
| CEO routes tasks | Secretary routes directly |
| All departments created at setup | Start with secretary only |
| Review department always present | Secretary handles reviews |
| 4-question onboarding | Just 2 questions |

## Migration Process

1. Existing owner info (business, mission, etc.) is carried over
2. `ceo/` folder is deleted
3. `reviews/` folder is deleted (if present)
4. Empty departments with no real content are deleted
5. `.company/CLAUDE.md` is regenerated in v2 format
6. `secretary/CLAUDE.md` is updated to v2 version

::: warning Note
Active departments (those with actual files) are NOT deleted. You can upgrade safely.
:::

## If You Decline

If you decline, you continue running on v1. The upgrade will be suggested again next time you run `/company`.
