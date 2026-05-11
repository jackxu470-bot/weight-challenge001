export type Profile = {
  id: string;
  name: string;
  password: string;
  initialWeight: number;
  avatarColor: string;
  isAdmin: boolean;
  createdAt: string;
};

export type WeightLog = {
  id: number;
  userId: string;
  weight: number;
  loggedDate: string;
  createdAt: string;
};

type Config = {
  prizePool: number;
  startDate: string;
};

const AVATAR_COLORS = ['#F8A4A4', '#A8E6CF', '#FFD3B6', '#D5AAFF', '#87CEEB', '#FFB7B2', '#B5EAD7', '#C7CEEA'];

function getProfiles(): Profile[] {
  return JSON.parse(localStorage.getItem('wc_profiles') || '[]');
}
function saveProfiles(p: Profile[]) { localStorage.setItem('wc_profiles', JSON.stringify(p)); }

function getLogs(): WeightLog[] {
  return JSON.parse(localStorage.getItem('wc_logs') || '[]');
}
function saveLogs(l: WeightLog[]) { localStorage.setItem('wc_logs', JSON.stringify(l)); }

function getConfig(): Config {
  return JSON.parse(localStorage.getItem('wc_config') || '{"prizePool":1000,"startDate":""}');
}
function saveConfig(c: Config) { localStorage.setItem('wc_config', JSON.stringify(c)); }

export const storage = {
  // --- Profiles ---
  getProfiles,
  getProfileById(id: string) { return getProfiles().find(p => p.id === id); },
  getProfileByName(name: string) { return getProfiles().find(p => p.name === name); },

  createProfile(name: string, password: string, initialWeight: number, isAdmin = false): Profile {
    const profiles = getProfiles();
    if (profiles.find(p => p.name === name)) throw new Error('名字已存在');
    const profile: Profile = {
      id: crypto.randomUUID(),
      name,
      password,
      initialWeight,
      avatarColor: AVATAR_COLORS[profiles.length % AVATAR_COLORS.length],
      isAdmin,
      createdAt: new Date().toISOString(),
    };
    saveProfiles([...profiles, profile]);
    return profile;
  },

  removeProfile(id: string) {
    saveProfiles(getProfiles().filter(p => p.id !== id));
    saveLogs(getLogs().filter(l => l.userId !== id));
  },

  verifyLogin(name: string, password: string): Profile | null {
    const p = storage.getProfileByName(name);
    if (p && p.password === password) return p;
    return null;
  },

  // --- Weight Logs ---
  getLogsByUser(userId: string): WeightLog[] {
    return getLogs().filter(l => l.userId === userId).sort((a, b) => b.loggedDate.localeCompare(a.loggedDate));
  },

  getAllLatestWeights(): Map<string, { weight: number; date: string }> {
    const logs = getLogs();
    const map = new Map<string, { weight: number; date: string }>();
    for (const l of logs) {
      const cur = map.get(l.userId);
      if (!cur || l.loggedDate > cur.date) {
        map.set(l.userId, { weight: l.weight, date: l.loggedDate });
      }
    }
    return map;
  },

  addWeightLog(userId: string, weight: number, loggedDate: string): WeightLog {
    const logs = getLogs();
    // replace same-date entry
    const filtered = logs.filter(l => !(l.userId === userId && l.loggedDate === loggedDate));
    const entry: WeightLog = {
      id: Date.now(),
      userId,
      weight,
      loggedDate,
      createdAt: new Date().toISOString(),
    };
    saveLogs([...filtered, entry]);
    return entry;
  },

  // --- Config ---
  getConfig,
  updateConfig(updates: Partial<Config>) {
    saveConfig({ ...getConfig(), ...updates });
  },

  // --- Reset ---
  resetAll() {
    localStorage.removeItem('wc_profiles');
    localStorage.removeItem('wc_logs');
    localStorage.removeItem('wc_config');
  },
};
