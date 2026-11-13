# ABOUTME: One command per step: test, synth, perf, figures, or all of them in order.
# ABOUTME: Needs Icarus Verilog on PATH and uv; synthesis uses native yosys if present, else YoWASP.
.PHONY: all test lint synth perf figures demo clean

all: lint test synth perf figures

lint:
	uv run ruff check .

test:
	uv run pytest -q

synth:
	uv run python -m tools.synth

perf:
	uv run python -m tools.perf

figures:
	uv run python -m tools.figures

demo:
	uv run python -m tools.sim programs/tests/hazard_demo.s --config pipe_fwd --vcd build/hazard_demo.vcd --trace build/hazard_demo.trace

clean:
	rm -rf build
