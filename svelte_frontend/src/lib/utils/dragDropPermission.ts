import { isDescendant } from './isDescendantPrevention';

export type DragItemType = string;
export type DropTargetType = string;
export type DropZone = 'top' | 'middle' | 'bottom';

export interface DragItem {
  type: DragItemType;
  id: number;
  groupId?: number | null;
  [key: string]: any;
}

export interface DropTarget {
  type: DropTargetType;
  id: number;
  groupId?: number | null;
  zone: DropZone;
}

export interface DropPermissionConfig {
  // Allowed drop combinations: { [dragType]: { [dropType]: allowedZones[] } }
  allowed: {
    [dragType: string]: {
      [dropType: string]: DropZone[] | 'any';
    };
  };
  // Optional: custom rules for special cases
  custom?: (
    dragged: DragItem,
    target: DropTarget,
    rootTree: any[]
  ) => { allowed: boolean; reason?: string } | undefined;
}

export function canDropGeneric(
  draggedItem: DragItem | null,
  target: DropTarget,
  rootTree: any[],
  config: DropPermissionConfig
): { allowed: boolean; reason?: string } {
  if (!draggedItem) return { allowed: false, reason: 'No dragged item' };

  // Don't allow dropping on itself
  if (draggedItem.type === target.type && draggedItem.id === target.id) {
    return { allowed: false, reason: 'Cannot drop on itself' };
  }

  // Custom rules (e.g. descendant prevention)
  if (config.custom) {
    const customResult = config.custom(draggedItem, target, rootTree);
    if (customResult !== undefined) return customResult;
  }

  // Check allowed combinations
  const allowedDropTypes = config.allowed[draggedItem.type];
  if (!allowedDropTypes) return { allowed: false, reason: 'Drag type not allowed' };

  const allowedZones = allowedDropTypes[target.type];
  if (!allowedZones) return { allowed: false, reason: 'Drop type not allowed for this drag type' };

  if (allowedZones === 'any' || allowedZones.includes(target.zone)) {
    return { allowed: true };
  }

  return { allowed: false, reason: 'Drop zone not allowed' };
}