# Contributing to VMOS API

Thank you for your interest in contributing to the VMOS API SDK! This document provides guidelines for contributing.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in [GitHub Issues](https://github.com/malithwishwa02-dot/Vmos-api/issues)
2. Create a new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce (if bug)
   - Expected vs actual behavior
   - Environment details (OS, Python/Node version, VMOS version)

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Write tests for new functionality
5. Run existing tests to ensure nothing breaks
6. Commit with clear messages: `git commit -m "Add feature X"`
7. Push to your fork: `git push origin feature/my-feature`
8. Open a Pull Request

## Development Setup

### Python SDK

```bash
cd src/python
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
isort .
mypy .
```

### TypeScript SDK

```bash
cd src/typescript
npm install

# Build
npm run build

# Run tests
npm test

# Run linting
npm run lint
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Use Black for formatting
- Use isort for imports
- Maximum line length: 88 characters

### TypeScript

- Follow the existing code style
- Use TypeScript strict mode
- Use meaningful variable names
- Add JSDoc comments for public APIs

## Documentation

- Update documentation for any new features
- Include docstrings/JSDoc for all public methods
- Add examples for new functionality
- Keep README.md up to date

## Testing

- Write unit tests for new code
- Ensure tests pass before submitting PR
- Aim for high code coverage
- Test edge cases

## Commit Messages

Use clear, descriptive commit messages:

- `feat: Add new screenshot API support`
- `fix: Handle connection timeout properly`
- `docs: Update authentication guide`
- `test: Add tests for container client`
- `refactor: Simplify node selector logic`

## Pull Request Process

1. Update documentation as needed
2. Add tests for new functionality
3. Ensure CI passes
4. Request review from maintainers
5. Address review feedback
6. Squash commits if requested

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's code of conduct

## Questions?

- Open a discussion on GitHub
- Contact maintainers

Thank you for contributing!
