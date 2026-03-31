import { NextRequest, NextResponse } from "next/server";

import { injectDirectorEvent } from "@/lib/api";

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

  const summary = String(payload.summary ?? "").trim();
  if (!summary) {
    return NextResponse.json(
      { message: "summary must not be empty." },
      { status: 400 }
    );
  }

  const panel = await injectDirectorEvent({
    summary,
    target_character_id:
      typeof payload.target_character_id === "string" &&
      payload.target_character_id.trim() !== ""
        ? payload.target_character_id.trim()
        : undefined,
    task_intent:
      typeof payload.task_intent === "string" && payload.task_intent.trim() !== ""
        ? payload.task_intent.trim()
        : undefined
  });

  if (panel === null) {
    return NextResponse.json(
      { message: "Inject director event failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(panel);
}
