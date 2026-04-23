# Changelog

## [1.0.0] - 2026-04-15

### Added
- Initial release of AUN adapter skill
- Complete AunAdapter implementation with end-marker protocol
- Session state tracking and auto-reset on new messages
- AUN context injection (Chinese) on first message per session
- Interactive install/uninstall script
- Integrity check script with 11 validation points
- Comprehensive test suite (16 tests)

### Changed
- Moved from `~/.hermes/skills/networking/aun-adapter/` to `~/.hermes/skills/aun-adapter/`
- Merged `uninstall.py` into `install.py` (interactive menu)
- Removed `references/` directory (spec kept in main docs only)

### Fixed
- Added third authorization map (`_get_unauthorized_dm_behavior`) to SKILL.md
- Updated SKILL.md insertion point descriptions for Hermes 2026-04-15+ (QQBOT is now last platform)
- Fixed disconnect test mock reference issue

### Technical Details
- Compatible with Hermes commit eda5ae5a (2026-04-15)
- Requires Python 3.11+
- Dependency: aun-core (auto-installed)
- Base adapter API: fully compatible with current BasePlatformAdapter
