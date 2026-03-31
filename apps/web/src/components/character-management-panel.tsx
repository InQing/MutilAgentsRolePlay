"use client";

import type {
  CharacterProfileContract,
  CreateCharacterRequestContract,
  EditableCharacterContract,
  UpdateCharacterRequestContract
} from "@mutilagentsroleplay/shared-contracts";
import { useEffect, useState, useTransition } from "react";

type CharacterManagementPanelProps = {
  initialCharacters: EditableCharacterContract[] | null;
};

type CharacterFormState = {
  display_name: string;
  profile: CharacterProfileContract;
  current_plan_summary: string;
  emotion_state: string;
  social_drive: number;
  interrupt_threshold: number;
};

const emptyProfile: CharacterProfileContract = {
  identity_and_background: "",
  personality: "",
  speaking_style: "",
  appearance_and_presence: "",
  additional_notes: ""
};

function createEmptyFormState(): CharacterFormState {
  return {
    display_name: "",
    profile: { ...emptyProfile },
    current_plan_summary: "",
    emotion_state: "steady",
    social_drive: 0.5,
    interrupt_threshold: 0.5
  };
}

function sortCharacters(items: EditableCharacterContract[]) {
  return [...items].sort((left, right) =>
    left.display_name.localeCompare(right.display_name, "zh-CN")
  );
}

function toFormState(character: EditableCharacterContract): CharacterFormState {
  return {
    display_name: character.display_name,
    profile: { ...character.profile },
    current_plan_summary: character.current_plan_summary,
    emotion_state: character.emotion_state,
    social_drive: character.social_drive,
    interrupt_threshold: character.interrupt_threshold
  };
}

