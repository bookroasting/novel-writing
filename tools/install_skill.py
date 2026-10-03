"""novel-writing 스킬 설치.

사용 (프로젝트 폴더에서):
  python3 tools/install_skill.py --target claude-project   # 이 프로젝트의 .claude/skills, .claude/agents
  python3 tools/install_skill.py --target claude-project --project ~/novels/my-book   # 다른 작품 폴더에
  python3 tools/install_skill.py --target claude-user      # ~/.claude/skills, ~/.claude/agents (모든 프로젝트)
  python3 tools/install_skill.py --target codex            # ~/.codex/skills (Codex CLI·앱)
  python3 tools/install_skill.py --target zip              # dist/novel-writing.zip (Claude 앱 등 업로드용)
  여러 개를 쉼표로: --target claude-project,codex

스킬 원본은 프로젝트의 novel-writing/ 폴더 하나다. 설치는 그 폴더를 복사한다.
Claude Code 대상이면 서브 에이전트(novel-writing/agents/*.md)를 agents 폴더에도 복사하고,
파일 안의 {{SKILL_DIR}}을 설치된 스킬 폴더의 절대 경로로 바꾼다.
Codex·zip에는 서브 에이전트 등록 형식이 없으므로 스킬 폴더만 넣는다. 그 환경에서는 SKILL.md가 단계 문서를 직접 읽게 안내한다.
"""
import argparse
import shutil
import sys
import zipfile
from pathlib import Path

NAME = "novel-writing"
REPO = Path(__file__).resolve().parents[1]
# 스킬 원본 위치: 작품 프로젝트 안이면 novel-writing/, 스킬 저장소(루트에 SKILL.md)면 저장소 루트
SRC = REPO / NAME if (REPO / NAME / "SKILL.md").exists() else REPO
SKILL_ITEMS = ("SKILL.md", "agents", "references", "scripts", "templates")   # 설치에 들어가는 것
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def copy_skill(dest_skills):
    dest = Path(dest_skills).expanduser() / NAME
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in SKILL_ITEMS:   # 저장소의 examples·tools 같은 개발용 폴더는 넣지 않는다
        s = SRC / item
        if s.is_dir():
            shutil.copytree(s, dest / item, ignore=IGNORE)
        elif s.exists():
            shutil.copy2(s, dest / item)
    return dest


def fill_placeholders(skill_copy, value):
    """설치본 스킬 폴더 안의 agents/*.md에 남은 {{SKILL_DIR}}을 채운다 (Codex·zip은 서브 에이전트를 등록하지 않지만 읽을 수는 있게)."""
    for a in (Path(skill_copy) / "agents").glob("*.md"):
        a.write_text(a.read_text(encoding="utf-8").replace("{{SKILL_DIR}}", value), encoding="utf-8")


def copy_agents(dest_agents, skill_dir):
    dest = Path(dest_agents).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    out = []
    for a in sorted((SRC / "agents").glob("*.md")):
        t = a.read_text(encoding="utf-8").replace("{{SKILL_DIR}}", str(skill_dir))
        (dest / a.name).write_text(t, encoding="utf-8")
        out.append(dest / a.name)
    return out


def install(target, project=None):
    if target == "claude-project":
        proj = Path(project).expanduser().resolve() if project else REPO
        d = copy_skill(proj / ".claude" / "skills")
        rel_dir = f".claude/skills/{NAME}"            # 프로젝트 안 상대 경로: 폴더를 옮겨도 끊기지 않는다
        fill_placeholders(d, rel_dir)
        ags = copy_agents(proj / ".claude" / "agents", rel_dir)
        return f"Claude Code(프로젝트 {proj}): {d} + 서브 에이전트 {len(ags)}개 → {proj / '.claude' / 'agents'}"
    if target == "claude-user":
        d = copy_skill("~/.claude/skills")
        fill_placeholders(d, str(d))
        ags = copy_agents("~/.claude/agents", d)
        return f"Claude Code(사용자 전체): {d} + 서브 에이전트 {len(ags)}개 → ~/.claude/agents"
    if target == "codex":
        d = copy_skill("~/.codex/skills")
        fill_placeholders(d, str(d))
        return f"Codex: {d} (서브 에이전트 없이 SKILL.md가 단계 문서를 직접 읽는다)"
    if target == "zip":
        out = REPO / "dist" / f"{NAME}.zip"
        out.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(SRC.rglob("*")):
                rel = f.relative_to(SRC)
                if rel.parts[0] not in SKILL_ITEMS:
                    continue
                if f.is_file() and "__pycache__" not in f.parts and f.name != ".DS_Store":
                    arc = Path(NAME) / f.relative_to(SRC)
                    if f.parent.name == "agents" and f.suffix == ".md":
                        z.writestr(str(arc), f.read_text(encoding="utf-8").replace("{{SKILL_DIR}}", f"<스킬 폴더({NAME})>"))
                    else:
                        z.write(f, arc)
        return f"zip: {out}"
    raise SystemExit(f"알 수 없는 대상: {target} (가능: claude-project, claude-user, codex, zip)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="claude-project, claude-user, codex, zip (쉼표로 여러 개)")
    ap.add_argument("--project", help="claude-project 대상의 작품 폴더 (기본: 이 저장소)")
    a = ap.parse_args()
    if not (SRC / "SKILL.md").exists():
        raise SystemExit(f"스킬 원본이 없다: {SRC}")
    for t in a.target.split(","):
        print("OK", install(t.strip(), a.project))


if __name__ == "__main__":
    sys.exit(main())
