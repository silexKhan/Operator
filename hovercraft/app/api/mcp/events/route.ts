import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * [SSE] 엔진의 상태 변화를 감지하여 '풀 패키지 데이터'를 브라우저로 실시간 전송
 */
export async function GET(req: NextRequest) {
  const encoder = new TextEncoder();
  const rootDir = path.resolve(process.cwd(), '../');
  const statePath = path.join(rootDir, 'data/state.json');
  const logPath = path.join(rootDir, 'logs/mcp_live.log');
  const circuitsDir = path.join(rootDir, 'mcp_operator/registry/circuits/registry');

  // [Helper] 다국어 텍스트 추출 로직 (utils.py의 get_i18n_text와 동일)
  const getI18nText = (data: any, lang: string) => {
    if (!data) return "";
    if (typeof data === "string") return data;
    if (Array.isArray(data)) return data.map(item => getI18nText(item, lang));
    if (typeof data === "object") {
      return data[lang] || data["en"] || Object.values(data)[0] || "";
    }
    return String(data);
  };

  // [Helper] 엔진의 부실한 state.json을 풍부한 데이터로 변환
  const getFullState = () => {
    try {
      if (!fs.existsSync(statePath)) return { active_circuit: 'None', circuits: [] };
      
      const rawState = JSON.parse(fs.readFileSync(statePath, 'utf-8'));
      const activeCircuit = rawState.active_circuit;
      const currentLang = rawState.lang || "ko";
      
      // 1. 등록된 모든 회선 목록 가져오기
      const circuits = fs.existsSync(circuitsDir) 
        ? fs.readdirSync(circuitsDir).filter(f => fs.statSync(path.join(circuitsDir, f)).isDirectory())
        : [];

      // 2. 활성 회선의 상세 정보 조립 (Overview + Protocols + Units)
      let details = null;
      if (activeCircuit && activeCircuit !== 'None') {
        const circuitPath = path.join(circuitsDir, activeCircuit);
        const overviewPath = path.join(circuitPath, 'overview.json');
        const protocolsPath = path.join(circuitPath, 'protocols.json');
        
        const overview = fs.existsSync(overviewPath) ? JSON.parse(fs.readFileSync(overviewPath, 'utf-8')) : {};
        const protocols = fs.existsSync(protocolsPath) ? JSON.parse(fs.readFileSync(protocolsPath, 'utf-8')) : { RULES: [] };

        // 유닛 정보 상세화
        const enrichedUnits = (overview.units || []).map((u: any) => {
          const unitName = typeof u === 'string' ? u : u.name;
          const unitProtoPath = path.join(rootDir, 'mcp_operator/registry/units', unitName, 'protocols.json');
          const unitProto = fs.existsSync(unitProtoPath) ? JSON.parse(fs.readFileSync(unitProtoPath, 'utf-8')) : {};
          return {
            name: unitName,
            mission: getI18nText(unitProto.OVERVIEW, currentLang) || "No mission defined",
            rules: getI18nText(unitProto.RULES, currentLang) || []
          };
        });

        details = {
          name: activeCircuit,
          description: getI18nText(overview.description, currentLang) || "No description provided.",
          mission: {
            objective: getI18nText(overview.mission?.objective, currentLang),
            criteria: getI18nText(overview.mission?.criteria, currentLang) || []
          },
          protocols: getI18nText(protocols.RULES, currentLang) || [],
          units: enrichedUnits
        };
      }

      return {
        active_circuit: activeCircuit,
        lang: rawState.lang || "ko",
        registered_circuits: circuits,
        active_circuit_details: details
      };
    } catch (e) {
      console.error("[SSE] State Enrichment Error:", e);
      return { error: "Enrichment failed" };
    }
  };

  const stream = new ReadableStream({
    async start(controller) {
      const sendEvent = (type: string, data: any) => {
        try {
          const eventString = `event: ${type}\ndata: ${JSON.stringify(data)}\n\n`;
          controller.enqueue(encoder.encode(eventString));
        } catch (e) {}
      };

      // 1. 초기 데이터 즉시 전송
      sendEvent('state', getFullState());

      // 2. 파일 감시 (이벤트 발생 시 풀 데이터 재전송)
      const stateWatcher = fs.watch(statePath, (eventType) => {
        if (eventType === 'change') {
          sendEvent('state', getFullState());
        }
      });

      const logWatcher = fs.watch(logPath, (eventType) => {
        if (eventType === 'change') {
          try {
            const logData = fs.readFileSync(logPath, 'utf-8');
            const lines = logData.trim().split('\n').filter(line => line.length > 0);
            if (lines.length > 0) {
              const lastLog = JSON.parse(lines[lines.length - 1]);
              sendEvent('log', lastLog);
            }
          } catch (e) {}
        }
      });

      req.signal.addEventListener('abort', () => {
        stateWatcher.close();
        logWatcher.close();
        try { controller.close(); } catch (e) {}
      });
    },
  });

  return new NextResponse(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}
