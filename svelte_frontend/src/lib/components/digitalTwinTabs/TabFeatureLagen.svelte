<script lang="ts">
  import { onMount } from 'svelte';
  import { Folder, FolderOpen, File, Eye, EyeOff, ChevronDown, ChevronRight, Save, RotateCcw, GripVertical } from 'lucide-svelte';
  import { fetchLayers, fetchGroups, bulkUpdateDigitalTwinAssociations } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { LayerWithAssociation, GroupWithLayers, LayerBulkOperation, GroupBulkOperation, BulkAssociationsPayload } from '$lib/types/digitalTwinAssociation';
  import type { Layer } from '$lib/types/layer';
  import type { Group } from '$lib/types/group';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();
  
  // Deep clone function to replace structuredClone
  function deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
    if (obj instanceof Array) return obj.map(item => deepClone(item)) as unknown as T;
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
  let originalData: { ungroupedLayers: LayerWithAssociation[], rootGroups: GroupWithLayers[] } = { ungroupedLayers: [], rootGroups: [] };
  let isSaving = $state(false);

  // Drag and drop state
  let draggedItem = $state<{ type: 'layer' | 'group', id: number, groupId?: number | null } | null>(null);
  let draggedOverItem = $state<{ type: 'layer' | 'group', id: number, groupId?: number | null, zone: 'top' | 'middle' | 'bottom' } | null>(null);

  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  onMount(async () => {
    try {
      isLoading = true;
      
      // Fetch all data
      allLayers = await fetchLayers();
      allGroups = await fetchGroups(digitalTwinId);
      
      // Process layer associations if they exist
      if (digitalTwin?.layer_associations) {
        layersWithDetails = digitalTwin.layer_associations
          .sort((a, b) => a.sort_order - b.sort_order)
          .map((association) => {
            const layerDetails = allLayers.find((layer) => layer.id === association.layer_id);
            
            return {
              ...association,
              title: layerDetails?.title || `Layer ${association.layer_id}`,
              beschrijving: layerDetails?.type || '',
              featureName: layerDetails?.featureName || ''
            };
          });
        
        // Separate ungrouped and grouped layers
        ungroupedLayers = layersWithDetails.filter(layer => layer.group_id === null);
        groupedLayers = layersWithDetails.filter(layer => layer.group_id !== null);
        
        // Build nested group structure
        rootGroups = buildNestedGroups(allGroups, layersWithDetails);
        
        // Expand all groups by default
        expandedGroups = new Set(getAllGroupIds(rootGroups));
        
        // Store original state for reset functionality
        originalData = deepClone({ ungroupedLayers, rootGroups });
        
      } else {
        layersWithDetails = [];
        ungroupedLayers = [];
        groupedLayers = [];
        rootGroups = [];
      }
      
    } catch (err) {
      console.error('Failed to load data:', err);
      error = err instanceof Error ? err.message : 'Unknown error occurred';
    } finally {
      isLoading = false;
    }
  });

  function buildNestedGroups(groups: Group[], layers: LayerWithAssociation[], parentId: number | null = null, depth: number = 0): GroupWithLayers[] {
    const childGroups = groups.filter(group => group.parent_id === parentId);
    
    return childGroups
      .sort((a, b) => a.sort_order - b.sort_order)
      .map(group => {
        const groupLayers = layers
          .filter(layer => layer.group_id === group.id)
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
    const layer = layersWithDetails.find(l => l.layer_id === layerId);
    if (layer) {
      layer.is_default = !layer.is_default;
      hasChanges = true;
      // Force reactivity
      layersWithDetails = [...layersWithDetails];
    }
  }

  function getTotalLayersInGroup(group: GroupWithLayers): number {
    let total = group.layers.length;
    for (const subgroup of group.subgroups) {
      total += getTotalLayersInGroup(subgroup);
    }
    return total;
  }

  function findGroupById(groups: GroupWithLayers[], id: number): GroupWithLayers | null {
    for (const group of groups) {
      if (group.id === id) return group;
      const found = findGroupById(group.subgroups, id);
      if (found) return found;
    }
    return null;
  }

  // Drag and drop functions
  function handleDragStart(e: DragEvent, type: 'layer' | 'group', id: number, groupId?: number | null) {
    draggedItem = { type, id, groupId };
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', ''); // Required for Firefox
    }
  }

  function getDropZone(e: DragEvent, element: HTMLElement): 'top' | 'middle' | 'bottom' {
    const rect = element.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const height = rect.height;
    
    const topThreshold = height * 0.35;
    const bottomThreshold = height * 0.65;
    
    if (y < topThreshold) return 'top';
    if (y > bottomThreshold) return 'bottom';
    return 'middle';
  }

  function handleDragOver(e: DragEvent, type: 'layer' | 'group', id: number, groupId?: number | null) {
    e.preventDefault();
    
    if (!draggedItem) return;
    
    const zone = getDropZone(e, e.currentTarget as HTMLElement);
    
    // Don't allow dropping on itself
    if (draggedItem.type === type && draggedItem.id === id) {
      draggedOverItem = null;
      return;
    }

    // Prevent group-to-layer drops
    if (draggedItem.type === 'group' && type === 'layer') {
      draggedOverItem = null;
      return;
    }

    // For group-to-group drops, prevent ANY drop on descendants
    if (draggedItem.type === 'group' && type === 'group') {
      // Check if target is a descendant of dragged item
      if (isDescendantGroup(draggedItem.id, id)) {
        draggedOverItem = null;
        return;
      }
    }
    
    // Allow all zones for valid drops
    draggedOverItem = { type, id, groupId, zone };
  }

  function handleDragLeave() {
    draggedOverItem = null;
  }

  function handleDrop(e: DragEvent, dropType: 'layer' | 'group', dropId: number, dropGroupId?: number | null) {
    e.preventDefault();
    
    if (!draggedItem || !draggedOverItem) return;

    const zone = draggedOverItem.zone;

    if (draggedItem.type === 'layer') {
      handleLayerDrop(dropType, dropId, dropGroupId, zone);
    } else if (draggedItem.type === 'group') {
      handleGroupDrop(dropType, dropId, dropGroupId, zone);
    }

    draggedItem = null;
    draggedOverItem = null;
    hasChanges = true;
  }

  function handleLayerDrop(dropType: string, dropId: number, dropGroupId: number | null | undefined, zone: string) {
    if (!draggedItem || draggedItem.type !== 'layer') return;

    const layerId = draggedItem.id;
    const sourceGroupId = draggedItem.groupId;

    // Find and remove the layer from its current location
    let layer: LayerWithAssociation | undefined;
    if (sourceGroupId === null || sourceGroupId === undefined) {
      const index = ungroupedLayers.findIndex(l => l.layer_id === layerId);
      if (index !== -1) {
        layer = ungroupedLayers.splice(index, 1)[0];
      }
    } else {
      const group = findGroupById(rootGroups, sourceGroupId);
      if (group) {
        const index = group.layers.findIndex(l => l.layer_id === layerId);
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
        const targetIndex = ungroupedLayers.findIndex(l => l.layer_id === dropId);
        const insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;
        ungroupedLayers.splice(insertIndex, 0, layer);
      } else {
        // Insert in group
        const targetGroup = findGroupById(rootGroups, targetGroupId);
        if (targetGroup) {
          const targetIndex = targetGroup.layers.findIndex(l => l.layer_id === dropId);
          const insertIndex = zone === 'top' ? targetIndex : targetIndex + 1;
          targetGroup.layers.splice(insertIndex, 0, layer);
        }
      }
    }

    updateLayerSortOrders();
  }

  function updateLayerSortOrders() {
    // Update ungrouped layers sort order
    ungroupedLayers.forEach((layer, index) => {
      layer.sort_order = index;
    });

    // Update grouped layers sort order recursively
    function updateGroupLayerSortOrders(groups: GroupWithLayers[]) {
      groups.forEach(group => {
        group.layers.forEach((layer, index) => {
          layer.sort_order = index;
        });
        updateGroupLayerSortOrders(group.subgroups);
      });
    }

    updateGroupLayerSortOrders(rootGroups);
    
    // Update main arrays
    updateLayersWithDetails();
    
    // Force reactivity
    ungroupedLayers = [...ungroupedLayers];
    rootGroups = [...rootGroups];
  }

  // Function to handle dropping groups with drag and drop
  function handleGroupDrop(dropType: string, dropId: number, dropGroupId: number | null | undefined, zone: string) {
    if (!draggedItem || draggedItem.type !== 'group') return;

    const groupId = draggedItem.id;

    // Find and remove the dragged group from its current location
    let draggedGroup: GroupWithLayers | undefined;

    function removeGroupFromParent(groups: GroupWithLayers[]): boolean {
      const index = groups.findIndex(g => g.id === groupId);
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
        
        // Find the correct siblings array
        let siblings: GroupWithLayers[];
        if (parentGroupId === null) {
          siblings = rootGroups;
        } else {
          const parentGroup = findGroupById(rootGroups, parentGroupId);
          if (!parentGroup) {
            console.error('Could not find parent group');
            return;
          }
          siblings = parentGroup.subgroups;
        }

        // Set the dragged group's parent and depth
        draggedGroup.parent_id = parentGroupId;
        draggedGroup.depth = parentGroupId === null ? 0 : (findGroupById(rootGroups, parentGroupId)?.depth ?? 0) + 1;

        // Find target index and insert
        const targetIndex = siblings.findIndex(g => g.id === dropId);
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
      group.subgroups.forEach(sub => updateDepths(sub, newDepth + 1));
    }
    updateDepths(draggedGroup, draggedGroup.depth);

    // Update sort orders
    updateGroupSortOrders(rootGroups);

    // Force reactivity
    rootGroups = [...rootGroups];
  }

  function isDescendantGroup(draggedGroupId: number, targetGroupId: number): boolean {
  // Find the dragged group (the one being moved)
  const draggedGroup = findGroupById(rootGroups, draggedGroupId);
  if (!draggedGroup) return false;

  // Check if the target group is anywhere in the dragged group's subgroup tree
  function checkSubgroups(groups: GroupWithLayers[]): boolean {
    for (const group of groups) {
      if (group.id === targetGroupId) return true;
      if (checkSubgroups(group.subgroups)) return true;
    }
    return false;
  }

  return checkSubgroups(draggedGroup.subgroups);
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
      groups.forEach(group => {
        allUpdatedLayers.push(...group.layers);
        collectGroupLayers(group.subgroups);
      });
    }
    
    collectGroupLayers(rootGroups);
    
    layersWithDetails = allUpdatedLayers;
    groupedLayers = allUpdatedLayers.filter(layer => layer.group_id !== null);
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
      ungroupedLayers.forEach(layer => {
        layerOperations.push({
          action: "update",
          layer_id: layer.layer_id,
          is_default: layer.is_default,
          sort_order: layer.sort_order,
          group_id: null,
        });
      });

      // Grouped layers (recursive)
      function collectGroupLayers(groups: GroupWithLayers[]) {
        groups.forEach(group => {
          group.layers.forEach(layer => {
            layerOperations.push({
              action: "update",
              layer_id: layer.layer_id,
              is_default: layer.is_default,
              sort_order: layer.sort_order,
              group_id: group.id,
            });
          });
          collectGroupLayers(group.subgroups);
        });
      }
      collectGroupLayers(rootGroups);

      // Collect group operations 
      const groupOperations: GroupBulkOperation[] = [];

      function collectGroupOperations(groups: Group[]): void {
        groups.forEach(group => {
          groupOperations.push({
            action: "update",
            id: group.id,
            title: group.title,
            parent_id: group.parent_id,
            sort_order: group.sort_order,
            digital_twin_id: group.digital_twin_id,
          });

          if ('subgroups' in group && Array.isArray((group as any).subgroups)) {
            collectGroupOperations((group as any).subgroups);
          }
        });
      }
      
      collectGroupOperations(rootGroups);

      // Compose full payload to match backend
      const payload: BulkAssociationsPayload = {
        layer_payload: { operations: layerOperations },
        group_payload: { operations: groupOperations },
      };

      // Call the combined bulk update API
      await bulkUpdateDigitalTwinAssociations(digitalTwinId, payload);

      hasChanges = false;
      originalData = deepClone({ ungroupedLayers, rootGroups });

      successBanner?.show();
    } catch (error) {
      console.error('Failed to save changes:', error);
      errorBanner?.show();
    } finally {
      isSaving = false;
    }
  }

  // Reset changes
  function resetChanges() {
    ungroupedLayers = deepClone(originalData.ungroupedLayers);
    rootGroups = deepClone(originalData.rootGroups);
    updateLayersWithDetails();
    hasChanges = false;
  }
