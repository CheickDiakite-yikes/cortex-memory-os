from pathlib import Path

from cortex_memory_os.benchmarks import run_all, write_run


def test_synthetic_benchmarks_pass():
    result = run_all()

    assert result.passed
    assert len(result.case_results) == 47
    assert {case.suite for case in result.case_results} >= {
        "MEM-RECALL-001",
        "RETRIEVAL-SCORE-001",
        "SCOPE-POLICY-001",
        "PERF-LAT-001",
        "PERF-HISTORY-001",
        "GATEWAY-HISTORY-001",
        "MEM-LIFECYCLE-001",
        "MEM-FORGET-001",
        "SEC-INJECT-001",
        "SEC-PII-001",
        "SEC-POLICY-001",
        "DBG-TRACE-001",
        "VAULT-RETENTION-001",
        "VAULT-ENCRYPT-001",
        "GATEWAY-CTX-001",
        "CONTEXT-PACK-001",
        "CTX-HOSTILE-001",
        "CONTEXT-TEMPLATE-001",
        "CONTEXT-PACK-SELF-LESSON-001",
        "GATEWAY-PALACE-001",
        "GATEWAY-EXPORT-001",
        "SHADOW-POINTER-001",
        "SCENE-SEGMENT-001",
        "MEM-COMPILE-001",
        "GRAPH-EDGE-001",
        "SQLITE-STORE-001",
        "MEMORY-PALACE-001",
        "PALACE-FLOW-001",
        "PALACE-EXPORT-UI-001",
        "AUDIT-001",
        "EXPORT-001",
        "EXPORT-AUDIT-001",
        "SKILL-FORGE-002",
        "SKILL-GATE-001",
        "SKILL-ROLLBACK-001",
        "SKILL-AUDIT-001",
        "GATEWAY-SKILL-AUDIT-001",
        "SKILL-EXECUTION-001",
        "GATEWAY-SKILL-EXECUTION-001",
        "SELF-LESSON-001",
        "SELF-LESSON-AUDIT-001",
        "GATEWAY-SELF-LESSON-001",
        "SELF-LESSON-STORE-001",
        "GATEWAY-SELF-LESSON-PROMOTE-001",
        "ROBOT-SAFE-001",
        "BENCH-PLAN-001",
    }


def test_benchmark_writer_creates_sanitized_json(tmp_path: Path):
    result = run_all()
    output_path = write_run(result, tmp_path)

    contents = output_path.read_text(encoding="utf-8")
    assert "CORTEX_FAKE_TOKEN_abc12345SECRET" not in contents
    assert "Ignore previous instructions" not in contents
    assert "prompt_injection" in contents
    assert output_path.suffix == ".json"
