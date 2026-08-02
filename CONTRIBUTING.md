# Contributing

Thank you for considering a contribution to Lumiere! 🎉

We welcome bug fixes, improvements, documentation updates, and new features. To keep the review process efficient, please follow the guidelines below.

## Before You Begin

If you're working on a substantial change - such as a new feature, an architectural improvement, or a large refactor - please start by opening a GitHub Discussion or Issue. This gives us a chance to discuss the proposed direction before implementation.

Smaller contributions, such as documentation improvements, typo fixes, bug fixes, or minor refactoring, can be submitted directly as Pull Requests.

## Setting Up Your Environment

See the [Development Guide](development.md) for instructions on:

- setting up the local development environment;
- running the application with Docker Compose;
- installing Git hooks;
- running formatting and linting tools.

## Dependencies

To reduce supply chain risk, Pull Requests from external contributors must **not** modify `pyproject.toml` or `uv.lock`.

If your contribution requires adding, removing, or updating a dependency, please open a Discussion or Issue first so we can review the proposal before implementation.

## Before Opening a Pull Request

Please make sure that:

- all pre-commit hooks pass successfully;
- the application runs correctly;
- tests are added or updated when necessary;
- documentation is updated if your changes affect the developer or user experience.

Keeping Pull Requests focused on a single logical change makes them much easier to review.

## AI-Assisted Contributions

AI tools are welcome as part of the development workflow. However, every Pull Request should reflect meaningful human review and understanding.

Before submitting a contribution, ensure that you have reviewed, tested, and validated the generated code yourself. You should be able to explain the implementation and justify the design decisions made in your changes.

## Questions

If anything is unclear, feel free to open a GitHub Discussion or Issue before you start working on a contribution.
