from pathlib import Path

# Test file to verify package structure
if __name__ == '__main__':
    repo_root = Path(__file__).parent
    print(f"Repository root: {repo_root}")
    
    # List key files
    key_files = [
        'README.md',
        'setup.py',
        'requirements.txt',
        'docker-compose.yml',
        'src/detector.py',
        'src/streaming_app.py',
        'src/producer.py',
        'src/alerts_consumer.py',
        'tests/test_detector.py',
        'docs/architecture.md',
        'docs/deployment.md',
        'docs/tuning.md',
    ]
    
    print("\nProject structure:")
    for file in key_files:
        path = repo_root / file
        status = '✓' if path.exists() else '✗'
        print(f"  {status} {file}")
