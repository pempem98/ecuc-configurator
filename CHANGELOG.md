# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-15

### Added

#### Models
- feat(model): add ECUC data models for AUTOSAR configuration
  - ECUCParameterValue with type validation
  - ECUCContainerValue with hierarchical structure
  - ECUCModuleConfigurationValues for BSW modules
  - ECUCValueCollection as top-level container
  - ECUCProject with metadata support
  - AutosarVersion enum (AR4.2.2, AR4.5.0)
  - ECUCParameterType enum (INTEGER, FLOAT, BOOLEAN, STRING, REFERENCE, ENUMERATION)

- feat(model): enhance CANMessage model
  - Add length property as alias for dlc
  - Add is_tx() and is_rx() methods
  - Support both length and dlc parameters in constructor

- feat(model): enhance LINNetwork model
  - Add baudrate property (converts kbps to bps)
  - Add nodes property (combines master and slave nodes)

#### Service Layer
- feat(service): implement ECUCService for configuration generation
  - Load CAN networks from DBC files
  - Load LIN networks from LDF files
  - Data validation (duplicate IDs, signal boundaries)
  - Generate ECUC projects with multiple modules
  - Support AR4.2.2 and AR4.5.0
  - Source file tracking
  - Summary statistics

- feat(service): add BSW module generation
  - CanIf (CAN Interface) module generation
  - Can (CAN Driver) module generation
  - LinIf (LIN Interface) module generation
  - Lin (LIN Driver) module generation

- feat(service): implement data validation
  - Duplicate CAN message ID detection
  - Duplicate LIN frame ID detection
  - Signal boundary checking
  - Cross-network validation

#### Generator
- feat(generator): implement ECUCGenerator for ARXML export
  - Generate AUTOSAR-compliant ARXML files
  - Support AR4.2.2 and AR4.5.0 schemas
  - Pretty printing support
  - Generate to file or string
  - Full ECUC hierarchy export

#### Tests
- test(service): add comprehensive service tests
  - Service initialization tests
  - Data loading tests
  - Validation tests
  - Generation tests
  - Integration tests
  - Total: 15 tests (all passing)

#### Documentation
- docs(service): add comprehensive service documentation
  - Service overview
  - Supported modules
  - Data validation rules
  - ECUC project structure
  - Usage examples
  - API reference
  - Error handling guide
  - Best practices
  - Performance considerations

- docs: add project README
  - Quick start guide
  - Installation instructions
  - Feature overview
  - API reference
  - Development guide
  - Roadmap

- docs: add implementation summary
  - Complete feature list
  - Test coverage report
  - Workflow diagrams
  - Success metrics

#### Examples
- feat(examples): add ECUC generation example
  - Full workflow demonstration
  - AR4.2.2 example
  - AR4.5.0 example
  - Generated ARXML output

### Changed
- refactor(loader): update DBC loader to use CANDatabase
- refactor(loader): update imports for renamed models

### Fixed
- fix(model): resolve field naming inconsistency (dlc vs length)
- fix(model): add missing properties to LINNetwork
- fix(service): handle baudrate conversion for LIN networks

## [0.0.1] - 2025-12-10

### Added

#### Initial Implementation
- feat(model): implement base data models
  - BaseElement with UUID support
  - Identifiable for AUTOSAR elements
  - Referenceable for reference support
  - Versioned for version tracking

- feat(model): implement CAN data models
  - CANSignal with bit-level positioning
  - CANMessage with DLC and signals
  - CANNode representation
  - CANDatabase container
  - ValueTable for signal values

- feat(model): implement LIN data models
  - LINSignal definition
  - LINFrame with frame types
  - LINNode with master/slave types
  - LINNetwork structure
  - ScheduleTable and ScheduleEntry

- feat(model): implement ECU data models
  - Parameter definition
  - Container structure
  - Module configuration
  - ECUConfiguration container

- feat(model): implement AUTOSAR data models
  - DataElement definition
  - PortInterface (SenderReceiver, ClientServer)
  - Port definition
  - Component structure
  - Package hierarchy

- feat(loader): implement base loader framework
  - Abstract BaseLoader class
  - CachedLoader with caching support
  - Custom exceptions
  - File validation utilities

- feat(loader): implement DBC loader
  - Parse DBC files using cantools
  - Convert to CANDatabase model
  - Handle value tables
  - Extract nodes
  - Support extended frames

- feat(loader): implement LDF loader
  - Parse LDF files with regex
  - Convert to LINNetwork model
  - Parse frames and signals
  - Parse schedule tables
  - Handle master/slave nodes

- test(model): add model tests (17 tests)
- test(loader): add DBC loader tests (10 tests)
- test(loader): add LDF loader tests (12 tests)

- docs(model): add model documentation
- docs(loader): add loader documentation
- docs: add Copilot instructions for development

### Notes
- Project follows PEP 8 style guide
- Uses Pydantic v2 for data validation
- Python 3.8+ required
- Supports AUTOSAR AR4.2.2 and AR4.5.0

[Unreleased]: https://github.com/yourusername/ecuc_configurator/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/ecuc_configurator/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/yourusername/ecuc_configurator/releases/tag/v0.0.1
