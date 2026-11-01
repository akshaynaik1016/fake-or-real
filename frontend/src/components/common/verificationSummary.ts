import type { VerificationCheckItem } from '../../api/client';
export function checkStatus(value: string) {
  if (value === 'passed') return 'verified';
  return ['verified','failed','warning','unavailable','not_performed'].includes(value) ? value : 'unavailable';
}
export function summarizeVerification(checks: VerificationCheckItem[]) {
  const counts = { verified: 0, failed: 0, warning: 0, unavailable: 0, not_performed: 0 };
  for (const check of checks) counts[checkStatus(check.status) as keyof typeof counts]++;
  const unresolved = counts.warning + counts.unavailable + counts.not_performed;
  return { ...counts, unresolved, text: `${counts.failed} failed · ${unresolved} unresolved · ${counts.verified} verified` };
}