</script>

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
  <div class="flex justify-between items-center">
    <div>
      <h2 class="text-2xl font-bold">Feature Lagen</h2>
      <p class="text-sm text-base-content/70">Sleep lagen om ze te herordenen en tussen groepen te verplaatsen</p>
    </div>
    
    {#if hasChanges}
      <div class="flex gap-2">
        <button 
          class="btn btn-ghost btn-sm"
          onclick={resetChanges}
          disabled={isSaving}
        >
          <RotateCcw class="w-4 h-4" />
          Reset
        </button>
        <button 
          class="btn btn-primary btn-sm"
          onclick={saveChanges}
          disabled={isSaving}
        >
          {#if isSaving}
            <span class="loading loading-spinner loading-xs"></span>
          {:else}
            <Save class="w-4 h-4" />
          {/if}
          Opslaan
        </button>
      </div>
    {/if}
  </div>

  <div class="bg-base-100 border border-base-300 rounded-lg p-4">
    {#if isLoading}
      <div class="flex items-center justify-center py-8">
        <span class="loading loading-spinner loading-md"></span>
        <span class="ml-3">Laden...</span>
      </div>
    {:else if error}
      <div class="alert alert-error">
        <span>Fout bij het laden: {error}</span>
      </div>
    {:else}
      <div class="space-y-4">
        <!-- Nested Structure -->
        <div class="space-y-1">
          <!-- Ungrouped Layers -->
          {#if ungroupedLayers.length > 0}
            <div class="mb-4">
              <h3 class="text-sm font-semibold text-base-content/80 mb-2 flex items-center gap-2">
                <File class="w-4 h-4" />
                Ongegroepeerde Lagen ({ungroupedLayers.length})
              </h3>
              <div class="ml-6 space-y-1">
                {#each ungroupedLayers as layer}
                  <div class="relative">
                    <div
                      class="flex items-center gap-2 px-2 py-1 hover:bg-base-200 rounded text-sm cursor-move {draggedItem?.type === 'layer' && draggedItem?.id === layer.layer_id ? 'opacity-50' : ''}"
                      draggable="true"
                      ondragstart={(e) => handleDragStart(e, 'layer', layer.layer_id, null)}
                      ondragover={(e) => handleDragOver(e, 'layer', layer.layer_id, null)}
                      ondragleave={handleDragLeave}
                      ondrop={(e) => handleDrop(e, 'layer', layer.layer_id, null)}
                      role="listitem"
                    >
                      <GripVertical class="w-4 h-4 text-base-content/30 flex-shrink-0" />
                      <File class="w-4 h-4 text-blue-600 flex-shrink-0" />
                      <span class="flex-1">
                        <span class="font-medium">{layer.title}</span>
                        {#if layer.is_default}
                          <span class="badge badge-primary badge-xs ml-2">Standaard</span>
                        {/if}
                      </span>
                      <span class="text-xs text-base-content/50">#{layer.sort_order}</span>
                      <button
                        class="btn btn-ghost btn-xs"
                        onclick={() => toggleDefault(layer.layer_id)}
                        title={layer.is_default ? 'Verwijder van standaard' : 'Maak standaard'}
                      >
                        {#if layer.is_default}
                          <Eye class="w-3 h-3" />
                        {:else}
                          <EyeOff class="w-3 h-3" />
                        {/if}
                      </button>
                    </div>
                    
                    <!-- Absolute positioned drop indicators -->
                    {#if getDropIndicatorStyle('layer', layer.layer_id, null).show}
                      {@const indicator = getDropIndicatorStyle('layer', layer.layer_id, null)}
                      {#if indicator.zone === 'top'}
                        <div class="absolute top-0 left-0 right-0 h-1 bg-primary rounded-full -translate-y-0.5 z-10"></div>
                      {:else if indicator.zone === 'bottom'}
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-full translate-y-0.5 z-10"></div>
                      {:else if indicator.zone === 'middle'}
                        <div class="absolute inset-0 border-2 border-primary bg-primary/10 rounded z-10 pointer-events-none"></div>
                      {/if}
                    {/if}
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          <!-- Root Groups -->
          {#if rootGroups.length > 0}
            <div class="mb-4">
              <h3 class="text-sm font-semibold text-base-content/80 mb-2 flex items-center gap-2">
                <Folder class="w-4 h-4" />
                Groepen ({rootGroups.length})
              </h3>
              {#each rootGroups as group}
                {@render groupComponent(group)}
              {/each}
            </div>
          {/if}
          
          {#if ungroupedLayers.length === 0 && rootGroups.length === 0}
            <div class="text-center py-8 text-base-content/50">
              <p>Geen lagen gevonden voor deze digital twin.</p>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

{#snippet groupComponent(group: GroupWithLayers)}
<div class="space-y-1" style="margin-left: {group.depth * 1.5}rem;" role="group">
  <!-- Group Header with relative positioning -->
  <div class="relative">
    <div
      class="flex items-center gap-2 px-2 py-1 hover:bg-base-200 rounded text-sm"
      ondragover={(e) => handleDragOver(e, 'group', group.id)}
      ondragleave={handleDragLeave}
      ondrop={(e) => handleDrop(e, 'group', group.id)}
      draggable="true"
      ondragstart={(e) => handleDragStart(e, 'group', group.id, group.parent_id)}
      role="listitem"
    >
      <button
        class="btn btn-ghost btn-xs p-0 min-h-0 h-4 w-4"
        onclick={() => toggleGroup(group.id)}
      >
        {#if expandedGroups.has(group.id)}
          <ChevronDown class="w-3 h-3" />
        {:else}
          <ChevronRight class="w-3 h-3" />
        {/if}
      </button>

      {#if expandedGroups.has(group.id)}
        <FolderOpen class="w-4 h-4 text-amber-600 flex-shrink-0" />
      {:else}
        <Folder class="w-4 h-4 text-amber-600 flex-shrink-0" />
      {/if}

      <span class="font-medium truncate">{group.title}</span>
      <span class="text-xs text-base-content/50">
        ({getTotalLayersInGroup(group)} lagen)
      </span>
    </div>
    
    <!-- Absolute positioned drop indicators for groups -->
    {#if getDropIndicatorStyle('group', group.id).show}
      {@const indicator = getDropIndicatorStyle('group', group.id)}
      {#if indicator.zone === 'top'}
        <div class="absolute top-0 left-0 right-0 h-1 bg-primary rounded-full -translate-y-0.5 z-10"></div>
      {:else if indicator.zone === 'bottom'}
        <div class="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-full translate-y-0.5 z-10"></div>
      {:else if indicator.zone === 'middle'}
        <div class="absolute inset-0 border-2 border-primary bg-primary/10 rounded z-10 pointer-events-none"></div>
      {/if}
    {/if}
  </div>

  <!-- Group Content (only if expanded) -->
  {#if expandedGroups.has(group.id)}
    <div class="space-y-1">
      <!-- Group Layers -->
      {#if group.layers.length > 0}
        <div class="space-y-1">
          {#each group.layers as layer}
            <div class="relative">
              <div
                class="flex items-center gap-2 px-2 py-1 hover:bg-base-200 rounded text-sm cursor-move {draggedItem?.type === 'layer' && draggedItem?.id === layer.layer_id ? 'opacity-50' : ''}"
                draggable="true"
                ondragstart={(e) => handleDragStart(e, 'layer', layer.layer_id, group.id)}
                ondragover={(e) => handleDragOver(e, 'layer', layer.layer_id, group.id)}
                ondragleave={handleDragLeave}
                ondrop={(e) => handleDrop(e, 'layer', layer.layer_id, group.id)}
                role="listitem"
              >
                <GripVertical class="w-4 h-4 text-base-content/30 flex-shrink-0" />
                <File class="w-4 h-4 text-green-600 flex-shrink-0" />
                <span class="flex-1">
                  <span class="font-medium">{layer.title}</span>
                  {#if layer.is_default}
                    <span class="badge badge-primary badge-xs ml-2">Standaard</span>
                  {/if}
                </span>
                <span class="text-xs text-base-content/50">#{layer.sort_order}</span>
                <button
                  class="btn btn-ghost btn-xs"
                  onclick={() => toggleDefault(layer.layer_id)}
                  title={layer.is_default ? 'Verwijder van standaard' : 'Maak standaard'}
                >
                  {#if layer.is_default}
                    <Eye class="w-3 h-3" />
                  {:else}
                    <EyeOff class="w-3 h-3" />
                  {/if}
                </button>
              </div>
              
              <!-- Absolute positioned drop indicators for group layers -->
              {#if getDropIndicatorStyle('layer', layer.layer_id, group.id).show}
                {@const indicator = getDropIndicatorStyle('layer', layer.layer_id, group.id)}
                {#if indicator.zone === 'top'}
                  <div class="absolute top-0 left-0 right-0 h-1 bg-primary rounded-full -translate-y-0.5 z-10"></div>
                {:else if indicator.zone === 'bottom'}
                  <div class="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-full translate-y-0.5 z-10"></div>
                {:else if indicator.zone === 'middle'}
                  <div class="absolute inset-0 border-2 border-primary bg-primary/10 rounded z-10 pointer-events-none"></div>
                {/if}
              {/if}
            </div>
          {/each}
        </div>
      {/if}

      <!-- Nested Subgroups -->
      {#each group.subgroups as subgroup}
        {@render groupComponent(subgroup)}
      {/each}
    </div>
  {/if}
</div>
{/snippet}