async function fetchCharactersFromProxy() {
  const response = await fetch("/api/characters", {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("角色管理 API 当前不可达。");
  }

  return (await response.json()) as EditableCharacterContract[];
}

export function CharacterManagementPanel({
  initialCharacters
}: CharacterManagementPanelProps) {
  const [characters, setCharacters] = useState<EditableCharacterContract[]>(
    sortCharacters(initialCharacters ?? [])
  );
  const [selectedCharacterId, setSelectedCharacterId] = useState<string | null>(
    initialCharacters?.[0]?.id ?? null
  );
  const [draft, setDraft] = useState<CharacterFormState>(
    initialCharacters?.[0] ? toFormState(initialCharacters[0]) : createEmptyFormState()
  );
  const [isCreating, setIsCreating] = useState(initialCharacters?.length ? false : true);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    if (initialCharacters !== null) {
      return;
    }

    let cancelled = false;
    startTransition(() => {
      void (async () => {
        try {
          const nextCharacters = await fetchCharactersFromProxy();
          if (cancelled) {
            return;
          }

          const sorted = sortCharacters(nextCharacters);
          setCharacters(sorted);
          if (sorted[0]) {
            setSelectedCharacterId(sorted[0].id);
            setDraft(toFormState(sorted[0]));
            setIsCreating(false);
          } else {
            setSelectedCharacterId(null);
            setDraft(createEmptyFormState());
            setIsCreating(true);
          }
        } catch (error) {
          if (!cancelled) {
            setFeedback(
              error instanceof Error ? error.message : "角色列表读取失败。"
            );
          }
        }
      })();
    });

    return () => {
      cancelled = true;
    };
  }, [initialCharacters]);

  function selectCharacter(character: EditableCharacterContract) {
    setSelectedCharacterId(character.id);
    setDraft(toFormState(character));
    setIsCreating(false);
    setFeedback(null);
  }

  function handleNewCharacter() {
    setSelectedCharacterId(null);
    setDraft(createEmptyFormState());
    setIsCreating(true);
    setFeedback("已切换到新角色创建表单。");
  }

  function handleFieldChange<K extends keyof CharacterFormState>(
    key: K,
    value: CharacterFormState[K]
  ) {
    setDraft((current) => ({
      ...current,
      [key]: value
    }));
  }

  function handleProfileChange<K extends keyof CharacterProfileContract>(
    key: K,
    value: CharacterProfileContract[K]
  ) {
    setDraft((current) => ({
      ...current,
      profile: {
        ...current.profile,
        [key]: value
      }
    }));
  }

  function handleSave() {
    setFeedback(null);
    startTransition(() => {
      void (async () => {
        const payload: CreateCharacterRequestContract | UpdateCharacterRequestContract = {
          display_name: draft.display_name,
          profile: draft.profile,
          current_plan_summary: draft.current_plan_summary,
          emotion_state: draft.emotion_state,
          social_drive: draft.social_drive,
          interrupt_threshold: draft.interrupt_threshold
        };

        const endpoint = isCreating
          ? "/api/characters"
          : `/api/characters/${selectedCharacterId}`;
        const method = isCreating ? "POST" : "PUT";
        const response = await fetch(endpoint, {
          method,
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const errorPayload = (await response.json().catch(() => null)) as
            | { detail?: string; message?: string }
            | null;
          setFeedback(errorPayload?.detail ?? errorPayload?.message ?? "角色保存失败。");
          return;
        }

        const saved = (await response.json()) as EditableCharacterContract;
        setCharacters((current) => {
          const next = current.filter((item) => item.id !== saved.id);
          return sortCharacters([...next, saved]);
        });
        setSelectedCharacterId(saved.id);
        setDraft(toFormState(saved));
        setIsCreating(false);
        setFeedback(isCreating ? "新角色已创建，并已进入当前世界。" : "角色更新已保存并立即生效。");
      })();
    });
  }

  function handleDelete() {
    if (selectedCharacterId === null) {
      return;
    }

    const target = characters.find((character) => character.id === selectedCharacterId);
    if (target === undefined) {
      return;
    }

    if (!window.confirm(`确认删除角色「${target.display_name}」吗？历史消息会保留，但该角色会从当前世界移除。`)) {
      return;
    }

    setFeedback(null);
    startTransition(() => {
      void (async () => {
        const response = await fetch(`/api/characters/${target.id}`, {
          method: "DELETE"
        });

        if (!response.ok) {
          const errorPayload = (await response.json().catch(() => null)) as
            | { detail?: string; message?: string }
            | null;
          setFeedback(errorPayload?.detail ?? errorPayload?.message ?? "角色删除失败。");
          return;
        }

        const nextCharacters = characters.filter((character) => character.id !== target.id);
        const sorted = sortCharacters(nextCharacters);
        setCharacters(sorted);
        if (sorted[0]) {
          setSelectedCharacterId(sorted[0].id);
          setDraft(toFormState(sorted[0]));
          setIsCreating(false);
        } else {
          setSelectedCharacterId(null);
          setDraft(createEmptyFormState());
          setIsCreating(true);
        }
        setFeedback("角色已从当前世界移除，历史记录仍然保留。");
      })();
    });
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <section className="glass p-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="eyebrow">Character Manager</p>
            <h2 className="text-2xl font-semibold text-ink">当前世界角色</h2>
          </div>
          <button
            className="rounded-full bg-orange-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:bg-orange-300"
            disabled={isPending}
            onClick={handleNewCharacter}
            type="button"
          >
            新增角色
          </button>
        </div>
        <p className="muted mt-4 text-sm leading-6">
          这里维护角色定义与当前运行参数。保存后会立即影响当前世界的后续行为，为后面的表达层与多模型接入提供统一角色来源。
        </p>
        <div className="mt-6 space-y-3">
          {characters.map((character) => {
            const isSelected = !isCreating && selectedCharacterId === character.id;
            return (
              <button
                key={character.id}
                className={`w-full rounded-2xl border px-4 py-4 text-left transition ${
                  isSelected
                    ? "border-orange-400 bg-orange-50"
                    : "border-slate-200 bg-white/70 hover:border-slate-300 hover:bg-white"
                }`}
                onClick={() => selectCharacter(character)}
                type="button"
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h3 className="text-base font-semibold text-ink">{character.display_name}</h3>
                    <p className="mt-1 text-xs uppercase tracking-[0.14em] text-slate-500">
                      {character.emotion_state}
                    </p>
                  </div>
                  <div className="text-right text-xs text-slate-500">
                    <p>社交驱动力 {character.social_drive.toFixed(2)}</p>
                    <p>打断阈值 {character.interrupt_threshold.toFixed(2)}</p>
                  </div>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-700">
                  当前计划：{character.current_plan_summary}
                </p>
              </button>
            );
          })}
          {!characters.length ? (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-white/60 px-4 py-4 text-sm text-slate-600">
              当前世界还没有角色，先从右侧创建第一个角色。
            </div>
          ) : null}
        </div>
      </section>

      <section className="glass p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="eyebrow">{isCreating ? "New Character" : "Edit Character"}</p>
            <h2 className="text-2xl font-semibold text-ink">
              {isCreating ? "创建角色" : "编辑角色"}
            </h2>
          </div>
          {!isCreating ? (
            <button
              className="rounded-full border border-rose-300 bg-white px-4 py-2 text-sm font-semibold text-rose-700 transition hover:border-rose-400 hover:bg-rose-50 disabled:cursor-not-allowed disabled:text-rose-300"
              disabled={isPending}
              onClick={handleDelete}
              type="button"
            >
              删除角色
            </button>
          ) : null}
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <section className="space-y-4 rounded-2xl border border-slate-200 bg-white/70 p-5">
            <h3 className="text-lg font-semibold text-ink">角色画像</h3>
            <label className="block text-sm font-medium text-slate-700">
              显示名
              <input
                className="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-400"
                onChange={(event) => handleFieldChange("display_name", event.target.value)}
                value={draft.display_name}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              身份与背景
              <textarea
                className="mt-2 min-h-24 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-400"
                onChange={(event) =>
                  handleProfileChange("identity_and_background", event.target.value)
                }
                value={draft.profile.identity_and_background}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              性格
              <textarea
                className="mt-2 min-h-24 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-400"
                onChange={(event) => handleProfileChange("personality", event.target.value)}
                value={draft.profile.personality}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              说话风格
              <textarea
                className="mt-2 min-h-24 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-400"
                onChange={(event) => handleProfileChange("speaking_style", event.target.value)}
                value={draft.profile.speaking_style}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              外在气质
              <textarea
                className="mt-2 min-h-24 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-400"
                onChange={(event) =>
                  handleProfileChange("appearance_and_presence", event.target.value)
                }
                value={draft.profile.appearance_and_presence}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              额外备注
              <textarea
                className="mt-2 min-h-24 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-400"
                onChange={(event) => handleProfileChange("additional_notes", event.target.value)}
                value={draft.profile.additional_notes}
              />
            </label>
          </section>

          <section className="space-y-4 rounded-2xl border border-slate-200 bg-white/70 p-5">
            <h3 className="text-lg font-semibold text-ink">行为参数</h3>
            <label className="block text-sm font-medium text-slate-700">
              当前计划
              <textarea
                className="mt-2 min-h-24 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-400"
                onChange={(event) =>
                  handleFieldChange("current_plan_summary", event.target.value)
                }
                value={draft.current_plan_summary}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              当前情绪
              <input
                className="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-400"
                onChange={(event) => handleFieldChange("emotion_state", event.target.value)}
                value={draft.emotion_state}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              社交驱动力
              <input
                className="mt-2 w-full"
                max="1"
                min="0"
                onChange={(event) =>
                  handleFieldChange("social_drive", Number(event.target.value))
                }
                step="0.01"
                type="range"
                value={draft.social_drive}
              />
              <p className="mt-2 text-sm text-slate-600">{draft.social_drive.toFixed(2)}</p>
            </label>
            <label className="block text-sm font-medium text-slate-700">
              打断阈值
              <input
                className="mt-2 w-full"
                max="1"
                min="0"
                onChange={(event) =>
                  handleFieldChange("interrupt_threshold", Number(event.target.value))
                }
                step="0.01"
                type="range"
                value={draft.interrupt_threshold}
              />
              <p className="mt-2 text-sm text-slate-600">
                {draft.interrupt_threshold.toFixed(2)}
              </p>
            </label>
            <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-4 text-sm leading-6 text-slate-600">
              修改后会立即影响当前世界中的该角色。删除角色只会把它从 active world 移除，不会物理删除历史消息和历史事件。
            </div>
          </section>
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button
            className="rounded-full bg-orange-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:bg-orange-300"
            disabled={isPending}
            onClick={handleSave}
            type="button"
          >
            {isPending ? "保存中..." : isCreating ? "创建角色" : "保存修改"}
          </button>
          {feedback ? <p className="text-sm text-slate-600">{feedback}</p> : null}
        </div>
      </section>
    </section>
  );
}
