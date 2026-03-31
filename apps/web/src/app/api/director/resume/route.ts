import { NextResponse } from "next/server";

import { resumeDirectorWorld } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function POST() {
  const panel = await resumeDirectorWorld();

  if (panel === null) {
    return NextResponse.json(
      { message: "Resume world failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(panel);
}
