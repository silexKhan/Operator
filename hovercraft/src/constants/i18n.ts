export const I18N = {
  Overview: { ko: "개요", en: "Overview" },
  Protocols: { ko: "규약", en: "Protocols" },
  Circuits: { ko: "회선", en: "Circuits" },
  Units: { ko: "유닛", en: "Units" },
  Monitor: { ko: "모니터링", en: "Monitor" },
  Settings: { ko: "시스템 설정", en: "System Settings" },
  PollingRate: { ko: "폴링 주기", en: "Polling Rate" },
  LogLimit: { ko: "로그 표시 제한", en: "Log Limit" },
  ResetSession: { ko: "세션 초기화", en: "Reset Session" },
  Apply: { ko: "적용", en: "Apply" },
  Cancel: { ko: "취소", en: "Cancel" },
  AwaitingSpecs: { ko: "상세 미션 명세를 기다리는 중...", en: "Awaiting detailed mission specifications..." },
  PrimaryObjective: { ko: "주요 목표", en: "Primary Objective" },
  SuccessCriteria: { ko: "달성 조건", en: "Success Criteria" },
  ArchitectSummary: { ko: "설계 요약", en: "Architect's Summary" },
  TechDependencies: { ko: "기술 의존성", en: "Technology Dependencies" }
};

export type I18NKey = keyof typeof I18N;
