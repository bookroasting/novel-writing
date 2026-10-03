#!/usr/bin/env bash
# 범용성 회귀 시험. 설명은 selftest.py 머리말.
# Playwright가 깔려 있으면 e북 브라우저 시험(T38)도 돈다. 없으면 그 시험만 건너뛴다.
# 스킬 저장소(루트에 SKILL.md)에서는 tools/tests/fixtures/kimjang-day 기준 작품을 프로젝트로 쓴다.
set -e
cd "$(dirname "$0")/../.."
: "${PLAYWRIGHT_BROWSERS_PATH:=$HOME/Library/Caches/ms-playwright}"
export PLAYWRIGHT_BROWSERS_PATH
if [ -f SKILL.md ]; then export NOVEL_ROOT="$PWD/tools/tests/fixtures/kimjang-day"; fi
python3 tools/tests/selftest.py
