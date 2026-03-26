import { NextRequest, NextResponse } from "next/server";

import { advanceWorld } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  let seconds = 900;

  try {
    const body = (await request.json()) as { seconds?: number };
    if (typeof body.seconds === "number" && Number.isFinite(body.seconds) && body.seconds > 0) {
      seconds = Math.floor(body.seconds);
    }
  } catch {
    seconds = 900;
  }

  const worldState = await advanceWorld(seconds);

  if (worldState === null) {
    return NextResponse.json(
      { message: "World advance failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(worldState);
}
