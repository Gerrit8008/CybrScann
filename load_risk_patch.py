#!/usr/bin/env python3
"""
Loader for risk assessment color patch
Add 'import load_risk_patch' at the top of app.py to apply the patch
"""

import logging
logger = logging.getLogger(__name__)

logger.info("Loading risk assessment color patch...")
try:
    import risk_assessment_direct_patch
    logger.info("✅ Risk assessment color patch loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load risk assessment color patch: {e}")
