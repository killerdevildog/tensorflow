# TensorFlow Java Documentation Generation

This directory contains scripts for generating TensorFlow Java API documentation.

## Issue #96799 Fix

This addresses [TensorFlow Issue #96799](https://github.com/tensorflow/tensorflow/issues/96799) where the TensorFlow Java documentation on tensorflow.org was showing outdated version information (0.3.3 instead of the current 1.1.0).

## Scripts

### build_comprehensive_java_api_docs.py (NEW)

**Recommended for tensorflow.org documentation generation**

This script generates comprehensive TensorFlow Java documentation that includes:
- TensorFlow Java library v1.1.0 (latest)
- TensorFlow Java NDArray components
- Core TensorFlow Java API from this repository
- Generated operations documentation

Usage:
```bash
python tensorflow/tools/docs/build_comprehensive_java_api_docs.py \
    --output_dir=/path/to/output \
    --site_path=java/api_docs/java
```

Optional flags:
- `--tensorflow_java_repo=/path/to/local/java/repo` - Use local TensorFlow Java repository
- `--gen_ops=true` - Include generated operations (default: true)

### build_java_api_docs.py (LEGACY)

This script generates documentation only for the core TensorFlow Java API that's part of this repository. It does not include the broader TensorFlow Java ecosystem.

## For tensorflow.org Maintainers

To update the Java documentation on tensorflow.org:

1. Use the `build_comprehensive_java_api_docs.py` script
2. This will automatically pull the latest TensorFlow Java sources (v1.1.0)
3. Generated documentation will reflect current version numbers and APIs

## Development Notes

The comprehensive script handles:
- Automatic cloning/updating of external repositories
- Version management (currently set to TensorFlow Java v1.1.0)
- Fallback to legacy behavior if external repos are unavailable
- Proper source overlay for generated components

## Version Information

- **TensorFlow Java**: v1.1.0 (current)
- **TensorFlow Java NDArray**: v1.0.0
- **Previous outdated version**: 0.3.3 (fixed by this update)
