import { NextRequest, NextResponse } from "next/server";

import { updateDirectorWorldSpeed } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  let payload: Record<string, unknown>;
  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json(
      { message: "Invalid request body." },
      { status: 400 }
    );
  }

  const speedMultiplier = Number(payload.speed_multiplier);
  if (!Number.isFinite(speedMultiplier) || speedMultiplier <= 0) {
    return NextResponse.json(
      { message: "speed_multiplier must be a positive number." },
      { status: 400 }
    );
  }

  const panel = await updateDirectorWorldSpeed(speedMultiplier);

  if (panel === null) {
    return NextResponse.json(
      { message: "Update world speed failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(panel);
}
