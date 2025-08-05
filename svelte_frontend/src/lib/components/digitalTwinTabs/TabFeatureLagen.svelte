<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import {
    fetchDigitalTwin,
    fetchLayers,
    fetchGroups,
    bulkUpdateDigitalTwinAssociations
  } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type {
    LayerWithAssociation,
    GroupWithLayers,
    LayerBulkOperation,
    GroupBulkOperation,
    BulkAssociationsPayload
  } from '$lib/types/digitalTwinAssociation';
  import type { Layer } from '$lib/types/layer';
  import type { Group } from '$lib/types/group';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import GroupModal from '$lib/components/modals/CreateGroupModal.svelte';
  import CreateLayerModal from '$lib/components/modals/CreateLayerModal.svelte';
  import DeleteModal from '$lib/components/modals/DeleteModal.svelte';
  import DeleteGroupModal from '$lib/components/modals/DeleteGroupModal.svelte';
  import { isDescendant } from '$lib/utils/isDescendantPrevention';
  import { canDropGeneric } from '$lib/utils/dragDropPermission';
  import type { DropZone } from '$lib/utils/dragDropPermission';
  import { addCatalogItemToList } from '$lib/utils/catalogAddUtil';
  import { dragStartAction } from '$lib/utils/dragStartAction';
  import { getTotalLayersInGroup } from '$lib/utils/treeUtils';
  import { getDropZone } from '$lib/utils/dropZoneUtils';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();
  let groupModalRef: InstanceType<typeof GroupModal>;
  let createLayerModalRef: InstanceType<typeof CreateLayerModal>;
  let deleteLayerModalShow = $state(false);
  let layerToDelete: LayerWithAssociation | null = null;
  let skipDeleteLayerConfirm = false;

  let deleteGroupModalShow = $state(false);
  let groupToDelete = $state<GroupWithLayers | null>(null);
  let deleteGroupOption: 'delete' | 'move' = 'delete';

  onMount(() => {
    // Restore skipDeleteLayerConfirm from sessionStorage if set
    const stored = sessionStorage.getItem('skipDeleteLayerConfirm');
    skipDeleteLayerConfirm = stored === 'true';
  });

  // Deep clone function to replace structuredClone
  function deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
    if (obj instanceof Array) return obj.map((item) => deepClone(item)) as unknown as T;
    if (typeof obj === 'object') {
      const clonedObj = {} as T;
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          clonedObj[key] = deepClone(obj[key]);
        }
      }
      return clonedObj;
    }
    return obj;
  }

  let allLayers = $state<Layer[]>([]);
  let allGroups = $state<Group[]>([]);
  let layersWithDetails = $state<LayerWithAssociation[]>([]);
  let ungroupedLayers = $state<LayerWithAssociation[]>([]);
  let groupedLayers = $state<LayerWithAssociation[]>([]);
  let rootGroups = $state<GroupWithLayers[]>([]);
  let expandedGroups = $state<Set<number>>(new Set());
  let hasChanges = $state(false);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let originalData: { ungroupedLayers: LayerWithAssociation[]; rootGroups: GroupWithLayers[] } = {
    ungroupedLayers: [],
    rootGroups: []
  };
  let isSaving = $state(false);

  // Drag and drop state
  let draggedItem = $state<{
    type: 'layer' | 'group' | 'catalog-layer';
    id: number;
    groupId?: number | null;
    layer?: Layer;
  } | null>(null);
  let draggedOverItem = $state<{
    type: 'layer' | 'group';
    id: number;
    groupId?: number | null;
    zone: 'top' | 'middle' | 'bottom';
  } | null>(null);

  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  // Catalog state
  let catalogLayers = $state<Layer[]>([]);
  let catalogSearchTerm = $state('');
  let catalogIsLoading = $state(true);
  let catalogError = $state<string | null>(null);

  // Get used layer IDs for filtering catalog
  let usedLayerIds = $derived(layersWithDetails.map((l) => l.layer_id));

  let editingGroupId = $state<number | null>(null);
  let editingGroupTitle = $state('');

  // Filter catalog layers
  const filteredCatalogLayers = $derived.by(() => {
    if (catalogSearchTerm.trim() === '') {
      return catalogLayers.filter((layer) => !usedLayerIds.includes(layer.id));
    } else {
      const term = catalogSearchTerm.toLowerCase();
      return catalogLayers.filter(
        (layer) =>
          !usedLayerIds.includes(layer.id) &&
          (layer.title.toLowerCase().includes(term) ||
            layer.type?.toLowerCase().includes(term) ||
            layer.featureName?.toLowerCase().includes(term))
      );
    }
  });

  async function fetchAllData() {
    isLoading = true;
    try {
      digitalTwin = await fetchDigitalTwin(digitalTwinId);
      allLayers = await fetchLayers();
      allGroups = await fetchGroups(digitalTwinId);

      if (digitalTwin?.layer_associations) {
        layersWithDetails = digitalTwin.layer_associations
          .sort((a, b) => a.sort_order - b.sort_order)
          .map((association) => {
            const layerDetails = allLayers.find((layer) => layer.id === association.layer_id);
            return {
              ...association,
              title: layerDetails?.title || `Layer ${association.layer_id}`,
              beschrijving: layerDetails?.type || '',
              featureName: layerDetails?.featureName || '',
              isNew: false
            };
          });

        ungroupedLayers = layersWithDetails.filter((layer) => layer.group_id === null);
        groupedLayers = layersWithDetails.filter((layer) => layer.group_id !== null);
        rootGroups = buildNestedGroups(allGroups, layersWithDetails);
        expandedGroups = new Set(getAllGroupIds(rootGroups));
        originalData = deepClone({ ungroupedLayers, rootGroups });
      } else {
        layersWithDetails = [];
        ungroupedLayers = [];
        groupedLayers = [];
        rootGroups = [];
      }

      catalogIsLoading = true;
      catalogLayers = allLayers;
      catalogIsLoading = false;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error occurred';
    } finally {
      isLoading = false;
    }
  }

  onMount(fetchAllData);

  // dragDropPermission.ts
  const dropConfig = {
    allowed: {
      'catalog-layer': {
        group: ['middle'] as DropZone[],
        layer: ['top', 'middle', 'bottom'] as DropZone[],
      },
      layer: {
        group: ['middle'] as DropZone[],
        layer: ['top', 'middle', 'bottom'] as DropZone[],
      },
      group: {
        group: ['top', 'middle', 'bottom'] as DropZone[],
      },
    },
    custom: (
      dragged: { type: string; id: number },
      target: { type: string; id: number },
      rootGroups: GroupWithLayers[]
    ) => {
      // Prevent group-to-group drops on descendants
      if (dragged.type === 'group' && target.type === 'group') {
        if (isDescendant(rootGroups, dragged.id, target.id)) {
          return { allowed: false, reason: 'Cannot drop a group on its descendant' };
        }
      }
      // Prevent group-to-layer drops
      if (dragged.type === 'group' && target.type === 'layer') {
        return { allowed: false, reason: 'Cannot drop a group on a layer' };
      }
      return undefined;
    }
  };

  function buildNestedGroups(
    groups: Group[],
    layers: LayerWithAssociation[],
    parentId: number | null = null,
    depth: number = 0
  ): GroupWithLayers[] {
    const childGroups = groups.filter((group) => group.parent_id === parentId);

    return childGroups
      .sort((a, b) => a.sort_order - b.sort_order)
      .map((group) => {
        const groupLayers = layers
          .filter((layer) => layer.group_id === group.id)
          .sort((a, b) => a.sort_order - b.sort_order);

        const subgroups = buildNestedGroups(groups, layers, group.id, depth + 1);

        return {
          ...group,
          depth,
          layers: groupLayers,
          subgroups
        };
      });
  }

  function getAllGroupIds(groups: GroupWithLayers[]): number[] {
    const ids: number[] = [];
    for (const group of groups) {
      ids.push(group.id);
      ids.push(...getAllGroupIds(group.subgroups));
    }
    return ids;
  }

  function toggleGroup(groupId: number) {
    if (expandedGroups.has(groupId)) {
      expandedGroups.delete(groupId);
    } else {
      expandedGroups.add(groupId);
    }
    expandedGroups = new Set(expandedGroups);
  }

  function toggleDefault(layerId: number) {
    // Update in layersWithDetails
    const layer = layersWithDetails.find((l) => l.layer_id === layerId);
    if (layer) {
      layer.is_default = !layer.is_default;
    }
    // Update in ungroupedLayers
    const ungrouped = ungroupedLayers.find((l) => l.layer_id === layerId);
    if (ungrouped) {
      ungrouped.is_default = layer?.is_default ?? false;
    }
    // Update in all group layers
    function updateInGroups(groups: GroupWithLayers[]) {
      for (const group of groups) {
        const groupLayer = group.layers.find((l) => l.layer_id === layerId);
        if (groupLayer) groupLayer.is_default = layer?.is_default ?? false;
        updateInGroups(group.subgroups);
      }
    }
    updateInGroups(rootGroups);

    hasChanges = true;
    // Force reactivity
    layersWithDetails = [...layersWithDetails];
    ungroupedLayers = [...ungroupedLayers];
    rootGroups = [...rootGroups];
  }

  function findGroupById(groups: GroupWithLayers[], id: number): GroupWithLayers | null {
    for (const group of groups) {
      if (group.id === id) return group;
      const found = findGroupById(group.subgroups, id);
      if (found) return found;
    }
    return null;
  }

  function handleEmptyStateDrop(e: DragEvent) {
    e.preventDefault();
    
    // Handle existing layers being moved from groups to ungrouped FIRST
    if (draggedItem && draggedItem.type === 'layer') {
      const layerId = draggedItem.id;
      const sourceGroupId = draggedItem.groupId;

      // Find and remove the layer from its current location (only if it's in a group)
      if (sourceGroupId !== null && sourceGroupId !== undefined) {
        let layer: LayerWithAssociation | undefined;
        const group = findGroupById(rootGroups, sourceGroupId);
        if (group) {
          const index = group.layers.findIndex((l) => l.layer_id === layerId);
          if (index !== -1) {
            layer = group.layers.splice(index, 1)[0];
          }
        }

        if (layer) {
          // Move the layer to ungrouped
          layer.group_id = null;
          layer.sort_order = ungroupedLayers.length;
          ungroupedLayers.push(layer);

          // Update the layer in layersWithDetails as well
          const layerInDetails = layersWithDetails.find(l => l.layer_id === layerId);
          if (layerInDetails) {
            layerInDetails.group_id = null;
            layerInDetails.sort_order = ungroupedLayers.length - 1;
          }

          // Update arrays for reactivity
          ungroupedLayers = [...ungroupedLayers];
          rootGroups = [...rootGroups];
          layersWithDetails = [...layersWithDetails];
          
          // Update sort orders without rebuilding layersWithDetails
          updateLayerSortOrders(true);
          hasChanges = true;
        }
      }
    } 
    // Handle catalog layers from the catalog ONLY if no draggedItem or draggedItem is catalog-layer
    else if (draggedItem?.type === 'catalog-layer' || (!draggedItem && (window as any).catalogDragData)) {
      const dragData = (window as any).catalogDragData;
      if (dragData && dragData.type === 'catalog-layer' && dragData.layer) {
        const layer = dragData.layer as Layer;
        const existingLayer = allLayers.find(l => l.id === layer.id);
        if (existingLayer) {
          addLayerToDigitalTwin(existingLayer);
        }
      }
    }

    // Clean up
    draggedItem = null;
    if ((window as any).catalogDragData) {
      delete (window as any).catalogDragData;
    }
  }

  // catalogAddUtil.ts
  function addLayerToDigitalTwin(layer: Layer, groupId: number | null = null) {
    // Create new layer association
    const newLayerAssociation: LayerWithAssociation = {
      layer_id: layer.id,
      is_default: false,
      sort_order: groupId === null ? ungroupedLayers.length : 0,
      group_id: groupId,
      title: layer.title,
      beschrijving: layer.type || '',
      featureName: layer.featureName || '',
      isNew: true // Mark as new layer
    };

    if (groupId === null) {
      // Add to ungrouped layers
      ungroupedLayers.push(newLayerAssociation);
      ungroupedLayers = [...ungroupedLayers];
    } else {
      // Add to specific group
      const targetGroup = findGroupById(rootGroups, groupId);
      if (targetGroup) {
        newLayerAssociation.sort_order = targetGroup.layers.length;
        targetGroup.layers.push(newLayerAssociation);
        rootGroups = [...rootGroups];
      }
    }

    // Update main arrays
    layersWithDetails.push(newLayerAssociation);
    layersWithDetails = [...layersWithDetails];

    hasChanges = true;
  }

  function mapLayerToAssociation(layer: Layer, groupId: number | null, sortOrder: number): LayerWithAssociation {
    return {
      layer_id: layer.id,
      is_default: false,
      sort_order: sortOrder,
      group_id: groupId,
      title: layer.title,
      beschrijving: layer.type || '',
      featureName: layer.featureName || '',
      isNew: true
    };
  }

  function handleCatalogAddLayer(layer: Layer) {
    addCatalogItemToList(
      layer,
      null,
      ungroupedLayers,
      rootGroups,
      findGroupById,
      mapLayerToAssociation
    );
    // Update arrays for reactivity
    ungroupedLayers = [...ungroupedLayers];
    layersWithDetails = [...layersWithDetails, mapLayerToAssociation(layer, null, ungroupedLayers.length - 1)];
    rootGroups = [...rootGroups];
    hasChanges = true;
  }

  function handleDragOver(
    e: DragEvent,
    type: 'layer' | 'group',
    id: number,
    groupId?: number | null
  ) {
    e.preventDefault();

    // Try to parse catalog drag data if no draggedItem
    if (!draggedItem) {
      const dragData = e.dataTransfer?.getData('application/json');
      if (dragData) {
        try {
          const parsedData = JSON.parse(dragData);
          if (parsedData.type === 'catalog-layer') {
            draggedItem = parsedData;
          }
        } catch (err) {
          if ((window as any).catalogDragData) {
            draggedItem = (window as any).catalogDragData;
          }
        }
      } else if ((window as any).catalogDragData) {
        draggedItem = (window as any).catalogDragData;
      }
    }

    if (!draggedItem) return;

    const zone = getDropZone(e, e.currentTarget as HTMLElement);
    const target = { type, id, groupId, zone };
    const { allowed } = canDropGeneric(draggedItem, target, rootGroups, dropConfig);

    if (!allowed) {
      draggedOverItem = null;
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'none';
      return;
    }
    draggedOverItem = { type, id, groupId, zone };
  }

  function handleDragLeave() {
    draggedOverItem = null;
  }

  function handleDrop(
    e: DragEvent,
    dropType: 'layer' | 'group',
    dropId: number,
    dropGroupId?: number | null
  ) {
    e.preventDefault();

    // Try to get drag data if no draggedItem
    if (!draggedItem) {
      const dragData = e.dataTransfer?.getData('application/json');
      if (dragData) {
        try {
          draggedItem = JSON.parse(dragData);
        } catch (err) {
          if ((window as any).catalogDragData) {
            draggedItem = (window as any).catalogDragData;
          }
        }
      } else if ((window as any).catalogDragData) {
        draggedItem = (window as any).catalogDragData;
      }
    }

    if (!draggedItem || !draggedOverItem) return;

    const zone = draggedOverItem.zone;

    if (draggedItem.type === 'catalog-layer') {
      handleCatalogLayerDrop(dropType, dropId, dropGroupId, zone);
    } else if (draggedItem.type === 'layer') {
      handleLayerDrop(dropType, dropId, dropGroupId, zone);
    } else if (draggedItem.type === 'group') {
      handleGroupDrop(dropType, dropId, dropGroupId, zone);
    }

    draggedItem = null;
    draggedOverItem = null;

    // Clean up global fallback
    if ((window as any).catalogDragData) {
      delete (window as any).catalogDragData;
    }

    hasChanges = true;
  }

  function handleCatalogLayerDrop(
    dropType: string,
    dropId: number,
    dropGroupId: number | null | undefined,
    zone: string
  ) {
    if (!draggedItem || draggedItem.type !== 'catalog-layer' || !draggedItem.layer) return;

    const layer = draggedItem.layer;

    if (dropType === 'group' && zone === 'middle') {
      // Drop into group
      addLayerToDigitalTwin(layer, dropId);
    } else if (dropType === 'layer') {
      // Drop above or below another layer
      const targetGroupId = dropGroupId ?? null;
      const newLayerAssociation: LayerWithAssociation = {
        layer_id: layer.id,
        is_default: false,
        sort_order: 0,
        group_id: targetGroupId,
        title: layer.title,
        beschrijving: layer.type || '',
        featureName: layer.featureName || '',
        isNew: true // Mark as new layer
      };

      if (targetGroupId === null) {
        // Insert in ungrouped layers
        const targetIndex = ungroupedLayers.findIndex((l) => l.layer_id === dropId);
        const insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;
        ungroupedLayers.splice(insertIndex, 0, newLayerAssociation);
        ungroupedLayers = [...ungroupedLayers];
      } else {
        // Insert in group
        const targetGroup = findGroupById(rootGroups, targetGroupId);
        if (targetGroup) {
          const targetIndex = targetGroup.layers.findIndex((l) => l.layer_id === dropId);
          const insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;
          targetGroup.layers.splice(insertIndex, 0, newLayerAssociation);
          rootGroups = [...rootGroups];
        }
      }

      // Update main arrays
      layersWithDetails.push(newLayerAssociation);
      layersWithDetails = [...layersWithDetails];

      // Update sort orders
      updateLayerSortOrders();
    } else {
      // Default: add to ungrouped layers
      addLayerToDigitalTwin(layer, null);
    }
  }

  function handleLayerDrop(
    dropType: string,
    dropId: number,
    dropGroupId: number | null | undefined,
    zone: string
  ) {
    if (!draggedItem || draggedItem.type !== 'layer') return;

    const layerId = draggedItem.id;
    const sourceGroupId = draggedItem.groupId;

    // Find and remove the layer from its current location
    let layer: LayerWithAssociation | undefined;
    if (sourceGroupId === null || sourceGroupId === undefined) {
      const index = ungroupedLayers.findIndex((l) => l.layer_id === layerId);
      if (index !== -1) {
        layer = ungroupedLayers.splice(index, 1)[0];
      }
    } else {
      const group = findGroupById(rootGroups, sourceGroupId);
      if (group) {
        const index = group.layers.findIndex((l) => l.layer_id === layerId);
        if (index !== -1) {
          layer = group.layers.splice(index, 1)[0];
        }
      }
    }

    if (!layer) return;

    if (dropType === 'group' && zone === 'middle') {
      // Drop into group
      layer.group_id = dropId;
      const targetGroup = findGroupById(rootGroups, dropId);
      if (targetGroup) {
        targetGroup.layers.push(layer);
      }
    } else if (dropType === 'layer') {
      // Drop above or below another layer
      const targetGroupId = dropGroupId ?? null;
      layer.group_id = targetGroupId;

      if (targetGroupId === null) {
        // Insert in ungrouped layers
        const targetIndex = ungroupedLayers.findIndex((l) => l.layer_id === dropId);
        const insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;
        ungroupedLayers.splice(insertIndex, 0, layer);
      } else {
        // Insert in group
        const targetGroup = findGroupById(rootGroups, targetGroupId);
        if (targetGroup) {
          const targetIndex = targetGroup.layers.findIndex((l) => l.layer_id === dropId);
          const insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;
          targetGroup.layers.splice(insertIndex, 0, layer);
        }
      }
    }

    updateLayerSortOrders();
  }

  function updateLayerSortOrders(skipDetailsUpdate: boolean = false) {
    // Update ungrouped layers sort order
    ungroupedLayers.forEach((layer, index) => {
      layer.sort_order = index;
    });

    // Update grouped layers sort order recursively
    function updateGroupLayerSortOrders(groups: GroupWithLayers[]) {
      groups.forEach((group) => {
        group.layers.forEach((layer, index) => {
          layer.sort_order = index;
        });
        updateGroupLayerSortOrders(group.subgroups);
      });
    }

    updateGroupLayerSortOrders(rootGroups);

    // Update main arrays only if not skipped
    if (!skipDetailsUpdate) {
      updateLayersWithDetails();
    }

    // Force reactivity
    ungroupedLayers = [...ungroupedLayers];
    rootGroups = [...rootGroups];
  }

  // Function to handle dropping groups with drag and drop
  function handleGroupDrop(
    dropType: string,
    dropId: number,
    dropGroupId: number | null | undefined,
    zone: string
  ) {
    if (!draggedItem || draggedItem.type !== 'group') return;

    const groupId = draggedItem.id;

    // Find and remove the dragged group from its current location
    let draggedGroup: GroupWithLayers | undefined;

    function removeGroupFromParent(groups: GroupWithLayers[]): boolean {
      const index = groups.findIndex((g) => g.id === groupId);
      if (index !== -1) {
        draggedGroup = groups.splice(index, 1)[0];
        return true;
      }
      for (const group of groups) {
        if (removeGroupFromParent(group.subgroups)) return true;
      }
      return false;
    }

    // Remove from current location
    const removed = removeGroupFromParent(rootGroups);
    if (!removed || !draggedGroup) {
      console.error('Could not find dragged group to remove');
      return;
    }

    // Handle the drop based on type and zone
    if (dropType === 'group') {
      if (zone === 'middle') {
        // Drop INTO target group as a subgroup
        const targetGroup = findGroupById(rootGroups, dropId);
        if (targetGroup) {
          draggedGroup.parent_id = targetGroup.id;
          draggedGroup.depth = targetGroup.depth + 1;
          targetGroup.subgroups.push(draggedGroup);
        }
      } else if (zone === 'top' || zone === 'bottom') {
        // Drop ABOVE or BELOW target group (as sibling)
        const targetGroup = findGroupById(rootGroups, dropId);
        if (!targetGroup) {
          console.error('Could not find target group');
          return;
        }

        const parentGroupId = targetGroup.parent_id;
        let siblings: GroupWithLayers[];
        if (parentGroupId === null) {
          // Dropping as a root group
          siblings = rootGroups;
          draggedGroup.parent_id = null;
          draggedGroup.depth = 0;
        } else {
          const parentGroup = findGroupById(rootGroups, parentGroupId);
          if (!parentGroup) {
            console.error('Could not find parent group');
            return;
          }
          siblings = parentGroup.subgroups;
          // Set the dragged group's parent and depth
          draggedGroup.parent_id = parentGroupId;
          draggedGroup.depth =
            parentGroupId === null ? 0 : (findGroupById(rootGroups, parentGroupId)?.depth ?? 0) + 1;
        }

        // Find target index and insert
        const targetIndex = siblings.findIndex((g) => g.id === dropId);
        if (targetIndex === -1) {
          console.error('Could not find target group in siblings');
          return;
        }

        const insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;
        siblings.splice(insertIndex, 0, draggedGroup);
      }
    }

    // Update depths of all subgroups recursively
    function updateDepths(group: GroupWithLayers, newDepth: number) {
      group.depth = newDepth;
      group.subgroups.forEach((sub) => updateDepths(sub, newDepth + 1));
    }
    updateDepths(draggedGroup, draggedGroup.depth);

    // Update sort orders
    updateGroupSortOrders(rootGroups);

    // Force reactivity
    rootGroups = [...rootGroups];
  }
  
  function updateGroupSortOrders(groups: GroupWithLayers[]) {
    groups.forEach((group, index) => {
      group.sort_order = index;
      updateGroupSortOrders(group.subgroups);
    });
  }

  function updateLayersWithDetails() {
    const allUpdatedLayers: LayerWithAssociation[] = [];

    // Add ungrouped layers
    allUpdatedLayers.push(...ungroupedLayers);

    // Add grouped layers recursively
    function collectGroupLayers(groups: GroupWithLayers[]) {
      groups.forEach((group) => {
        allUpdatedLayers.push(...group.layers);
        collectGroupLayers(group.subgroups);
      });
    }

    collectGroupLayers(rootGroups);

    layersWithDetails = allUpdatedLayers;
    groupedLayers = allUpdatedLayers.filter((layer) => layer.group_id !== null);
  }

  function getDropIndicatorStyle(type: 'layer' | 'group', id: number, groupId?: number | null) {
    if (!draggedOverItem || draggedOverItem.type !== type || draggedOverItem.id !== id) {
      return { show: false, zone: null };
    }

    return { show: true, zone: draggedOverItem.zone };
  }

  // Save changes to the API
  async function saveChanges() {
    if (!hasChanges) return;

    isSaving = true;
    try {
      // Collect layer operations
      const layerOperations: LayerBulkOperation[] = [];

      // Ungrouped layers
      ungroupedLayers.forEach((layer) => {
        layerOperations.push({
          action: layer.isNew ? 'create' : 'update',
          layer_id: layer.layer_id,
          is_default: layer.is_default,
          sort_order: layer.sort_order,
          group_id: null
        });
      });

      // Grouped layers (recursive)
      function collectGroupLayers(groups: GroupWithLayers[]) {
        groups.forEach((group) => {
          group.layers.forEach((layer) => {
            layerOperations.push({
              action: layer.isNew ? 'create' : 'update',
              layer_id: layer.layer_id,
              is_default: layer.is_default,
              sort_order: layer.sort_order,
              group_id: group.id
            });
          });
          collectGroupLayers(group.subgroups);
        });
      }
      collectGroupLayers(rootGroups);

      // Add deleted layers
      if (window._deletedLayerIds && Array.isArray(window._deletedLayerIds)) {
        for (const deletedId of window._deletedLayerIds) {
          layerOperations.push({
            action: 'delete',
            layer_id: deletedId
          } as LayerBulkOperation);
        }
      }

      // Collect group operations
      const groupOperations: GroupBulkOperation[] = [];

      function collectGroupOperations(groups: GroupWithLayers[]): void {
        groups.forEach((group) => {
          groupOperations.push({
            action: 'update',
            id: group.id,
            title: group.title,
            parent_id: group.parent_id,
            sort_order: group.sort_order,
            digital_twin_id: group.digital_twin_id
          });

          if ('subgroups' in group && Array.isArray((group as any).subgroups)) {
            collectGroupOperations((group as any).subgroups);
          }
        });
      }

      collectGroupOperations(rootGroups);

      // Add deleted groups
      if (window._deletedGroupIds && Array.isArray(window._deletedGroupIds)) {
        for (const deletedGroupId of window._deletedGroupIds) {
          groupOperations.push({
            action: 'delete',
            id: deletedGroupId
          } as GroupBulkOperation);
        }
      }

      // Compose full payload to match backend
      const payload: BulkAssociationsPayload = {
        layer_payload: { operations: layerOperations },
        group_payload: { operations: groupOperations }
      };

      // Call the combined bulk update API
      await bulkUpdateDigitalTwinAssociations(digitalTwinId, payload);

      // After successful save, mark all layers as no longer new
      function markLayersAsExisting(layers: LayerWithAssociation[]) {
        layers.forEach((layer) => {
          layer.isNew = false;
        });
      }
      markLayersAsExisting(ungroupedLayers);

      function markGroupLayersAsExisting(groups: GroupWithLayers[]) {
        groups.forEach((group) => {
          markLayersAsExisting(group.layers);
          markGroupLayersAsExisting(group.subgroups);
        });
      }
      markGroupLayersAsExisting(rootGroups);

      // Clear deleted layer IDs after successful save
      if (window._deletedLayerIds) {
        window._deletedLayerIds = [];
      }

      // Clear deleted group IDs after successful save
      if (window._deletedGroupIds) {
        window._deletedGroupIds = [];
      }

      hasChanges = false;
      originalData = deepClone({ ungroupedLayers, rootGroups });

      await fetchAllData();
      successBanner?.show();
    } catch (error) {
      console.error('Failed to save changes:', error);
      errorBanner?.show();
    } finally {
      isSaving = false;
    }
  }

  function startEditGroupTitle(group: GroupWithLayers) {
    editingGroupId = group.id;
    editingGroupTitle = group.title;
  }

  function finishEditGroupTitle(group: GroupWithLayers) {
    if (editingGroupTitle.trim() !== '') {
      group.title = editingGroupTitle.trim();
      hasChanges = true;
    }
    editingGroupId = null;
    editingGroupTitle = '';
  }

  // Reset changes
  function resetChanges() {
    ungroupedLayers = deepClone(originalData.ungroupedLayers);
    rootGroups = deepClone(originalData.rootGroups);
    updateLayersWithDetails();
    hasChanges = false;
  }

  function confirmDeleteLayer(layer: LayerWithAssociation) {
    layerToDelete = layer;
    if (sessionStorage.getItem('skipDeleteLayerConfirm') === 'true') {
      actuallyDeleteLayer(layer);
    } else {
      deleteLayerModalShow = true;
    }
  }

  async function actuallyDeleteLayer(layer: LayerWithAssociation) {
    // Remove from layersWithDetails
    layersWithDetails = layersWithDetails.filter(l => l.layer_id !== layer.layer_id);

    // Remove from ungroupedLayers or rootGroups
    if (layer.group_id === null) {
      ungroupedLayers = ungroupedLayers.filter(l => l.layer_id !== layer.layer_id);
    } else {
      // Remove from group
      function removeLayerFromGroup(groups: GroupWithLayers[]) {
        groups.forEach(group => {
          group.layers = group.layers.filter(l => l.layer_id !== layer.layer_id);
          removeLayerFromGroup(group.subgroups);
        });
      }
      removeLayerFromGroup(rootGroups);
    }

    // Track deleted layer for bulk API call (only if it's not a new layer)
    if (!layer.isNew) {
      if (!window._deletedLayerIds) {
        window._deletedLayerIds = [];
      }
      window._deletedLayerIds.push(layer.layer_id);
    }

    // Update main arrays
    layersWithDetails = [...layersWithDetails];
    ungroupedLayers = [...ungroupedLayers];
    rootGroups = [...rootGroups];

    hasChanges = true;
  }

  function handleDeleteLayerModalConfirm(detail: { doNotAskAgain: boolean }) {
    if (layerToDelete) {
      actuallyDeleteLayer(layerToDelete);
      if (detail.doNotAskAgain) {
        skipDeleteLayerConfirm = true;
        sessionStorage.setItem('skipDeleteLayerConfirm', 'true');
      }
    }
    deleteLayerModalShow = false;
    layerToDelete = null;
  }

  function handleDeleteLayerModalCancel() {
    deleteLayerModalShow = false;
    layerToDelete = null;
  }

  function confirmDeleteGroup(group: GroupWithLayers) {
    groupToDelete = group;
    deleteGroupOption = 'delete';
    deleteGroupModalShow = true;
  }

  function handleDeleteGroupModalConfirm(option: 'delete' | 'move') {
    if (!groupToDelete) {
      deleteGroupModalShow = false;
      return;
    }
    const group = groupToDelete;

    // Remove group from rootGroups
    rootGroups = rootGroups.filter((g) => g.id !== group.id);

    // Remove group from all subgroups
    function removeGroupFromSubgroups(groups: GroupWithLayers[]) {
      groups.forEach((g) => {
        g.subgroups = g.subgroups.filter((sg) => sg.id !== group.id);
        removeGroupFromSubgroups(g.subgroups);
      });
    }
    removeGroupFromSubgroups(rootGroups);

    // Handle layers in the group
    function collectAllLayers(groups: GroupWithLayers[]): LayerWithAssociation[] {
      let result: LayerWithAssociation[] = [];
      for (const g of groups) {
        result = result.concat(g.layers);
        result = result.concat(collectAllLayers(g.subgroups));
      }
      return result;
    }
    const layersInGroup = group.layers.concat(collectAllLayers(group.subgroups));

    if (option === 'delete') {
      // Remove from all arrays and mark for deletion
      if (!window._deletedLayerIds) window._deletedLayerIds = [];
      window._deletedLayerIds.push(...layersInGroup.map(l => l.layer_id));
      layersWithDetails = layersWithDetails.filter(l => !layersInGroup.some(g => g.layer_id === l.layer_id));
      ungroupedLayers = ungroupedLayers.filter(l => !layersInGroup.some(g => g.layer_id === l.layer_id));
    } else if (option === 'move') {
      // Move all layers to ungrouped
      layersInGroup.forEach(l => {
        l.group_id = null;
        if (!ungroupedLayers.some(u => u.layer_id === l.layer_id)) {
          ungroupedLayers.push(l);
        }
      });
      // Remove from all group arrays
      function removeLayersFromGroups(groups: GroupWithLayers[]) {
        for (const g of groups) {
          g.layers = g.layers.filter(l => !layersInGroup.some(gl => gl.layer_id === l.layer_id));
          removeLayersFromGroups(g.subgroups);
        }
      }
      removeLayersFromGroups(rootGroups);
    }

    // Track deleted group for bulk API call
    if (!window._deletedGroupIds) window._deletedGroupIds = [];
    window._deletedGroupIds.push(group.id);

    // Update main arrays
    layersWithDetails = [...layersWithDetails];
    ungroupedLayers = [...ungroupedLayers];
    rootGroups = [...rootGroups];

    hasChanges = true;
    deleteGroupModalShow = false;
    groupToDelete = null;
  }

  function handleDeleteGroupModalCancel() {
    deleteGroupModalShow = false;
    groupToDelete = null;
  }

  function handleGroupCreated(newGroup: Group) {
    allGroups = [...allGroups, newGroup];

    if (newGroup.parent_id == null) {
      // Find max sort_order among root groups
      const maxSortOrder = rootGroups.length > 0
        ? Math.max(...rootGroups.map(g => g.sort_order ?? 0))
        : -1;
      const groupWithOrder = {
        ...newGroup,
        sort_order: maxSortOrder + 1,
        depth: 0,
        layers: [],
        subgroups: []
      };
      rootGroups = [...rootGroups, groupWithOrder];
    } else {
      // Find parent and add as subgroup
      const parent = findGroupById(rootGroups, newGroup.parent_id);
      if (parent) {
        // Find max sort_order among subgroups
        const maxSortOrder = parent.subgroups.length > 0
          ? Math.max(...parent.subgroups.map(g => g.sort_order ?? 0))
          : -1;
        const groupWithOrder = {
          ...newGroup,
          sort_order: maxSortOrder + 1,
          depth: (parent.depth ?? 0) + 1,
          layers: [],
          subgroups: []
        };
        parent.subgroups = [...parent.subgroups, groupWithOrder];
        rootGroups = [...rootGroups];
      }
    }
    hasChanges = true;
  }

  function handleLayerCreated(event: CustomEvent<Layer>) {
    const newLayer = event.detail;
    // Refresh the catalog to include the new layer
    allLayers = [...allLayers, newLayer];
    catalogLayers = [...catalogLayers, newLayer];
  }
