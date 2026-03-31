import { NextResponse } from "next/server";

import { pauseDirectorWorld } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function POST() {
  const panel = await pauseDirectorWorld();

  if (panel === null) {
    return NextResponse.json(
      { message: "Pause world failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(panel);
}
