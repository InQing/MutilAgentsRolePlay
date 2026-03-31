import type {
  CreateCharacterRequestContract,
  ConversationSummaryContract,
  CreateMessageRequestContract,
  CreateMomentRequestContract,
  DeleteCharacterResponseContract,
  DirectorPanelStateContract,
  EditableCharacterContract,
  InjectDirectorEventRequestContract,
  MessageRecordContract,
  UpdateCharacterRequestContract,
  WorldStateContract
} from "@mutilagentsroleplay/shared-contracts";

function getApiBaseUrl() {
  return (
    process.env.MARP_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://127.0.0.1:8000/api"
  );
}

async function fetchBackendJson<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      cache: "no-store",
      ...init
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function fetchDirectorPanel(): Promise<DirectorPanelStateContract | null> {
  return fetchBackendJson<DirectorPanelStateContract>("/director/panel");
}

export async function pauseDirectorWorld(): Promise<DirectorPanelStateContract | null> {
  return fetchBackendJson<DirectorPanelStateContract>("/director/pause", {
    method: "POST"
  });
}

export async function resumeDirectorWorld(): Promise<DirectorPanelStateContract | null> {
  return fetchBackendJson<DirectorPanelStateContract>("/director/resume", {
    method: "POST"
  });
}

export async function updateDirectorWorldSpeed(
  speedMultiplier: number
): Promise<DirectorPanelStateContract | null> {
  return fetchBackendJson<DirectorPanelStateContract>("/director/speed", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      speed_multiplier: speedMultiplier
    })
  });
}

export async function injectDirectorEvent(
  payload: InjectDirectorEventRequestContract
): Promise<DirectorPanelStateContract | null> {
  return fetchBackendJson<DirectorPanelStateContract>("/director/inject", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

export async function fetchWorldState(): Promise<WorldStateContract | null> {
  return fetchBackendJson<WorldStateContract>("/world/state");
}

export async function advanceWorld(seconds = 900): Promise<WorldStateContract | null> {
  return fetchBackendJson<WorldStateContract>(`/world/advance?seconds=${seconds}`, {
    method: "POST"
  });
}

export async function fetchCharacters(): Promise<EditableCharacterContract[] | null> {
  return fetchBackendJson<EditableCharacterContract[]>("/characters");
}

export async function updateCharacter(
  characterId: string,
  payload: UpdateCharacterRequestContract
): Promise<EditableCharacterContract | null> {
  return fetchBackendJson<EditableCharacterContract>(`/characters/${characterId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

export async function createCharacter(
  payload: CreateCharacterRequestContract
): Promise<EditableCharacterContract | null> {
  return fetchBackendJson<EditableCharacterContract>("/characters", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

export async function deleteCharacter(
  characterId: string
): Promise<DeleteCharacterResponseContract | null> {
  return fetchBackendJson<DeleteCharacterResponseContract>(`/characters/${characterId}`, {
    method: "DELETE"
  });
}

export async function fetchConversations(): Promise<ConversationSummaryContract[] | null> {
  return fetchBackendJson<ConversationSummaryContract[]>("/social/conversations");
}

export async function fetchConversationMessages(
  conversationId: string
): Promise<MessageRecordContract[] | null> {
  return fetchBackendJson<MessageRecordContract[]>(
    `/social/conversations/${conversationId}/messages`
  );
}

export async function createConversationMessage(
  conversationId: string,
  payload: CreateMessageRequestContract
): Promise<MessageRecordContract | null> {
  return fetchBackendJson<MessageRecordContract>(
    `/social/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    }
  );
}

export async function createMoment(
  payload: CreateMomentRequestContract
): Promise<MessageRecordContract | null> {
  return fetchBackendJson<MessageRecordContract>("/social/moments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}
