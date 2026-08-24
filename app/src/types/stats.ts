// Mirrors the shape produced by the backend pipeline (gacha-stats-backend,
// scripts/stats_schema.py + scripts/update_stats.py) and written to data/stats.json.
// This is descriptive typing for the frontend only — the Pydantic schema in the
// backend is the actual validation boundary.

export interface CharacterEquip {
  name: string;
  icon: string;
  rarity: number;
  level: number;
  superimposition: number;
}

export interface HsrCharacter {
  icon: string;
  eidolon: number;
  element: string;
  path: string;
  level: number;
  lc: CharacterEquip | null;
}

export interface ChallengeNode {
  id: number;
  level: number;
  eidolon: number;
}

export interface ApocalypticShadowFloor {
  floor: string;
  score: number;
  node_1: ChallengeNode[] | null;
  node_2: ChallengeNode[] | null;
  node_3: ChallengeNode[] | null;
}

export interface PureFictionFloor {
  floor: string;
  score: number;
  node_1: ChallengeNode[] | null;
  node_2: ChallengeNode[] | null;
  node_3: ChallengeNode[] | null;
}

export interface MemoryOfChaosFloor {
  floor: string;
  cycles: number;
  first_half: ChallengeNode[];
  second_half: ChallengeNode[];
}

export interface AnomalyArbitrationRecord {
  characters: ChallengeNode[];
}

export interface AnomalyArbitration {
  season: string | null;
  cycles_used: number;
  boss_stars: number;
  mini_boss_stars: number;
  boss_record: AnomalyArbitrationRecord | null;
  mini_boss_records: AnomalyArbitrationRecord[] | null;
}

export interface HsrData {
  nickname: string;
  level: number;
  avatar_url: string;
  achievements: number;
  active_days: number;
  avatar_count: number;
  chest_count: number;
  five_star_characters: Record<string, HsrCharacter>;
  stamina: number | null;
  current_train_score: number | null;
  apocalyptic_shadow: { total_stars: number; floor_data: ApocalypticShadowFloor } | null;
  pure_fiction: { total_stars: number; floor_data: PureFictionFloor } | null;
  memory_of_chaos: { season: string; total_stars: number; floor_data: MemoryOfChaosFloor } | null;
  anomaly_arbitration: AnomalyArbitration | null;
}

export interface GenshinWeapon {
  name: string;
  icon: string;
  rarity: number;
  level: number;
  refinement: number;
}

export interface GenshinCharacter {
  icon: string;
  constellation: number;
  element: string;
  weaponType: string;
  level: number;
  friendship: number;
  weapon: GenshinWeapon | null;
}

export interface GenshinData {
  nickname: string;
  level: number;
  avatar_url: string;
  achievements: number;
  active_days: number;
  avatar_count: number;
  oculus: number;
  chest_count: number;
  five_star_characters: Record<string, GenshinCharacter>;
  resin: number | null;
  daily_task: number | null;
}

export interface EndfieldWeapon {
  name: string;
  iconUrl: string;
  rarity: string;
  type: string;
  level: number;
  refineLevel: number;
}

export interface EndfieldCharacter {
  avatarSqUrl: string;
  rarity: string;
  potential: number;
  profession: string;
  property: string;
  weaponType: string;
  level: number;
  owned_at: number;
  weapon: EndfieldWeapon | null;
}

export interface EndfieldData {
  nickname: string;
  level: number;
  avatar_url: string;
  achievements: number;
  active_days: number;
  avatar_count: number;
  aurylenes: number;
  chest_count: number;
  six_star_characters: Record<string, EndfieldCharacter>;
  stamina: string | number | null;
  daily_mission: number | null;
  last_updated: string | null;
}

export interface DiaryRow {
  Date: string;
  "Net Currency Gain": number;
  "Pulls Net Gain": number;
}

export interface EndfieldAttendanceReward {
  name: string;
  count: number;
  icon: string;
}

export interface EndfieldAttendance {
  status: string;
  rewards: EndfieldAttendanceReward[];
  attendance: {
    totalSignIns: number;
    calendar: { awardId: string; available: boolean; done: boolean }[];
  };
}

export type DegradedSection = "hsr_data" | "genshin_data" | "endfield_data";

export interface Stats {
  last_updated: string;
  hsr_data: HsrData | null;
  genshin_data: GenshinData | null;
  hsr_diary: DiaryRow | null;
  genshin_diary: DiaryRow | null;
  endfield_attendance: EndfieldAttendance | null;
  endfield_data: EndfieldData | null;
  degraded_sections: DegradedSection[];
}
