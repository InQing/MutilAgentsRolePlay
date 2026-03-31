import { NextRequest, NextResponse } from "next/server";

import { createCharacter, fetchCharacters } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function GET() {
  const characters = await fetchCharacters();

  if (characters === null) {
    return NextResponse.json(
      { message: "Character API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(characters);
}

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

  const created = await createCharacter(payload as never);

  if (created === null) {
    return NextResponse.json(
      { message: "Create character failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(created);
}
