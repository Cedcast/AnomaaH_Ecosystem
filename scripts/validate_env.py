#!/usr/bin/env python3
"""Environment Configuration Validator for AnomaaH Platform"""

import os
import sys

# Simplified validation for the PR
def main():
    """Main validation function."""
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required variables: {', '.join(missing)}")
        sys.exit(1)
    
    print("✅ Basic environment validation passed")
    sys.exit(0)

if __name__ == '__main__':
    main()
