export type ActionType =
  | "group_message"
  | "private_message"
  | "moment_post"
  | "moment_comment"
  | "plan_update"
  | "ignore";

export type VisibilityMode = "realtime" | "delayed" | "hidden";

export interface DirectorExplanation {
  summary: string;
  confidence: number;
}

export interface ActionDecision {
  actionType: ActionType;
  targetId?: string;
  reason: string;
  shouldAdjustPlan: boolean;
}

export interface CharacterStateContract {
  id: string;
  displayName: string;
  currentPlanSummary: string;
  emotionState: string;
  socialDrive: number;
  interruptThreshold: number;
}

export interface PermissionView {
  privateChatVisibility: VisibilityMode;
  planVisibility: VisibilityMode;
  relationshipVisibility: VisibilityMode;
  canInjectEvents: boolean;
  canControlWorld: boolean;
}

export interface DirectorLogEntryContract {
  event_id: string;
  sequence_number: number;
  kind: string;
  summary: string;
  created_at: string;
  character_id?: string | null;
  director_explanation?: string | null;
}

export interface DirectorConversationPreviewContract {
  id: string;
  title: string;
  conversation_type: string;
  participant_ids: string[];
  last_message_preview?: string | null;
  last_message_sender_id?: string | null;
  last_message_sender_name?: string | null;
  last_message_at?: string | null;
}

export interface DirectorCharacterSnapshotContract {
  id: string;
  display_name: string;
  emotion_state: string;
  current_plan_summary: string;
  social_drive: number;
  interrupt_threshold: number;
  next_task_type?: string | null;
  next_task_intent?: string | null;
  next_task_run_at?: string | null;
}

export interface DirectorRelationshipEdgeContract {
  source_character_id: string;
  source_display_name: string;
  target_character_id: string;
  target_display_name: string;
  affinity: number;
  labels: string[];
  updated_at?: string | null;
}

export interface DirectorMomentInteractionEntryContract {
  id: string;
  interaction_type: string;
  actor_id: string;
  actor_display_name: string;
  target_moment_id: string;
  target_moment_preview: string;
  target_moment_sender_id?: string | null;
  target_moment_sender_name?: string | null;
  content?: string | null;
  created_at: string;
}

export type DirectorTaskIntentContract =
  | "reply_to_direct_prompt"
  | "check_group_chat"
  | "share_update"
  | "stay_on_task";

export interface InjectDirectorEventRequestContract {
  summary: string;
  target_character_id?: string | null;
  task_intent?: DirectorTaskIntentContract | string | null;
}

export interface DirectorPanelStateContract {
  world_id: string;
  current_time: string;
  speed_multiplier: number;
  paused: boolean;
  director_visibility_delay_seconds: number;
  pending_task_count: number;
  permissions: {
    private_chat_visibility: VisibilityMode;
    plan_visibility: VisibilityMode;
    relationship_visibility: VisibilityMode;
    can_inject_events: boolean;
    can_control_world: boolean;
  };
  characters: DirectorCharacterSnapshotContract[];
  relationships: DirectorRelationshipEdgeContract[];
  conversations: DirectorConversationPreviewContract[];
  moment_interactions: DirectorMomentInteractionEntryContract[];
  recent_logs: DirectorLogEntryContract[];
}

export interface WorldClockStateContract {
  now: string;
  speed_multiplier: number;
  paused: boolean;
}

export interface WorldCharacterStateContract {
  id: string;
  display_name: string;
  current_plan_summary: string;
  emotion_state: string;
  social_drive: number;
  interrupt_threshold: number;
}

export interface WorldStateContract {
  world_id: string;
  clock: WorldClockStateContract;
  active_characters: WorldCharacterStateContract[];
  recent_events: string[];
  pending_tasks: string[];
}

export interface CharacterProfileContract {
  identity_and_background: string;
  personality: string;
  speaking_style: string;
  appearance_and_presence: string;
  additional_notes: string;
}

export interface EditableCharacterContract {
  id: string;
  display_name: string;
  profile: CharacterProfileContract;
  current_plan_summary: string;
  emotion_state: string;
  social_drive: number;
  interrupt_threshold: number;
}

export interface CreateCharacterRequestContract {
  display_name: string;
  profile: CharacterProfileContract;
  current_plan_summary: string;
  emotion_state: string;
  social_drive: number;
  interrupt_threshold: number;
}

export interface UpdateCharacterRequestContract extends CreateCharacterRequestContract {}

export interface DeleteCharacterResponseContract {
  character_id: string;
}

export type ConversationTypeContract = "group" | "private" | "moment";

export interface ConversationSummaryContract {
  id: string;
  title: string;
  conversation_type: ConversationTypeContract;
  participant_ids: string[];
}

export interface MessageRecordContract {
  id: string;
  conversation_id: string;
  conversation_type: ConversationTypeContract;
  sender_id: string;
  content: string;
  created_at: string;
  target_id?: string | null;
  mentions: string[];
}

export interface CreateMessageRequestContract {
  conversation_id: string;
  conversation_type: ConversationTypeContract;
  sender_id: string;
  content: string;
  target_id?: string | null;
  mentions?: string[];
  created_at?: string;
}

export interface CreateMomentRequestContract {
  sender_id: string;
  content: string;
  mentions?: string[];
  created_at?: string;
}
