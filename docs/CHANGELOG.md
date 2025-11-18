# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial project setup and structure
- Main automation script for JotForm payment requests
- Support for 3-stage approval workflow (Inputter → PCM → RD)
- Automated PDF invoice generation for testing
- Screenshot capture at each stage
- Configuration management via `config.py`
- Utility functions for common operations
- Comprehensive README with setup instructions
- Unit tests framework with sample tests
- Setup script for easy initialization
- Example environment file for configuration
- Git ignore rules for Python projects

### Features
- Headless browser automation using Playwright
- Automatic EFS reference extraction
- Organized output folders by EFS reference
- Error handling and retry logic
- Configurable test data and settings
- Support for Sponsorship/Charitable Donation payment type

### Documentation
- Detailed README with usage instructions
- Code comments and docstrings
- Setup and troubleshooting guides

## [Unreleased]

### Planned
- Support for all 6 payment types
- Email approval workflow integration
- Batch processing capabilities
- Test report generation
- CI/CD integration
- Configuration via environment variables
- Rejection flow testing
- Enhanced error reporting
- Performance optimizations

---

## Version History

### How to Release

1. Update version number in this file
2. Update README if needed
3. Commit changes: `git commit -m "Release v1.0.0"`
4. Tag release: `git tag -a v1.0.0 -m "Release version 1.0.0"`
5. Push: `git push origin main --tags`
