export interface GraphLayoutNode { id: string; type: string; label: string }
export function shortLabel(value: string, limit = 64): string {
  const clean = value.replace(/\s+/g, ' ').trim();
  return clean.length > limit ? `${clean.slice(0, limit - 1)}…` : clean;
}
export function layoutTrustGraph(nodes: GraphLayoutNode[]) {
  const identity = nodes.filter(n => ['offer', 'organization', 'notice', 'case'].includes(n.type));
  const entities = nodes.filter(n => !['offer', 'organization', 'notice', 'case', 'evidence', 'source', 'contradiction', 'cross_finding'].includes(n.type));
  const findings = nodes.filter(n => ['evidence', 'source', 'contradiction', 'cross_finding'].includes(n.type));
  const positions: Record<string, { x: number; y: number }> = {};
  identity.forEach((n, i) => { positions[n.id] = { x: 0, y: i * 150 }; });
  entities.forEach((n, i) => { positions[n.id] = { x: 330, y: i * 125 }; });
  findings.forEach((n, i) => { positions[n.id] = { x: 660 + (i % 2) * 270, y: Math.floor(i / 2) * 112 }; });
  return nodes.map(n => ({ id: n.id, position: positions[n.id], label: shortLabel(n.label),
    column: ['offer','organization', 'notice','case'].includes(n.type) ? 'identity' : ['evidence','source','contradiction','cross_finding'].includes(n.type) ? 'evidence' : 'entity' }));
}
