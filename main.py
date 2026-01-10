import subprocess

# Phase 1: Data generation
subprocess.run(["python", "src/generate_data.py"])

# Phase 2: Run data quality checks
subprocess.run(["python", "src/run_data_quality_checks.py"])

# Phase 4: Historical logging
subprocess.run(["python", "src/run_data_quality_historical.py"])

print("All phases executed successfully.")
