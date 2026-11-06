PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE := 1
.PHONY: doctor validate eval collector-status collector-verify
doctor:
	$(PYTHON) -B scripts/doctor.py
validate:
	$(PYTHON) -B scripts/validate_lab.py
eval:
	$(PYTHON) -B scripts/run_evals.py --smoke --no-report
collector-status:
	$(PYTHON) -B scripts/collector_service.py status
collector-verify:
	$(PYTHON) -B scripts/collector.py verify


# claude-terminal-default:v1
.PHONY: claude-terminal-test claude-terminal-status
claude-terminal-test:
	$(PYTHON) -B tests/test_claude_terminal.py -v
	$(PYTHON) -B tests/test_claude_terminal_launch.py -v
claude-terminal-status:
	$(PYTHON) -B scripts/claude_terminal/claude_cli_launch.py --status
# /claude-terminal-default:v1
