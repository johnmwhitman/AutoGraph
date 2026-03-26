import sys
sys.path.insert(0, r'C:\AI\autograph')
try:
    from analytics import log_event, hash_ip
    log_event('smoke_test', client_slug='diag_check')
    print('ANALYTICS IMPORT OK')
except Exception as e:
    print(f'ANALYTICS IMPORT FAILED: {e}')
