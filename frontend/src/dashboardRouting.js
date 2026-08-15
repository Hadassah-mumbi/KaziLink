const STORAGE_KEY = 'kazilink_dashboard_selection';

function getStorage() {
  if (typeof window !== 'undefined' && window.localStorage) {
    return window.localStorage;
  }

  if (!globalThis.__kazilink_dashboard_storage) {
    globalThis.__kazilink_dashboard_storage = {};
  }

  return globalThis.__kazilink_dashboard_storage;
}

export function getStoredDashboardSelection() {
  try {
    return getStorage().getItem ? getStorage().getItem(STORAGE_KEY) : getStorage()[STORAGE_KEY] ?? null;
  } catch {
    return null;
  }
}

export function setDashboardSelection(mode) {
  if (!['customer', 'provider'].includes(mode)) return null;

  try {
    const storage = getStorage();
    if (storage.setItem) {
      storage.setItem(STORAGE_KEY, mode);
    } else {
      storage[STORAGE_KEY] = mode;
    }
    return mode;
  } catch {
    return null;
  }
}

export function clearDashboardSelection() {
  try {
    const storage = getStorage();
    if (storage.removeItem) {
      storage.removeItem(STORAGE_KEY);
    } else {
      delete storage[STORAGE_KEY];
    }
  } catch {
    // ignore storage failures
  }
}

export function getDashboardRouteForUser(user) {
  if (user?.is_admin) return '/admin/dashboard';
  if (user?.is_provider) return '/dashboard/choose';
  return '/dashboard';
}

export function getDashboardEntryRoute(user) {
  return getDashboardRouteForUser(user);
}
