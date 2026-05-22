#!/usr/bin/env node
/**
 * qa-scout v0.2.9 — input-manifest.yaml 마이그레이션 유틸 (v0.2.7/v0.2.8 → v0.2.9)
 *
 * SDD: ../../docs/qa-scout/spec.md §5-7 마이그레이션 4단계
 *      + ../../docs/qa-scout/spec.md Playwright 검증 슬롯.
 *
 * 사용법:
 *   node plugins/qa-scout/scripts/migrate-to-v029.mjs <input-manifest.yaml> <mode>
 *
 * mode:
 *   dry-run — 변경 preview 출력만, 파일 미수정 (기본 검토 시 권장)
 *   write   — backup 생성 + schema_version 갱신 + 누락 슬롯 5종 append (실제 파일 수정)
 *
 * 마이그레이션 룰:
 *   - 대상 manifest의 schema_version이 "0.2.9"면 no-op (이미 마이그레이션됨)
 *   - schema_version "0.2.7" 또는 "0.2.8" → "0.2.9" 갱신
 *   - 신규 슬롯 5종(final_artifacts / execution_gate / playwright_verification / readme_discovery / two_doc_cross_check)
 *     중 manifest top-level에 이미 존재하는 슬롯은 보존하고, 누락된 슬롯만 EOF에 append
 *   - 기존 downstream_enrichment / developer_deep_scope / deep_screen_targets / received_artifacts
 *     등 v0.2.7/v0.2.8 구조는 모두 보존 (텍스트 라인 그대로)
 *   - write 모드는 backup 파일 생성 후 원본 덮어쓰기
 *     backup 경로: <manifest>.v0.2.<X>-backup-<YYYYMMDDTHHMMSSZ>
 *
 * 신규 슬롯 기본값 (SDD §5-9·§5-10·§5-11 + 2026-05-22 UX 강화):
 *   final_artifacts.feature_spec        = "feature-spec.md"
 *   final_artifacts.ui_menu_mindmap     = "ui-menu-mindmap.md"
 *   execution_gate.decision             = "context-insufficient"
 *   execution_gate.reviewer_status      = "CONTEXT-INSUFFICIENT"
 *   playwright_verification.status      = "NOT_RUN"
 *   readme_discovery.scanned            = false
 *   two_doc_cross_check.result          = "NOT_RUN"
 *   나머지 필드는 null / [] / "" 의 안전한 빈 값
 *
 * 종료 코드:
 *   0 — 정상 (마이그레이션 완료, no-op 포함)
 *   1 — 마이그레이션 차단 (지원 외 schema_version 등)
 *   2 — 인자 오류 또는 파일 접근 실패
 *
 * 의존성: Node 표준 fs·path만 사용 (npm install 불필요).
 *         YAML 파서 미사용 — 텍스트 라인 기반 패치로 기존 주석·들여쓰기·구조 보존.
 */

import { readFileSync, writeFileSync, statSync, copyFileSync } from 'fs';
import { resolve } from 'path';

const SUPPORTED_FROM = ['0.2.7', '0.2.8'];
const TARGET_VERSION = '0.2.9';
const NEW_SLOTS = [
  'final_artifacts',
  'execution_gate',
  'playwright_verification',
  'readme_discovery',
  'two_doc_cross_check'
];

const [, , manifestArg, mode] = process.argv;

if (!manifestArg || !mode) {
  console.error('Usage: node migrate-to-v029.mjs <input-manifest.yaml> <dry-run|write>');
  console.error('');
  console.error('mode 설명:');
  console.error('  dry-run — 변경 preview 출력만, 파일 미수정');
  console.error('  write   — backup 생성 + 파일 갱신');
  process.exit(2);
}

if (mode !== 'dry-run' && mode !== 'write') {
  console.error(`Invalid mode: ${mode}. Use 'dry-run' or 'write'.`);
  process.exit(2);
}

let manifestPath;
try {
  manifestPath = resolve(manifestArg);
  const st = statSync(manifestPath);
  if (!st.isFile()) {
    console.error(`ERROR: ${manifestArg} is not a file`);
    process.exit(2);
  }
} catch (err) {
  console.error(`ERROR: manifest file access failed — ${err.message}`);
  process.exit(2);
}

let original;
try {
  original = readFileSync(manifestPath, 'utf8');
} catch (err) {
  console.error(`ERROR: read failed — ${err.message}`);
  process.exit(2);
}