</script>

<GroupModal
  bind:this={groupModalRef}
  availableGroups={allGroups}
  digitalTwinId={Number(digitalTwinId)}
  on:created={(event) => handleGroupCreated(event.detail)}
/>

<CreateLayerModal
  bind:this={createLayerModalRef}
  on:created={handleLayerCreated}
  isBackgroundPage={false}
/>

<DeleteModal
  show={deleteLayerModalShow}
  title="Laag verwijderen"
  message="Weet je zeker dat je deze laag wilt verwijderen uit de digital twin?"
  confirmLabel="Verwijder"
  cancelLabel="Annuleer"
  showCheckbox={true}
  checkboxLabel="Niet meer vragen deze sessie"
  onconfirm={handleDeleteLayerModalConfirm}
  oncancel={handleDeleteLayerModalCancel}
/>

<DeleteGroupModal
  show={deleteGroupModalShow}
  groupTitle={groupToDelete?.title ?? ''}
  layerCount={groupToDelete ? getTotalLayersInGroup(groupToDelete) : 0}
  ondelete={handleDeleteGroupModalConfirm}
  oncancel={handleDeleteGroupModalCancel}
/>

<div class="flex h-full gap-4">
  <!-- Layer Catalog -->
  <div class="w-1/3">
    <div class="bg-base-100 border-base-300 h-full rounded-lg border p-4">
      <div class="space-y-4">
        <!-- Header -->
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold">Feature Lagen Catalogus</h3>
            <p class="text-base-content/70 text-sm">
              Sleep lagen naar de digital twin of klik op + om toe te voegen
            </p>
          </div>
          <button
            class="btn btn-primary btn-sm"
            onclick={() => createLayerModalRef.showModal()}
            title="Nieuwe layer aanmaken"
          >
            <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
            Nieuwe Feature Laag
          </button>
        </div>

        <!-- Search -->
        <div class="relative">
          <img src="/icons/search.svg" alt="Zoeken" class="text-base-content/50 absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 transform" />
          <input
            type="text"
            placeholder="Zoek lagen..."
            class="input input-bordered input-sm w-full pl-10"
            bind:value={catalogSearchTerm}
          />
        </div>

        <!-- Layer List -->
        <div class="max-h-96 space-y-1 overflow-y-auto">
          {#if catalogIsLoading}
            <div class="flex items-center justify-center py-8">
              <span class="loading loading-spinner loading-sm"></span>
              <span class="ml-2 text-sm">Laden...</span>
            </div>
          {:else if catalogError}
            <div class="alert alert-error alert-sm">
              <span class="text-sm">{catalogError}</span>
            </div>
          {:else if filteredCatalogLayers.length === 0}
            <div class="text-base-content/50 py-8 text-center">
              <img src="/icons/file.svg" alt="Geen lagen" class="mx-auto mb-2 h-8 w-8 opacity-50" />
              <p class="text-sm">
                {catalogSearchTerm
                  ? 'Geen lagen gevonden voor deze zoekopdracht'
                  : 'Alle beschikbare lagen zijn al toegevoegd'}
              </p>
            </div>
          {:else}
            {#each filteredCatalogLayers as layer}
              <div
                class="hover:bg-base-200 hover:border-base-300 group flex cursor-move items-center gap-2 rounded border border-transparent px-3 py-2 text-sm transition-colors"
                use:dragStartAction={{
                  item: { type: 'catalog-layer' as 'catalog-layer', id: layer.id, layer },
                  type: 'catalog-layer' as 'catalog-layer',
                  dataKey: 'application/json',
                  effectAllowed: 'copy',
                  globalKey: 'catalogDragData',
                  onDragStart: (item) => {
                    console.log('Dragging:', item);
                    draggedItem = item;
                  }
                }}
                draggable="true"
                role="listitem"
              >
                <img src="/icons/file-catalog.svg" alt="Laag" class="h-4 w-4 flex-shrink-0" />
                <div class="min-w-0 flex-1">
                  <div class="truncate font-medium">{layer.title}</div>
                  {#if layer.type}
                    <div class="text-base-content/60 truncate text-xs">{layer.type}</div>
                  {/if}
                </div>
                <button
                  class="btn btn-ghost btn-xs opacity-0 transition-opacity group-hover:opacity-100 hover:opacity-100"
                  onclick={(e) => {
                    e.stopPropagation();
                    handleCatalogAddLayer(layer);
                  }}
                  onmousedown={(e) => e.stopPropagation()}
                  title="Voeg toe aan digital twin"
                >
                  <img src="/icons/plus.svg" alt="Voeg toe" class="h-3 w-3" />
                </button>
              </div>
            {/each}
          {/if}
        </div>

        <!-- Stats -->
        {#if !catalogIsLoading && !catalogError}
          <div class="text-base-content/50 border-base-300 border-t pt-2 text-xs">
            {filteredCatalogLayers.length} beschikbare lagen
            {#if usedLayerIds.length > 0}
              • {usedLayerIds.length} al toegevoegd
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Feature Layers -->
  <div class="flex-1">
    <AlertBanner
      bind:this={successBanner}
      type="success"
      message="Layer volgorde succesvol opgeslagen!"
    />
    <AlertBanner
      bind:this={errorBanner}
      type="error"
      message="Fout bij het opslaan van wijzigingen."
    />

    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold">Feature Lagen</h2>
          <p class="text-base-content/70 text-sm">
            Sleep lagen om ze te herordenen en tussen groepen te verplaatsen
          </p>
        </div>

        {#if hasChanges}
          <div class="flex gap-2">
            <button class="btn btn-ghost btn-sm" onclick={resetChanges} disabled={isSaving}>
              <img src="/icons/rotate-ccw.svg" alt="Reset" class="h-4 w-4" />
              Reset
            </button>
            <button class="btn btn-primary btn-sm" onclick={saveChanges} disabled={isSaving}>
              {#if isSaving}
                <span class="loading loading-spinner loading-xs"></span>
              {:else}
                <img src="/icons/save.svg" alt="Opslaan" class="h-4 w-4" />
              {/if}
              Opslaan
            </button>
            <button
              class="btn btn-outline btn-sm ml-2"
              type="button"
              onclick={() => console.log('Associated layers:', layersWithDetails)}
            >
              Debug: Log associated layers
            </button>
          </div>
        {/if}
      </div>

      <div class="bg-base-100 border-base-300 rounded-lg border p-4">
        <!-- Make this div scrollable -->
        <div class="space-y-4 h-[calc(100vh-200px)] overflow-y-auto">
          <!-- Nested Structure -->
          <div class="space-y-1">
            <!-- Ungrouped Layers -->
            <div class="mb-4">
              <h3 class="text-base-content/80 mb-2 flex items-center gap-2 text-sm font-semibold">
                <img src="/icons/file.svg" alt="Laag" class="h-4 w-4" />
                Ongegroepeerde Lagen ({ungroupedLayers.length})
              </h3>
              <div class="ml-6 space-y-1">
                {#each ungroupedLayers as layer}
                  <div
                    use:dragStartAction={{
                      item: { type: 'layer' as 'layer', id: layer.layer_id, groupId: layer.group_id ?? null },
                      type: 'layer' as 'layer',
                      dataKey: 'application/json',
                      effectAllowed: 'move',
                      onDragStart: (item) => { draggedItem = item; }
                    }}
                    class="relative"
                    draggable="true"
                  >
                    <div
                      class="hover:bg-base-200 flex cursor-move items-center gap-2 rounded px-2 py-1 text-sm {draggedItem?.type ===
                        'layer' && draggedItem?.id === layer.layer_id
                        ? 'opacity-50'
                        : ''}"
                      ondragover={(e) => handleDragOver(e, 'layer', layer.layer_id, null)}
                      ondragleave={handleDragLeave}
                      ondrop={(e) => handleDrop(e, 'layer', layer.layer_id, null)}
                      role="listitem"
                    >
                      <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                      <img src="/icons/file-ungrouped.svg" alt="Laag" class="h-4 w-4 flex-shrink-0" />
                      <span class="flex-1">
                        <span class="font-medium">{layer.title}</span>
                        {#if layer.isNew}
                          <span class="badge badge-success badge-xs ml-2">nieuw</span>
                        {/if}
                        {#if layer.is_default}
                          <span class="badge badge-info badge-xs ml-2">Standaard</span>
                        {/if}
                      </span>
                      <span class="text-base-content/50 text-xs">#{layer.sort_order}</span>
                      <button
                        class="btn btn-sm btn-circle"
                        class:btn-secondary={layer.is_default}
                        class:btn-outline={!layer.is_default}
                        onclick={() => toggleDefault(layer.layer_id)}
                        title={layer.is_default ? 'Standaard laag' : 'Instellen als standaard'}
                        aria-label={layer.is_default ? 'Standaard laag' : 'Instellen als standaard'}
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                      <button
                        class="btn btn-ghost btn-xs"
                        onclick={() => confirmDeleteLayer(layer)}
                        title="Verwijder laag"
                        aria-label="Verwijder laag"
                      >
                        <img src="/icons/trash-2.svg" alt="Verwijder laag" class="h-5 w-5" />
                      </button>
                    </div>

                    <!-- Absolute positioned drop indicators -->
                    {#if getDropIndicatorStyle('layer', layer.layer_id, null).show}
                      {@const indicator = getDropIndicatorStyle('layer', layer.layer_id, null)}
                      {#if indicator.zone === 'top'}
                        <div
                          class="bg-primary absolute top-0 right-0 left-0 z-10 h-1 -translate-y-0.5 rounded-full"
                        ></div>
                      {:else if indicator.zone === 'bottom'}
                        <div
                          class="bg-primary absolute right-0 bottom-0 left-0 z-10 h-1 translate-y-0.5 rounded-full"
                        ></div>
                      {:else if indicator.zone === 'middle'}
                        <div
                          class="border-primary bg-primary/10 pointer-events-none absolute inset-0 z-10 rounded border-2"
                        ></div>
                      {/if}
                    {/if}
                  </div>
                {/each}
              </div>

              <!-- Empty state for ungrouped layers -->
              {#if ungroupedLayers.length === 0}
                <div class="ml-6">
                  <div 
                    class="border-2 border-dashed border-base-300 rounded-lg p-6 text-center text-base-content/50 transition-colors {(draggedItem?.type === 'layer' && draggedItem?.groupId !== null) || draggedItem?.type === 'catalog-layer' ? 'border-primary bg-primary/5' : ''}"
                    role="region"
                    ondragover={(e) => {
                      e.preventDefault();
                      // draggedItem should already be set by dragStartAction for existing layers
                      // Only try to set it if it's not already set (for catalog items)
                      if (!draggedItem) {
                        const dragData = e.dataTransfer?.getData('application/json');
                        if (dragData) {
                          try {
                            draggedItem = JSON.parse(dragData);
                          } catch (err) {
                            // Ignore parse errors
                          }
                        } else if ((window as any).catalogDragData) {
                          draggedItem = (window as any).catalogDragData;
                        }
                      }
                    }}
                    ondrop={handleEmptyStateDrop}
                  >
                    <img src="/icons/file.svg" alt="Geen lagen" class="mx-auto mb-3 h-10 w-10 opacity-50" />
                    <h4 class="text-base font-medium mb-2">Geen ongegroepeerde lagen</h4>
                    <p class="mb-3 text-sm">Sleep lagen vanuit de catalogus hiernaartoe om ze toe te voegen.</p>
                    <div class="inline-flex items-center gap-2 text-xs text-base-content/40">
                      Sleep & laat los
                    </div>
                  </div>
                </div>
              {/if}
            </div>

            <!-- Root Groups -->
            <div class="mb-4">
              <h3 class="text-base-content/80 mb-2 flex items-center gap-2 text-sm font-semibold">
                <img src="/icons/folder-group.svg" alt="Map" class="h-4 w-4" />
                Groepen ({rootGroups.length})
                <button
                  class="btn btn-sm btn-outline mb-2"
                  onclick={() => groupModalRef.showModal()}
                  disabled={isSaving}
                >
                <img src="/icons/plus.svg" alt="Nieuwe groep" class="mr-1 h-4 w-4" />
                  Nieuwe groep
                </button>
              </h3>
              {#each rootGroups as group}
                {@render groupComponent(group)}
              {/each}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

{#snippet groupComponent(group: GroupWithLayers)}
  <div class="space-y-1" style="margin-left: {group.depth * 1.5}rem;" role="group">
    <!-- Group Header with relative positioning -->
    <div class="relative">
      <div
        class="hover:bg-base-200 flex items-center gap-2 rounded px-2 py-1 text-sm"
        ondragover={(e) => handleDragOver(e, 'group', group.id)}
        ondragleave={handleDragLeave}
        ondrop={(e) => handleDrop(e, 'group', group.id)}
        draggable="true"
        use:dragStartAction={{
          item: { type: 'group' as 'group', id: group.id, group },
          type: 'group' as 'group',
          dataKey: 'application/json',
          effectAllowed: 'move',
          onDragStart: (item) => {
            console.log('Dragging:', item);
            draggedItem = item;
          }
        }}
        role="listitem"
      >
        <button
          class="btn btn-ghost btn-xs h-4 min-h-0 w-4 p-0"
          onclick={() => toggleGroup(group.id)}
        >
        {#if expandedGroups.has(group.id)}
          <img src="/icons/chevron-down.svg" alt="Expand" class="h-3 w-3" />
        {:else}
          <img src="/icons/chevron-right.svg" alt="Collapse" class="h-3 w-3" />
        {/if}
        </button>

        {#if expandedGroups.has(group.id)}
          <img src="/icons/folder-open-group.svg" alt="Folder open" class="h-4 w-4 flex-shrink-0 text-amber-600" />
        {:else}
          <img src="/icons/folder-group.svg" alt="Folder closed" class="h-4 w-4 flex-shrink-0 text-amber-600" />
        {/if}

        {#if editingGroupId === group.id}
          <input
            class="input input-xs input-bordered w-64 text-sm"
            bind:value={editingGroupTitle}
            onblur={() => finishEditGroupTitle(group)}
            onkeydown={(e) => e.key === 'Enter' && finishEditGroupTitle(group)}
          />
          <button
            class="btn btn-ghost btn-xs ml-1"
            title="Bevestigen"
            onclick={() => finishEditGroupTitle(group)}
            tabindex="-1"
            aria-label="Bevestig naam"
          >
            <img src="/icons/check.svg" alt="Opslaan" class="h-4 w-4" />
          </button>
          <button
            class="btn btn-ghost btn-xs ml-1"
            title="Annuleren"
            onclick={() => {
              editingGroupId = null;
              editingGroupTitle = '';
            }}
            tabindex="-1"
            aria-label="Annuleer naam wijzigen"
          >
            <img src="/icons/x.svg" alt="Annuleer" class="h-4 w-4" />
          </button>
        {:else}
          <span class="truncate font-medium">{group.title}</span>
          <button
            class="btn btn-ghost btn-xs ml-1"
            title="Naam wijzigen"
            onclick={() => startEditGroupTitle(group)}
            tabindex="-1"
            aria-label="Title wijzigen"
          >
            <img src="/icons/pencil.svg" alt="Wijzig groep naam" class="h-3 w-3" />
          </button>
          <button
            class="btn btn-ghost btn-xs ml-1"
            title="Verwijder groep"
            onclick={() => confirmDeleteGroup(group)}
            aria-label="Verwijder groep"
          >
            <img src="/icons/trash-2.svg" alt="Verwijder groep" class="h-4 w-4 text-error" />
          </button>
        {/if}
        <span class="text-base-content/50 text-xs">
          ({getTotalLayersInGroup(group)} lagen)
        </span>
      </div>

      <!-- Absolute positioned drop indicators for groups -->
      {#if getDropIndicatorStyle('group', group.id).show}
        {@const indicator = getDropIndicatorStyle('group', group.id)}
        {#if indicator.zone === 'top'}
          <div
            class="bg-primary absolute top-0 right-0 left-0 z-10 h-1 -translate-y-0.5 rounded-full"
          ></div>
        {:else if indicator.zone === 'bottom'}
          <div
            class="bg-primary absolute right-0 bottom-0 left-0 z-10 h-1 translate-y-0.5 rounded-full"
          ></div>
        {:else if indicator.zone === 'middle'}
          <div
            class="border-primary bg-primary/10 pointer-events-none absolute inset-0 z-10 rounded border-2"
          ></div>
        {/if}
      {/if}
    </div>

    <!-- Group Content (only if expanded) -->
    {#if expandedGroups.has(group.id)}
      <div class="space-y-1">
        <!-- Group Layers -->
        <div class="space-y-1">
          {#each group.layers as layer}
            <div class="relative">
              <div
                class="hover:bg-base-200 flex cursor-move items-center gap-2 rounded px-2 py-1 text-sm {draggedItem?.type ===
                  'layer' && draggedItem?.id === layer.layer_id
                  ? 'opacity-50'
                  : ''}"
                draggable="true"
                use:dragStartAction={{
                  item: { type: 'layer' as 'layer', id: layer.layer_id, groupId: group?.id },
                  type: 'layer' as 'layer',
                  dataKey: 'application/json',
                  effectAllowed: 'move',
                  onDragStart: (item) => {
                    console.log('Dragging:', item);
                    draggedItem = item;
                  }
                }}
                ondragover={(e) => handleDragOver(e, 'layer', layer.layer_id, group.id)}
                ondragleave={handleDragLeave}
                ondrop={(e) => handleDrop(e, 'layer', layer.layer_id, group.id)}
                role="listitem"
              >
                <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                <img src="/icons/file-grouped.svg" alt="File" class="h-4 w-4 flex-shrink-0" />
                <span class="flex-1">
                  <span class="font-medium">{layer.title}</span>
                  {#if layer.isNew}
                    <span class="badge badge-success badge-xs ml-2">nieuw</span>
                  {/if}
                  {#if layer.is_default}
                    <span class="badge badge-info badge-xs ml-2">Standaard</span>
                  {/if}
                </span>
                <span class="text-base-content/50 text-xs">#{layer.sort_order}</span>
                <button
                  class="btn btn-sm btn-circle"
                  class:btn-secondary={layer.is_default}
                  class:btn-outline={!layer.is_default}
                  onclick={() => toggleDefault(layer.layer_id)}
                  title={layer.is_default ? 'Standaard laag' : 'Instellen als standaard'}
                  aria-label={layer.is_default ? 'Standaard laag' : 'Instellen als standaard'}
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button
                  class="btn btn-ghost btn-xs"
                  onclick={() => confirmDeleteLayer(layer)}
                  title="Verwijder laag"
                  aria-label="Verwijder laag"
                >
                  <img src="/icons/trash-2.svg" alt="Trash" class="w-5 h-5 text-error" />
                </button>
              </div>

              <!-- Absolute positioned drop indicators for group layers -->
              {#if getDropIndicatorStyle('layer', layer.layer_id, group.id).show}
                {@const indicator = getDropIndicatorStyle('layer', layer.layer_id, group.id)}
                {#if indicator.zone === 'top'}
                  <div
                    class="bg-primary absolute top-0 right-0 left-0 z-10 h-1 -translate-y-0.5 rounded-full"
                  ></div>
                {:else if indicator.zone === 'bottom'}
                  <div
                    class="bg-primary absolute right-0 bottom-0 left-0 z-10 h-1 translate-y-0.5 rounded-full"
                  ></div>
                {:else if indicator.zone === 'middle'}
                  <div
                    class="border-primary bg-primary/10 pointer-events-none absolute inset-0 z-10 rounded border-2"
                  ></div>
                {/if}
              {/if}
            </div>
          {/each}
        </div>

        <!-- Nested Subgroups -->
        {#each group.subgroups as subgroup}
          {@render groupComponent(subgroup)}
        {/each}
      </div>
    {/if}
  </div>
{/snippet}
