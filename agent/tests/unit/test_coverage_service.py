import subprocess
from pathlib import Path

from app.models.enums import CoverageStatus
from app.services.coverage_service import analyze_coverage
from app.services.git_service import analyze_changes


def test_missing_when_no_test_dirs_exist(sut_repo: Path):
    changed = analyze_changes(sut_repo, base_ref="main")
    coverage = analyze_coverage(sut_repo, changed)

    assert coverage.unit == CoverageStatus.MISSING
    assert coverage.integration == CoverageStatus.MISSING
    assert coverage.e2e == CoverageStatus.NOT_REQUIRED  # no frontend files changed
    assert coverage.performance == CoverageStatus.NOT_REQUIRED  # no locustfile exists


def test_present_when_a_matching_unit_test_exists(sut_repo: Path):
    unit_dir = sut_repo / "backend" / "tests" / "unit"
    unit_dir.mkdir(parents=True)
    (unit_dir / "test_tasks.py").write_text("def test_tasks(): assert True\n", encoding="utf-8")

    changed = analyze_changes(sut_repo, base_ref="main")
    coverage = analyze_coverage(sut_repo, changed)

    assert coverage.unit == CoverageStatus.PRESENT
    assert any(Path(f).name == "test_tasks.py" for f in coverage.found_test_files)


def test_missing_when_test_dir_exists_but_nothing_matches(sut_repo: Path):
    unit_dir = sut_repo / "backend" / "tests" / "unit"
    unit_dir.mkdir(parents=True)
    (unit_dir / "test_unrelated.py").write_text("def test_unrelated(): assert True\n", encoding="utf-8")

    changed = analyze_changes(sut_repo, base_ref="main")
    coverage = analyze_coverage(sut_repo, changed)

    assert coverage.unit == CoverageStatus.MISSING


def test_e2e_not_required_becomes_missing_once_frontend_changes(sut_repo: Path):
    frontend_file = sut_repo / "frontend" / "pages" / "2_Tasks.py"
    frontend_file.parent.mkdir(parents=True)
    frontend_file.write_text("print('tasks page')\n", encoding="utf-8")
    # git diff only sees staged/tracked changes - stage it so it counts as "changed".
    subprocess.run(["git", "add", "-A"], cwd=sut_repo.parent, check=True, capture_output=True)

    changed = analyze_changes(sut_repo, base_ref="main")
    coverage = analyze_coverage(sut_repo, changed)

    assert coverage.e2e == CoverageStatus.MISSING


def test_performance_stays_not_required_without_a_locustfile(sut_repo: Path):
    perf_dir = sut_repo / "tests" / "performance"
    perf_dir.mkdir(parents=True)
    (perf_dir / "notes.txt").write_text("no locustfile here\n", encoding="utf-8")

    changed = analyze_changes(sut_repo, base_ref="main")
    coverage = analyze_coverage(sut_repo, changed)

    assert coverage.performance == CoverageStatus.NOT_REQUIRED


def test_performance_present_when_matching_locustfile_exists(sut_repo: Path):
    perf_dir = sut_repo / "tests" / "performance"
    perf_dir.mkdir(parents=True)
    (perf_dir / "locustfile_tasks.py").write_text("# tasks load test\n", encoding="utf-8")

    changed = analyze_changes(sut_repo, base_ref="main")
    coverage = analyze_coverage(sut_repo, changed)

    assert coverage.performance == CoverageStatus.PRESENT
