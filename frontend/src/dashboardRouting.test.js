import test from 'node:test';
import assert from 'node:assert/strict';

import {
  getDashboardEntryRoute,
  getDashboardRouteForUser,
  setDashboardSelection,
  clearDashboardSelection,
} from './dashboardRouting.js';

test('provider users without a saved selection go to the dashboard chooser', () => {
  clearDashboardSelection();
  assert.equal(getDashboardEntryRoute({ is_provider: true, is_admin: false }), '/dashboard/choose');
});

test('provider users are always sent to the chooser when they log in', () => {
  clearDashboardSelection();
  setDashboardSelection('customer');
  assert.equal(getDashboardRouteForUser({ is_provider: true, is_admin: false }), '/dashboard/choose');
});

test('provider users can still choose the provider dashboard from the chooser', () => {
  clearDashboardSelection();
  setDashboardSelection('provider');
  assert.equal(getDashboardRouteForUser({ is_provider: true, is_admin: false }), '/dashboard/choose');
});
