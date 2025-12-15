# Contributing to ECUC Configurator

Thank you for your interest in contributing to ECUC Configurator! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive environment.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant code snippets or error messages

### Suggesting Features

Feature suggestions are welcome! Please:
- Check if the feature already exists
- Provide clear use case
- Explain expected behavior
- Consider implementation complexity

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   pytest
   pytest --cov=src/autosar
   ```

5. **Commit your changes**
   - Use conventional commits format (see below)
   - Write clear commit messages

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Describe your changes
   - Link related issues
   - Ensure CI passes

## Development Setup

### Requirements

- Python >= 3.8
- pip
- virtualenv (recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ecuc_configurator.git
cd ecuc_configurator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/autosar --cov-report=html

# Run specific test file
pytest tests/test_service_ecuc.py -v

# Run specific test
pytest tests/test_service_ecuc.py::TestECUCService::test_service_initialization
```

### Code Quality

```bash
# Run linting
flake8 src/ tests/

# Run type checking
mypy src/

# Format code
black src/ tests/
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use Black formatter (line length: 88)
- Use isort for imports
- Add type hints to all functions
- Write docstrings (Google style)

### Type Hints

Always use type hints:

```python
def process_message(msg: CANMessage, network: CANDatabase) -> bool:
    """Process a CAN message."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def load_network(file_path: str, network_name: Optional[str] = None) -> CANDatabase:
    """
    Load CAN network from DBC file.
    
    Args:
        file_path: Path to DBC file
        network_name: Optional network name (defaults to filename)
        
    Returns:
        Loaded CAN network
        
    Raises:
        FileNotFoundError: If file does not exist
        ParserError: If parsing fails
    """
    pass
```

### Error Handling

- Use custom exceptions
- Provide helpful error messages
- Log errors appropriately

```python
try:
    network = load_dbc(file_path)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    raise
except ParserError as e:
    logger.error(f"Failed to parse DBC: {e}")
    raise
```

### Testing

- Write tests for new features
- Maintain test coverage above 80%
- Use descriptive test names
- Test both success and failure cases

```python
class TestECUCService:
    """Test suite for ECUC Service."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = ECUCService()
        assert service.autosar_version == AutosarVersion.AR_4_2_2
    
    def test_validation_duplicate_ids(self):
        """Test validation catches duplicate IDs."""
        # Test implementation
        pass
```

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Scopes

- `model`: Data models
- `loader`: File loaders
- `service`: Service layer
- `generator`: Code generators
- `test`: Tests

### Examples

```
feat(service): add XLSX loader support

Implement XLSX loader to read ECU configuration from Excel files.
Supports multiple sheets for signals, messages, and nodes.

Closes #123

---

fix(loader): handle empty DBC files gracefully

Previously, empty DBC files would cause a crash. Now returns
an empty CANDatabase with appropriate warning.

Fixes #456

---

docs(readme): update installation instructions

Add virtualenv setup instructions and troubleshooting section.

---

test(model): add validation tests for LIN frames

Add tests for frame ID validation and signal boundary checking.
```

### Important Notes

- **Do NOT use emoji in commit messages**
- Keep subject line under 72 characters
- Use imperative mood ("add" not "added")
- Reference issues when applicable

## Pull Request Guidelines

### PR Title

Follow commit message format:

```
feat(service): add XLSX loader support
fix(loader): handle empty DBC files
docs(readme): update installation instructions
```

### PR Description

Include:

1. **Summary**: What does this PR do?
2. **Motivation**: Why is this change needed?
3. **Changes**: List of changes made
4. **Testing**: How was this tested?
5. **Related Issues**: Link to issues

Example:

```markdown
## Summary
Implements XLSX loader to read ECU configuration from Excel files.

## Motivation
Many projects store ECU configuration in Excel format.
This loader enables importing these configurations.

## Changes
- Add XLSXLoader class
- Add Excel file parsing logic
- Add model conversion
- Add tests (10 new tests)
- Update documentation

## Testing
- Unit tests: 10/10 passing
- Integration test with sample Excel file
- Manual testing with production files

## Related Issues
Closes #123
```

### Checklist

Before submitting PR:

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow format
- [ ] No merge conflicts
- [ ] PR description complete

## Project Structure

```
ecuc_configurator/
├── src/autosar/        # Source code
│   ├── model/          # Data models
│   ├── loader/         # File loaders
│   ├── service/        # Business logic
│   └── generator/      # Code generators
├── tests/              # Test files
├── examples/           # Usage examples
├── doc/               # Documentation
└── README.md
```

### Adding New Models

1. Create model in `src/autosar/model/`
2. Inherit from appropriate base class
3. Add type hints and docstrings
4. Add field validators if needed
5. Export from `__init__.py`
6. Add tests in `tests/test_models.py`

### Adding New Loaders

1. Create loader in `src/autosar/loader/`
2. Inherit from `BaseLoader`
3. Implement abstract methods
4. Add error handling
5. Export from `__init__.py`
6. Add tests in `tests/test_loader_*.py`

### Adding New Service Features

1. Add methods to appropriate service
2. Add validation logic
3. Add error handling
4. Update documentation
5. Add tests

## Documentation

### Code Documentation

- Add docstrings to all public classes and methods
- Include type hints
- Provide usage examples where helpful

### User Documentation

- Update README.md for new features
- Add examples to `examples/`
- Update service README if needed
- Add to CHANGELOG.md

### API Changes

Document any API changes:
- Breaking changes in CHANGELOG
- Migration guide if needed
- Update version number

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update CHANGELOG.md
2. Update version in `pyproject.toml`
3. Create git tag
4. Push tag to trigger release

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

## Getting Help

- Check documentation
- Search existing issues
- Ask in discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README (for major contributions)

Thank you for contributing to ECUC Configurator!
