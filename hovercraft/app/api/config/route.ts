import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const CONFIG_PATH = path.join(process.cwd(), 'ship_config.json');

export async function GET() {
  try {
    const data = await fs.readFile(CONFIG_PATH, 'utf-8');
    return NextResponse.json(JSON.parse(data));
  } catch (error) {
    return NextResponse.json({ error: 'Config not found' }, { status: 404 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { shipName, captainName } = body;
    
    if (!shipName || !captainName) {
      return NextResponse.json({ error: 'Missing parameters' }, { status: 400 });
    }

    const config = { shipName, captainName, initializedAt: new Date().toISOString() };
    await fs.writeFile(CONFIG_PATH, JSON.stringify(config, null, 2));
    
    return NextResponse.json({ success: true, config });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to save config' }, { status: 500 });
  }
}
