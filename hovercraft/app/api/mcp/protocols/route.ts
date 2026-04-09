import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * [GET] 회선, 유닛, 글로벌 프로토콜 정보를 조회하는 통합 API
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const type = searchParams.get('type');
  const name = searchParams.get('name');
  
  const rootDir = path.resolve(process.cwd(), '../');
  const statePath = path.join(rootDir, 'data/state.json');

  const getI18nText = (data: any, lang: string) => {
    if (!data) return "";
    if (typeof data === "string") return data;
    if (Array.isArray(data)) return data.map(item => getI18nText(item, lang));
    if (typeof data === "object") {
      return data[lang] || data["en"] || Object.values(data)[0] || "";
    }
    return String(data);
  };

  try {
    const rawState = fs.existsSync(statePath) ? JSON.parse(fs.readFileSync(statePath, 'utf-8')) : {};
    const currentLang = rawState.lang || "ko";

    switch (type) {
      case 'units_list':
        const unitsDir = path.join(rootDir, 'mcp_operator/registry/units');
        if (fs.existsSync(unitsDir)) {
          const units = fs.readdirSync(unitsDir).filter(f => fs.statSync(path.join(unitsDir, f)).isDirectory() && f !== '__pycache__');
          return NextResponse.json({ units });
        }
        return NextResponse.json({ units: [] });

      case 'unit':
        const unitPath = path.join(rootDir, `mcp_operator/registry/units/${name}/protocols.json`);
        if (fs.existsSync(unitPath)) {
          const unitData = JSON.parse(fs.readFileSync(unitPath, 'utf-8'));
          return NextResponse.json({
            OVERVIEW: getI18nText(unitData.OVERVIEW, currentLang),
            RULES: getI18nText(unitData.RULES, currentLang)
          });
        }
        return NextResponse.json({ error: 'Unit protocol not found', path: unitPath }, { status: 404 });

      case 'circuit_full':
        const overviewPath = path.join(rootDir, `mcp_operator/registry/circuits/registry/${name}/overview.json`);
        const protocolsPath = path.join(rootDir, `mcp_operator/registry/circuits/registry/${name}/protocols.json`);
        
        const data: any = {};
        if (fs.existsSync(overviewPath)) {
          const overview = JSON.parse(fs.readFileSync(overviewPath, 'utf-8'));
          data.overview = { ...overview, description: getI18nText(overview.description, currentLang) };
          data.units = (overview.units || []).map((u: any) => {
            const uName = typeof u === 'string' ? u : u.name;
            const uProtoPath = path.join(rootDir, 'mcp_operator/registry/units', uName, 'protocols.json');
            const uProto = fs.existsSync(uProtoPath) ? JSON.parse(fs.readFileSync(uProtoPath, 'utf-8')) : {};
            return { name: uName, mission: getI18nText(uProto.OVERVIEW, currentLang), rules: getI18nText(uProto.RULES, currentLang) };
          });
        }
        
        if (fs.existsSync(protocolsPath)) {
          const circuitProtocols = JSON.parse(fs.readFileSync(protocolsPath, 'utf-8'));
          data.protocols = getI18nText(circuitProtocols.RULES || circuitProtocols, currentLang);
        }

        const globalProtocolsPath = path.join(rootDir, 'mcp_operator/engine/protocols.json');
        if (fs.existsSync(globalProtocolsPath)) {
          const globalFull = JSON.parse(fs.readFileSync(globalProtocolsPath, 'utf-8'));
          const langData = globalFull.LANGUAGES?.[currentLang] || globalFull.LANGUAGES?.["en"] || {};
          data.global_protocols = { title: currentLang === "ko" ? "글로벌 운영 규약" : "Global Operational Protocol", rules: langData.RULES || [] };
        }
        
        const missionPath = path.join(rootDir, 'data/mission.json');
        if (fs.existsSync(missionPath)) {
          const missionRaw = JSON.parse(fs.readFileSync(missionPath, 'utf-8'));
          data.mission = { objective: getI18nText(missionRaw.objective, currentLang), criteria: getI18nText(missionRaw.criteria, currentLang), status: missionRaw.status };
        }
        return NextResponse.json(data);

      default:
        return NextResponse.json({ error: 'Invalid type' }, { status: 400 });
    }
  } catch (error) {
    return NextResponse.json({ error: 'Failed to read resource' }, { status: 500 });
  }
}
