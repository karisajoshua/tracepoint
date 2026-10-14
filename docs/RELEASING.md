# Release and deployment checklist

Tracepoint is pre-1.0 and not production-ready. Green CI is not security certification.

## Before a release

1. Review the changelog and linked issues.
2. Confirm required CI checks pass on the exact release commit.
3. Review dependency changes and CodeQL alerts.
4. Validate API contracts, migrations, and rollback behavior.
5. Validate the public dashboard with synthetic data only.
6. Verify environment variables contain no secrets in browser bundles.
7. Record known limitations and publish release notes.

## Deployment validation

Verify the deployed commit SHA, Vercel build state, 2D and 3D map rendering on mobile and desktop, and browser console errors. Test without exposing credentials or customer data. Treat successful CI and successful deployment as distinct checks.

## Branch protection (administrator action)

Protect main with required status checks, pull-request reviews, conversation resolution, and restricted force pushes. CODEOWNERS requests reviewers; enforcement requires repository settings. See GitHub Settings → Branches or Rules → Rulesets.
