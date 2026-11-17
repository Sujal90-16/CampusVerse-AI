import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DATABASE_PATH', tempfile.mktemp(prefix='campusverse-test-', suffix='.db'))
os.environ.setdefault('JWT_SECRET', 'test-secret-that-is-long-enough-for-hmac-sha256')
