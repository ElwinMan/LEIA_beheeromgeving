/**
 * Checks if targetId is a descendant of parentId in a tree structure.
 * @param items - Array of tree nodes
 * @param parentId - The id of the parent node
 * @param targetId - The id to check for being a descendant
 * @param idKey - The property name for the node id (default: 'id')
 * @param childrenKey - The property name for children array (default: 'subgroups')
 */
export function isDescendant(
  items: any[],
  parentId: any,
  targetId: any,
  idKey: string = 'id',
  childrenKey: string = 'subgroups'
): boolean {
  const parent = findNodeById(items, parentId, idKey, childrenKey);
  if (!parent) return false;

  function checkChildren(children: any[]): boolean {
    for (const child of children) {
      if (child[idKey] === targetId) return true;
      if (checkChildren(child[childrenKey] || [])) return true;
    }
    return false;
  }

  return checkChildren(parent[childrenKey] || []);
}

/**
 * Finds a node by id in a tree structure.
 * @param items - Array of tree nodes
 * @param id - The id to find
 * @param idKey - The property name for the node id (default: 'id')
 * @param childrenKey - The property name for children array (default: 'subgroups')
 */
export function findNodeById(
  items: any[],
  id: any,
  idKey: string = 'id',
  childrenKey: string = 'subgroups'
): any | null {
  for (const item of items) {
    if (item[idKey] === id) return item;
    const found = findNodeById(item[childrenKey] || [], id, idKey, childrenKey);
    if (found) return found;
  }
  return null;
}