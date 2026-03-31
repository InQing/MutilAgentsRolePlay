from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


def _normalize_required_text(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("value must not be empty")
    return normalized


def _normalize_optional_text(value: str) -> str:
    return value.strip()


class CharacterProfile(BaseModel):
    identity_and_background: str = "待补充角色背景。"
    personality: str = "待补充角色性格。"
    speaking_style: str = "待补充说话风格。"
    appearance_and_presence: str = "待补充外在气质。"
    additional_notes: str = ""

    @field_validator(
        "identity_and_background",
        "personality",
        "speaking_style",
        "appearance_and_presence",
    )
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator("additional_notes")
    @classmethod
    def validate_optional_text(cls, value: str) -> str:
        return _normalize_optional_text(value)


def build_default_character_profile(*, character_id: str, display_name: str) -> CharacterProfile:
    sample_profiles = {
        "char-001": CharacterProfile(
            identity_and_background="热衷组织聚会与维持社交连接，习惯主动留意群体气氛。",
            personality="外向、敏锐、愿意主动接话，也会在意大家是否被照顾到。",
            speaking_style="语气热络，常用带气氛感的表达，喜欢先抛一个轻松的话头。",
            appearance_and_presence="给人精力充沛、容易靠近的印象，出场时存在感比较强。",
            additional_notes="适合承担破冰、串场和推动群体互动的角色。",
        ),
        "char-002": CharacterProfile(
            identity_and_background="工作节奏稳定，习惯先完成手头事务，再决定是否参与社交。",
            personality="克制、专注、边界感明确，不会轻易被无关信息打断。",
            speaking_style="句子偏短，信息密度高，表达直接但不会失礼。",
            appearance_and_presence="给人安静、可靠、略带距离感的印象。",
            additional_notes="更适合在必要时回应，而不是主动制造大量话题。",
        ),
    }
    return sample_profiles.get(
        character_id,
        CharacterProfile(
            identity_and_background=f"{display_name} 的角色背景待进一步补充。",
            personality="性格画像待进一步补充。",
            speaking_style="说话风格待进一步补充。",
            appearance_and_presence="外在气质待进一步补充。",
            additional_notes="当前为默认生成的人设占位。",
        ),
    )


class CharacterState(BaseModel):
    id: str
    display_name: str
    current_plan_summary: str
    emotion_state: str = "steady"
    social_drive: float = Field(default=0.5, ge=0.0, le=1.0)
    interrupt_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    profile: CharacterProfile = Field(default_factory=CharacterProfile, exclude=True)


class EditableCharacter(BaseModel):
    id: str
    display_name: str
    profile: CharacterProfile
    current_plan_summary: str
    emotion_state: str = "steady"
    social_drive: float = Field(default=0.5, ge=0.0, le=1.0)
    interrupt_threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class CharacterMutationPayload(BaseModel):
    display_name: str
    profile: CharacterProfile
    current_plan_summary: str
    emotion_state: str = "steady"
    social_drive: float = Field(default=0.5, ge=0.0, le=1.0)
    interrupt_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator("display_name", "current_plan_summary", "emotion_state")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)


class CreateCharacterRequest(CharacterMutationPayload):
    pass


class UpdateCharacterRequest(CharacterMutationPayload):
    pass


class DeleteCharacterResponse(BaseModel):
    character_id: str


def build_editable_character(character: CharacterState) -> EditableCharacter:
    return EditableCharacter(
        id=character.id,
        display_name=character.display_name,
        profile=character.profile,
        current_plan_summary=character.current_plan_summary,
        emotion_state=character.emotion_state,
        social_drive=character.social_drive,
        interrupt_threshold=character.interrupt_threshold,
    )


def build_character_state(*, character_id: str | None = None, payload: CharacterMutationPayload) -> CharacterState:
    return CharacterState(
        id=character_id or f"char-{uuid4().hex[:8]}",
        display_name=payload.display_name,
        profile=payload.profile,
        current_plan_summary=payload.current_plan_summary,
        emotion_state=payload.emotion_state,
        social_drive=payload.social_drive,
        interrupt_threshold=payload.interrupt_threshold,
    )
