"""작가 산출물 잠금 줄을 원장에 남긴다 (references/ledger.md "잠금").

사용: python3 <스킬>/scripts/lock_run.py --run <run> [--root <프로젝트 폴더>]
new_run.py는 run을 열 때, publish 단계는 출판을 마칠 때 이 줄을 남긴다. 블록·스냅샷을 승인받아 고친 뒤에도 다시 남긴다.
직전 잠금 이후 승인 없는 변경이 있으면 쓰지 않고 멈춘다.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from booktoc import require_run, ROOT, lock_line, lock_violations  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args()
    require_run(a.run, a.root)
    led = Path(a.root) / "02_draft" / a.run / "00_RUN_STATUS.md"
    if not led.exists():
        raise SystemExit(f"원장이 없다: {led}")
    lines = led.read_text(encoding="utf-8").split("\n")
    last = max([i for i, ln in enumerate(lines) if ln.startswith("lock:")], default=-1)
    open_pa = [i for i, ln in enumerate(lines) if i > last and re.match(r"^gate:\s*post-audit\s*→\s*approved\b", ln)]
    if open_pa and not any(re.match(r"^stage:\s*post-audit-fix (done .*\(republish\.py, owner |abandoned)", ln) for ln in lines[open_pa[-1] + 1:]):
        raise SystemExit(f"잠그지 않았다. 원장 {open_pa[-1] + 1}줄의 출판 뒤 수정이 진행 중이다. 그 수정은 republish.py가 마치며 잠근다")
    meta = Path(a.root) / "03_output" / a.run / "metadata.md"
    if meta.exists() and not re.search(r"분량:\s*[\d,]+자", meta.read_text(encoding="utf-8")):
        raise SystemExit("잠그지 않았다. metadata.md에 '분량: <글자 수>자' 줄이 없거나 형식이 다르다(stage-publish.md 2단계 형식)")
    bad = lock_violations(a.run, a.root)
    if bad:   # 다시 잠그는 것으로 승인 없는 변경을 덮지 못한다
        raise SystemExit("잠그지 않았다. 직전 잠금 이후 승인 없는 변경이 있다:\n  " + "\n  ".join(bad))
    line = lock_line(a.run, a.root)
    led.write_text(led.read_text(encoding="utf-8").rstrip("\n") + "\n" + line + "\n", encoding="utf-8")
    print("OK", line)


if __name__ == "__main__":
    main()
