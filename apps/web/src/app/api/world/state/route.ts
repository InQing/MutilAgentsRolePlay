import { NextResponse } from "next/server";

import { fetchWorldState } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function GET() {
  const worldState = await fetchWorldState();

  if (worldState === null) {
    return NextResponse.json(
      { message: "World API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(worldState);
}
