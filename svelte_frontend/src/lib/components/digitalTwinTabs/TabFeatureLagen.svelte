<script lang="ts">
  import { onMount } from 'svelte';
  import { Folder, FolderOpen, File, Eye, EyeOff, ChevronDown, ChevronRight, Save, RotateCcw, GripVertical } from 'lucide-svelte';
  import { fetchLayers, fetchGroups, bulkUpdateDigitalTwinLayers } from '$lib/api';
  import type { DigitalTwin, Layer, LayerWithAssociation, Group, GroupWithLayers, LayerBulkOperation } from '$lib/types/digitalTwin';

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
  let isSaving = $state(false);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let originalData: { ungroupedLayers: LayerWithAssociation[], rootGroups: GroupWithLayers[] } = { ungroupedLayers: [], rootGroups: [] };

  // Drag and drop state
  let draggedItem = $state<{ type: 'layer' | 'group', id: number, groupId?: number | null } | null>(null);
  let draggedOverItem = $state<{ type: 'layer' | 'group', id: number, groupId?: number | null, zone: 'top' | 'middle' | 'bottom' } | null>(null);

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
      ungroupedLayers = [...ungroupedLayers];
      rootGroups = [...rootGroups];
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
    
    // For groups, only allow middle zone (drop into group)
    if (type === 'group' && zone !== 'middle') {
      draggedOverItem = null;
      return;
    }
    
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

    updateSortOrders();
  }

  function updateSortOrders() {
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

  function getDropZoneClass(type: 'layer' | 'group', id: number, groupId?: number | null) {
    if (!draggedOverItem || draggedOverItem.type !== type || draggedOverItem.id !== id) {
      return '';
    }
    
    const zone = draggedOverItem.zone;
    if (zone === 'top') return 'border-t-4 border-t-primary';
    if (zone === 'bottom') return 'border-b-4 border-b-primary';
    if (zone === 'middle') return 'border-2 border-primary bg-primary/10';
    
    return '';
  }

  // Save changes to the API
  async function saveChanges() {
    if (!hasChanges) return;
    
    isSaving = true;
    try {
      // Collect all layer associations and operation action
      const operations: LayerBulkOperation[] = [];
      
      // Add ungrouped layers
      ungroupedLayers.forEach(layer => {
        operations.push({
          action: "update",
          layer_id: layer.layer_id,
          is_default: layer.is_default,
          sort_order: layer.sort_order,
          group_id: null
        });
      });

      // Add grouped layers recursively
      function collectGroupLayers(groups: GroupWithLayers[]) {
        groups.forEach(group => {
          group.layers.forEach(layer => {
            operations.push({
              action: "update",
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

      await bulkUpdateDigitalTwinLayers(digitalTwinId, operations);
      
      hasChanges = false;
      originalData = deepClone({ ungroupedLayers, rootGroups });
      
      alert('Layer volgorde succesvol opgeslagen!');
    } catch (error) {
      console.error('Failed to save changes:', error);
      alert('Fout bij het opslaan van wijzigingen.');
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
        <!-- Summary -->
        {#if hasChanges}
          <div class="p-3 rounded text-sm space-y-1">
            <p><strong>Overzicht:</strong></p>
            <p>Ongegroepeerde lagen: {ungroupedLayers.length}</p>
            <p>Gegroepeerde lagen: {groupedLayers.length}</p>
            <p>Hoofdgroepen: {rootGroups.length}</p>
            <p>Totaal lagen: {layersWithDetails.length}</p>
            <p class="text-warning font-medium">⚠️ Er zijn niet-opgeslagen wijzigingen</p>
          </div>
        {/if}
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
                  <div
                    class="flex items-center gap-2 px-2 py-1 hover:bg-base-200 rounded text-sm cursor-move {getDropZoneClass('layer', layer.layer_id, null)} {draggedItem?.type === 'layer' && draggedItem?.id === layer.layer_id ? 'opacity-50' : ''}"
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
  <div class="space-y-1" style="margin-left: {group.depth * 1.5}rem;">
    <!-- Group Header -->
    <div
      class="flex items-center gap-2 px-2 py-1 hover:bg-base-200 rounded text-sm {getDropZoneClass('group', group.id)}"
      ondragover={(e) => handleDragOver(e, 'group', group.id)}
      ondragleave={handleDragLeave}
      ondrop={(e) => handleDrop(e, 'group', group.id)}
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

    <!-- Group Content (when expanded) -->
    {#if expandedGroups.has(group.id)}
      <div class="space-y-1">
        <!-- Group Layers -->
        {#if group.layers.length > 0}
          <div class="space-y-1">
            {#each group.layers as layer}
              <div
                class="flex items-center gap-2 px-2 py-1 hover:bg-base-200 rounded text-sm cursor-move {getDropZoneClass('layer', layer.layer_id, group.id)} {draggedItem?.type === 'layer' && draggedItem?.id === layer.layer_id ? 'opacity-50' : ''}"
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
