# Contributing to Configr

First off, thank you for considering contributing to Configr! It's people like you that make Configr better for everyone.

This document provides guidelines and steps for contributing to this project.

## Code of Conduct

By participating in this project, you are expected to uphold our principles of openness, respect, and inclusivity. We welcome contributions from everyone regardless of gender, race, ethnicity, or any other factor. Contributions are evaluated solely on their merit.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git

### Setting Up Your Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/configr.git
   cd configr
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Making Changes

1. Create a new branch:
   ```bash
   git checkout -b my-branch-name
   ```
   
   Choose a descriptive branch name that reflects the changes you're making.

2. Make your changes
3. Test your changes:
   ```bash
   pytest
   ```
   Ensure all existing tests pass. If you've modified functionality, add or update tests accordingly.

4. Follow PEP 8 coding standards
   - While no specific linter is required, your code should adhere to PEP 8 guidelines.

## Submitting Changes

1. Push your changes to your fork:
   ```bash
   git push origin my-branch-name
   ```

2. Submit a pull request on GitHub
   - Provide a clear description of the problem and solution
   - Include any relevant issue numbers by using keywords like "Fixes #123" or "Resolves #123"
   - Explain your approach and the reasoning behind your changes

## Pull Request Process

1. Update documentation if your changes modify the behavior or structure of the code
2. Ensure your code passes all tests
3. Your pull request will be reviewed by maintainers
4. Address any feedback or requested changes
5. Once approved, your pull request will be merged

## Documentation

If your contribution changes how users interact with the project or modifies its functionality, please update the relevant documentation. Pull requests that change functionality without updating documentation may be rejected.

## Communication

- For bug reports, feature requests, or discussions, please open an issue on GitHub
- For questions or clarifications about contributing, open a discussion on GitHub

## Recognition

Contributors will be acknowledged in our README.md file. Significant contributors may be added to a CONTRIBUTORS.md file in the future. All contributions remain visible and attributed in the Git history.

## Additional Resources

- <a href="https://docs.github.com/en/github/collaborating-with-pull-requests" target="_blank">GitHub Pull Request Documentation</a>
- <a href="https://peps.python.org/pep-0008/" target="_blank">PEP 8 Style Guide</a>

Thank you for contributing to Configr!