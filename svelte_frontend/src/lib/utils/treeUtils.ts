/**
 * Generic utility functions for working with tree-like data structures
 */

/**
 * Interface for objects that have nested children and items to count
 */
export interface TreeNode<T = any> {
  /** Array of child nodes */
  children?: TreeNode<T>[];
  /** Array of items to count in this node */
  items?: T[];
}

/**
 * Recursively counts all items in a tree structure
 * @param node - The tree node to count items from
 * @param itemsKey - The key name for the items array (default: 'items')
 * @param childrenKey - The key name for the children array (default: 'children')
 * @returns Total count of items in the node and all its descendants
 */
export function getTotalItemsInTree<T extends Record<string, any>>(
  node: T,
  itemsKey: string = 'items',
  childrenKey: string = 'children'
): number {
  // Count items in current node
  const items = node[itemsKey];
  let total = Array.isArray(items) ? items.length : 0;

  // Recursively count items in child nodes
  const children = node[childrenKey];
  if (Array.isArray(children)) {
    for (const child of children) {
      total += getTotalItemsInTree(child, itemsKey, childrenKey);
    }
  }

  return total;
}

/**
 * Specifically for counting layers in groups (maintains backward compatibility)
 * @param group - Group object with layers and subgroups
 * @returns Total number of layers in the group and all subgroups
 */
export function getTotalLayersInGroup(group: { layers: any[]; subgroups: any[] }): number {
  return getTotalItemsInTree(group, 'layers', 'subgroups');
}
