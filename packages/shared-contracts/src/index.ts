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

