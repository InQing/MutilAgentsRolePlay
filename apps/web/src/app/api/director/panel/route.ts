import { NextResponse } from "next/server";

import { fetchDirectorPanel } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function GET() {
  const panel = await fetchDirectorPanel();

  if (panel === null) {
    return NextResponse.json(
      { message: "Director panel API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(panel);
}
