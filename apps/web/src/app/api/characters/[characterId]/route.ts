import { NextRequest, NextResponse } from "next/server";

import { deleteCharacter, updateCharacter } from "@/lib/api";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ characterId: string }>;
};

export async function PUT(request: NextRequest, context: RouteContext) {
  let payload: Record<string, unknown>;

  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json(
      { message: "Invalid request body." },
      { status: 400 }
    );
  }

  const { characterId } = await context.params;
  const updated = await updateCharacter(characterId, payload as never);

  if (updated === null) {
    return NextResponse.json(
      { message: "Update character failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(updated);
}

export async function DELETE(_: NextRequest, context: RouteContext) {
  const { characterId } = await context.params;
  const deleted = await deleteCharacter(characterId);

  if (deleted === null) {
    return NextResponse.json(
      { message: "Delete character failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(deleted);
}