// schema_version 감지 — 최상위 라인 우선 (들여쓰기 없음)
const SCHEMA_RE = /^schema_version:\s*"?([0-9]+\.[0-9]+(?:\.[0-9]+)?)"?\s*(#.*)?$/m;
const schemaMatch = original.match(SCHEMA_RE);
if (!schemaMatch) {
  console.error('ERROR: schema_version line not found at top level');
  process.exit(1);
}
const currentVersion = schemaMatch[1];

// 마이그레이션 대상 판정
if (currentVersion === TARGET_VERSION) {
  const report = {
    mode,
    manifest: manifestPath.replace(/\\/g, '/'),
    current_version: currentVersion,
    target_version: TARGET_VERSION,
    action: 'no-op',
    reason: 'manifest is already at v0.2.9 — no migration needed',
    schema_version_change: null,
    slots_already_present: detectExistingSlots(original),
    slots_to_append: [],
    backup_path: null
  };
  console.log(JSON.stringify(report, null, 2));
  process.exit(0);
}

if (!SUPPORTED_FROM.includes(currentVersion)) {
  console.error(
    `ERROR: unsupported schema_version "${currentVersion}". ` +
    `Supported source versions: ${SUPPORTED_FROM.join(', ')} → ${TARGET_VERSION}`
  );
  process.exit(1);
}

// 기존 슬롯 감지 — 들여쓰기 없는 top-level key
function detectExistingSlots(text) {
  const present = [];
  for (const slot of NEW_SLOTS) {
    const re = new RegExp(`^${slot}:\\s*(#.*)?$`, 'm');
    if (re.test(text)) present.push(slot);
  }
  return present;
}

const existing = detectExistingSlots(original);
const missing = NEW_SLOTS.filter(s => !existing.includes(s));

// schema_version 라인 갱신 (write 모드에서만 실제 적용)
const updatedSchemaLine = `schema_version: "${TARGET_VERSION}"`;
let patched = original.replace(SCHEMA_RE, (match, _ver, comment) => {
  const tail = comment ? ` ${comment}` : '';
  return `${updatedSchemaLine}${tail}`;
});

// 누락 슬롯 본문 (SDD §5-1·§5-9·§5-10·§5-11 SoT 정합)
const SLOT_BODIES = {
  final_artifacts: `# -------------------------------------------------------
# v0.2.9 신규 슬롯 — final_artifacts (SDD §5-1·§4 #4 — migrated by migrate-to-v029.mjs)
# -------------------------------------------------------
# 최종 읽기 산출물 2종 경로 + hash. Sheets 이행 대상은 feature_spec만.
final_artifacts:
  feature_spec: "feature-spec.md"
  ui_menu_mindmap: "ui-menu-mindmap.md"
  readable_outputs_count: 2
  sheets_target: "feature_spec only"
  hash:
    feature_spec_sha256: null
    ui_menu_mindmap_sha256: null
    hashed_at: null
`,
  execution_gate: `# -------------------------------------------------------
# v0.2.9 신규 슬롯 — execution_gate (SDD §5-10 — migrated by migrate-to-v029.mjs)
# -------------------------------------------------------
# 마이그레이션 시점 기본값은 context-insufficient — 단계 1c execution gate 재실행 필요.
# decision 4종 × reviewer_status 4종 1:1 매핑 (SDD §5-10-2).
execution_gate:
  asked_at: null
  environment_class: "unknown"
  has_prod_or_real_data: "unknown"
  forbidden_actions: []
  allowed_state_change_scope: []
  proceed_approved: null
  decision: "context-insufficient"
  reviewer_status: "CONTEXT-INSUFFICIENT"
  confirmed_by: null
  confirmed_at: null
  notes: "migrated from v0.2.7/v0.2.8 by migrate-to-v029.mjs — rerun 단계 1c to fill"
`,
  playwright_verification: `# -------------------------------------------------------
# v0.2.9 신규 슬롯 — playwright_verification (2026-05-22 UX 강화 — migrated by migrate-to-v029.mjs)
# -------------------------------------------------------
# 마이그레이션 시점 기본값은 NOT_RUN — 단계 9e 라이브 검증 재실행 필요.
# URL·테스트 계정·execution_gate가 있으면 기본 실행 시도하고, 화면↔문서 gap을 양방향 기록한다.
playwright_verification:
  status: "NOT_RUN"
  tested_url: null
  login_account_role: null
  screens_visited: []
  evidence_files: []
  spec_missing_count: null
  screen_missing_count: null
  mismatch_count: null
  forbidden_actions_observed: []
  skip_reason: "migrated from v0.2.7/v0.2.8 by migrate-to-v029.mjs — rerun 단계 9e to fill"
  blocked_reason: null
  failed_reason: null
  notes:
    - "Capture SPEC-MISSING / SCREEN-MISSING / DOC-SCREEN-MISMATCH during 단계 9e."
`,
  readme_discovery: `# -------------------------------------------------------
# v0.2.9 신규 슬롯 — readme_discovery (SDD §5-11 — migrated by migrate-to-v029.mjs)
# -------------------------------------------------------
# 마이그레이션 시점 기본값은 scanned=false — 단계 4a README discovery 재실행 필요.
# README는 요구사항 SoT 아닌 탐색 힌트. agent_guidance_files[]는 top-level 배열.
readme_discovery:
  scanned: false
  scanned_at: null
  scan_roots: []
  readme_files: []
  referenced_paths: []
  developer_confirmed_paths: []
  rejected_paths: []
  agent_guidance_files: []
  extracted_project_hints:
    feature_modules: []
    environment_hints:
      local_url: null
      test_accounts_hint: null
      run_commands: []
    api_docs_links: []
  notes: "migrated from v0.2.7/v0.2.8 by migrate-to-v029.mjs — rerun 단계 4a to fill"
`,
  two_doc_cross_check: `# -------------------------------------------------------
# v0.2.9 신규 슬롯 — two_doc_cross_check (SDD §5-9 — migrated by migrate-to-v029.mjs)
# -------------------------------------------------------
# 마이그레이션 시점 기본값은 NOT_RUN — 단계 9d.5 cross-check 게이트 재실행 필요.
# 행 단위 결과는 feature-spec.md §8(방향 A) + ui-menu-mindmap.md §6(방향 B) — 별도 제3 문서 금지.
two_doc_cross_check:
  executed_at: null
  result: "NOT_RUN"
  fr_mapping_rate: null
  leaf_mapping_rate: null
  risky_action_dual_marked: false
  unmapped_fr: []
  unmapped_leaf: []
  risky_action_one_sided: []
  notes:
    - "migrated from v0.2.7/v0.2.8 by migrate-to-v029.mjs — rerun 단계 9d.5 cross-check to fill"
  artifacts:
    feature_spec_section: "feature-spec.md#§8-마인드맵-대조-결과"
    ui_menu_mindmap_section: "ui-menu-mindmap.md#§6-기능정의서-대조-결과"
`
};

// append 본문 구성
const HEADER = `# -------------------------------------------------------
# v0.2.9 마이그레이션 append 영역 (by plugins/qa-scout/scripts/migrate-to-v029.mjs)
# 원본 manifest schema_version ${currentVersion} → ${TARGET_VERSION}로 갱신됨.
# 누락된 v0.2.9 신규 슬롯 ${missing.length}개 추가: ${missing.join(', ') || '(none)'}.
# 기본값은 안전한 빈 상태이며 단계 1c/4a/9e/9d.5 재실행으로 채워야 한다.
# -------------------------------------------------------
`;

if (missing.length > 0) {
  // 줄바꿈 정합 — 원본 EOF에 newline 보장
  if (!patched.endsWith('\n')) patched += '\n';
  patched += '\n' + HEADER;
  for (const slot of missing) {
    patched += '\n' + SLOT_BODIES[slot];
  }
}

// 결과 보고
const report = {
  mode,
  manifest: manifestPath.replace(/\\/g, '/'),
  current_version: currentVersion,
  target_version: TARGET_VERSION,
  action: 'migrate',
  schema_version_change: `${currentVersion} → ${TARGET_VERSION}`,
  slots_already_present: existing,
  slots_to_append: missing,
  appended_lines: missing.length === 0 ? 0 : (patched.length - original.length),
  backup_path: null
};

if (mode === 'dry-run') {
  report.dry_run_preview = {
    original_bytes: original.length,
    patched_bytes: patched.length,
    diff_bytes: patched.length - original.length,
    schema_version_line_updated: true,
    head_of_appended_block: missing.length > 0
      ? patched.slice(original.length, Math.min(patched.length, original.length + 400)).replace(/\r/g, '')
      : '(no new slots to append)'
  };
  console.log(JSON.stringify(report, null, 2));
  process.exit(0);
}

// write 모드 — backup 생성 후 원본 덮어쓰기
const ts = new Date().toISOString().replace(/[-:]/g, '').replace(/\..*$/, '');
const backupPath = `${manifestPath}.v${currentVersion}-backup-${ts}`;
try {
  copyFileSync(manifestPath, backupPath);
} catch (err) {
  console.error(`ERROR: backup write failed — ${err.message}`);
  process.exit(2);
}

try {
  writeFileSync(manifestPath, patched, 'utf8');
} catch (err) {
  console.error(`ERROR: manifest write failed — ${err.message}`);
  console.error(`backup retained at: ${backupPath}`);
  process.exit(2);
}

report.backup_path = backupPath.replace(/\\/g, '/');
console.log(JSON.stringify(report, null, 2));
process.exit(0);
