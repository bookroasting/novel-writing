# AGENTS.md

이 저장소는 `novel-writing` 스킬 자체다. Codex 같은 에이전트는 이 파일을 먼저 읽는다.

1. 작품을 쓰려면 `SKILL.md`를 읽고 그 절차를 따른다. 작품 파일은 이 저장소가 아니라 작품 폴더에 둔다.
2. 서브 에이전트를 쓸 수 없는 환경이면 단계마다 `references/stage-<단계>.md`를 직접 읽고 수행한다.
3. 스크립트는 `python3 scripts/<이름>.py --root <작품 폴더>`로 실행한다.
4. 스킬을 고친 뒤에는 `bash tools/tests/selftest.sh`가 모두 통과해야 한다.

Codex에 스킬로 설치하려면 `python3 tools/install_skill.py --target codex`.
