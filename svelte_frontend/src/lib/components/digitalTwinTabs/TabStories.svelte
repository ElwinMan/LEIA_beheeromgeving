<script lang="ts">
  import { onMount } from 'svelte';
  import {
    fetchStories,
    fetchDigitalTwinStories,
    bulkUpdateDigitalTwinStories,
    fetchLayers,
    fetchDigitalTwin
  } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { Story } from '$lib/types/tool';
  import type { Layer } from '$lib/types/layer';
  import type { StoryWithAssociation, StoryBulkOperation, StoryAssociationResponse } from '$lib/types/digitalTwinAssociation';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import DeleteModal from '$lib/components/modals/DeleteModal.svelte';
  import CreateStoryModal from '$lib/components/modals/CreateStoryModal.svelte';
  import { dragStartAction } from '$lib/utils/dragStartAction';
  import { getDropZone } from '$lib/utils/dropZoneUtils';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();
  let createStoryModalRef: InstanceType<typeof CreateStoryModal>;

  // State for local digital twin data (can be updated independently)
  let localDigitalTwin = $state<DigitalTwin | null>(digitalTwin);

  // Deep clone function
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

  // State
  let allStories = $state<Story[]>([]);
  let storiesWithDetails = $state<StoryWithAssociation[]>([]);
  let hasChanges = $state(false);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let originalData: StoryWithAssociation[] = [];
  let isSaving = $state(false);

  // Delete modal state
  let deleteStoryModalShow = $state(false);
  let storyToDelete: StoryWithAssociation | null = null;
  let skipDeleteStoryConfirm = $state(false);

  // Drag and drop state
  let draggedItem = $state<{
    type: 'story' | 'catalog-story';
    id: number;
    story?: Story;
  } | null>(null);
  let draggedOverItem = $state<{
    type: 'story';
    id: number;
    zone: 'top' | 'middle' | 'bottom';
  } | null>(null);

  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  // Catalog state
  let catalogStories = $state<Story[]>([]);
  let catalogSearchTerm = $state('');
  let catalogIsLoading = $state(true);
  let catalogError = $state<string | null>(null);

  // Layer validation state
  let allLayers = $state<Layer[]>([]);
  let showLayerInfo: { [key: number]: boolean } = $state({});
  
  let digitalTwinLayers = $derived(
    localDigitalTwin?.layer_associations.map(assoc => 
      allLayers.find(layer => layer.id === assoc.layer_id)
    ).filter(Boolean) || []
  );
  let digitalTwinLayerIds = $derived(
    digitalTwinLayers.map(layer => layer?.id).filter(Boolean) || []
  );

  // Get used story IDs for filtering catalog
  let usedStoryIds = $derived(storiesWithDetails.map((s) => s.content_id));

  // Check if story can be added (has all required layers)
  function validateStoryLayers(story: Story): { canAdd: boolean; missingLayers: string[] } {
    if (!story.content?.chapters || !Array.isArray(story.content.chapters)) {
      return { canAdd: true, missingLayers: [] }; // No layer requirements
    }

    const requiredLayerIds = new Set<string>();
    
    // Extract all layer IDs from all chapters and steps
    story.content.chapters.forEach((chapter: any) => {
      if (chapter.steps && Array.isArray(chapter.steps)) {
        chapter.steps.forEach((step: any) => {
          if (step.layers && Array.isArray(step.layers)) {
            step.layers.forEach((layer: any) => {
              if (layer.id) {
                requiredLayerIds.add(layer.id.toString());
              }
            });
          }
        });
      }
    });

    const missingLayerIds = Array.from(requiredLayerIds).filter(
      layerId => !digitalTwinLayerIds.includes(parseInt(layerId))
    );

    // Get layer titles for missing layers
    const missingLayers = missingLayerIds.map(layerId => {
      const layer = allLayers.find(l => l.id === parseInt(layerId));
      return layer?.title || `Layer ${layerId}`;
    });

    return {
      canAdd: missingLayerIds.length === 0,
      missingLayers
    };
  }

  // Filter catalog stories
  const filteredCatalogStories = $derived.by(() => {
    const filtered = catalogStories.filter((story) => !usedStoryIds.includes(story.id));
    
    let searchFiltered;
    if (catalogSearchTerm.trim() === '') {
      searchFiltered = filtered;
    } else {
      const term = catalogSearchTerm.toLowerCase();
      searchFiltered = filtered.filter(
        (story) =>
          story.name.toLowerCase().includes(term) ||
          (story.description && story.description.toLowerCase().includes(term))
      );
    }

    // Sort by compatibility first (compatible stories on top)
    return searchFiltered.sort((a, b) => {
      const validationA = validateStoryLayers(a);
      const validationB = validateStoryLayers(b);
      
      // Sort by compatibility first (compatible stories on top)
      if (validationA.canAdd && !validationB.canAdd) return -1;
      if (!validationA.canAdd && validationB.canAdd) return 1;
      
      // Then sort alphabetically by name
      return a.name.localeCompare(b.name);
    });
  });

  onMount(() => {
    const stored = sessionStorage.getItem('skipDeleteStoryConfirm');
    skipDeleteStoryConfirm = stored === 'true';
  });

  async function loadAllLayers() {
    try {
      allLayers = await fetchLayers();
    } catch (err) {
      console.error('Error loading layers:', err);
    }
  }

  async function loadDigitalTwin() {
    try {
      localDigitalTwin = await fetchDigitalTwin(digitalTwinId);
    } catch (err) {
      console.error('Error loading digital twin:', err);
      // Fallback to the prop if API call fails
      localDigitalTwin = digitalTwin;
    }
  }

  async function fetchAllData() {
    isLoading = true;
    try {
      // Load all layers first for validation
      await loadAllLayers();
      // Load digital twin data to get current layer associations
      await loadDigitalTwin();
      
      // Fetch all stories for catalog
      allStories = await fetchStories();
      catalogStories = allStories;
      catalogIsLoading = false;

      // Fetch digital twin stories
      const associations: StoryAssociationResponse[] = await fetchDigitalTwinStories(digitalTwinId);
      
      // Get story details and create StoryWithAssociation objects
      storiesWithDetails = associations
        .map((assoc) => {
          const story = allStories.find((s) => s.id === assoc.content_id);
          if (story) {
            return {
              tool_id: assoc.tool_id,
              content_type_id: assoc.content_type_id,
              content_id: assoc.content_id,
              sort_order: assoc.sort_order,
              name: story.name,
              description: story.description || '',
              content: story.content,
              isNew: false
            } as StoryWithAssociation;
          }
          return null;
        })
        .filter((story): story is StoryWithAssociation => story !== null)
        .sort((a, b) => a.sort_order - b.sort_order);

      originalData = deepClone(storiesWithDetails);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error occurred';
      catalogError = error;
    } finally {
      isLoading = false;
    }
  }

  onMount(fetchAllData);

  function handleDragStart(story: StoryWithAssociation) {
    const fullStory = allStories.find(s => s.id === story.content_id);
    draggedItem = { type: 'story', id: story.content_id, story: fullStory };
  }

  function handleDragEnd() {
    draggedItem = null;
    draggedOverItem = null;
  }

  function handleDragLeave() {
    draggedOverItem = null;
  }

  function handleDragOver(e: DragEvent, index: number) {
    e.preventDefault();
    if (!draggedItem) return;

    const story = storiesWithDetails[index];
    const listItem = (e.currentTarget as HTMLElement);
    const zone = getDropZone(e, listItem);
    draggedOverItem = { type: 'story', id: story.content_id, zone };
  }

  function handleDrop(e: DragEvent, targetIndex: number) {
    e.preventDefault();
    
    if (!draggedItem) return;

    // Handle story from catalog
    if (draggedItem.type === 'catalog-story') {
      const sourceStory = draggedItem.story;
      if (!sourceStory) return;

      // Validate story layers before allowing drop
      const validation = validateStoryLayers(sourceStory);
      if (!validation.canAdd) {
        // Show error message or prevent drop
        alert(`Deze story kan niet worden toegevoegd. Ontbrekende lagen: ${validation.missingLayers.join(', ')}`);
        handleDragEnd();
        return;
      }

      const existingStory = allStories.find(s => s.id === sourceStory.id);
      if (!existingStory) return;

      const zone = draggedOverItem?.zone || 'middle';
      let insertIndex = targetIndex;
      
      if (zone === 'bottom') {
        insertIndex = targetIndex + 1;
      }

      // Add new story from catalog
      const newStory = createStoryAssociation(sourceStory, insertIndex);

      storiesWithDetails.splice(insertIndex, 0, newStory);
      
      // Update sort_order for all items
      updateSortOrders();
      storiesWithDetails = [...storiesWithDetails];
      
      hasChanges = true;
    } 
    // Handle moving existing story within the list
    else if (draggedItem.type === 'story') {
      const draggedStoryId = draggedItem.id;
      const existingIndex = storiesWithDetails.findIndex(s => s.content_id === draggedStoryId);
      
      if (existingIndex !== -1) {
        const zone = draggedOverItem?.zone || 'middle';
        let insertIndex = targetIndex;
        
        if (zone === 'bottom') {
          insertIndex = targetIndex + 1;
        } else if (zone === 'middle') {
          // For middle drops of existing items, adjust based on direction
          if (existingIndex < targetIndex) {
            // Moving down: place item below target (target moves up)
            insertIndex = targetIndex + 1;
          }
          // Moving up: place item above target (use targetIndex as-is)
        }
        
        // Only move if it's actually a different position
        if (existingIndex !== insertIndex) {
          moveStoryInList(existingIndex, insertIndex);
        }
      }
    }

    handleDragEnd();
  }

  function moveStoryInList(fromIndex: number, toIndex: number) {
    const item = storiesWithDetails[fromIndex];
    
    // Adjust target index if moving forward (to account for removal shifting indices)
    let adjustedToIndex = toIndex;
    if (fromIndex < toIndex) {
      adjustedToIndex = toIndex - 1;
    }
    
    storiesWithDetails.splice(fromIndex, 1);
    storiesWithDetails.splice(adjustedToIndex, 0, item);
    
    // Update sort_order for all items
    updateSortOrders();
    storiesWithDetails = [...storiesWithDetails];
    
    hasChanges = true;
  }

  function createStoryAssociation(story: Story, sortOrder: number): StoryWithAssociation {
    return {
      tool_id: 0, // Will be set by backend
      content_type_id: 0, // Will be set by backend
      content_id: story.id,
      sort_order: sortOrder,
      name: story.name,
      description: story.description || '',
      content: story.content,
      isNew: true
    };
  }

  function handleEmptyStateDrop(e: DragEvent) {
    e.preventDefault();
    
    const dragData = (window as any).catalogDragData;
    if (!dragData) return;

    const story = dragData as Story;
    
    // Validate story layers before allowing drop
    const validation = validateStoryLayers(story);
    if (!validation.canAdd) {
      alert(`Deze story kan niet worden toegevoegd. Ontbrekende lagen: ${validation.missingLayers.join(', ')}`);
      delete (window as any).catalogDragData;
      return;
    }
    
    const existingStory = allStories.find(s => s.id === story.id);
    if (!existingStory) return;

    const newStory = createStoryAssociation(existingStory, storiesWithDetails.length);

    storiesWithDetails.push(newStory);
    storiesWithDetails = [...storiesWithDetails];
    hasChanges = true;
    
    // Clean up
    delete (window as any).catalogDragData;
  }

  function getDropIndicatorStyle(type: 'story', id: number) {
    if (!draggedOverItem || draggedOverItem.type !== type || draggedOverItem.id !== id) {
      return { show: false, zone: null };
    }

    return { show: true, zone: draggedOverItem.zone };
  }

  function addStoryToDigitalTwin(story: Story) {
    const newStoryAssociation: StoryWithAssociation = {
      tool_id: 0, // Will be set by backend
      content_type_id: 0, // Will be set by backend
      content_id: story.id,
      sort_order: storiesWithDetails.length,
      name: story.name,
      description: story.description || '',
      content: story.content,
      isNew: true
    };

    storiesWithDetails.push(newStoryAssociation);
    storiesWithDetails = [...storiesWithDetails];
    hasChanges = true;
  }

  function handleCatalogAddStory(story: Story) {
    addStoryToDigitalTwin(story);
  }

  function updateSortOrders() {
    storiesWithDetails.forEach((story, index) => {
      story.sort_order = index;
    });
  }

  async function saveChanges() {
    if (!hasChanges) return;

    isSaving = true;
    try {
      const operations: StoryBulkOperation[] = [];

      // Add all stories (create for new, update for existing)
      storiesWithDetails.forEach((story) => {
        operations.push({
          action: story.isNew ? 'create' : 'update',
          tool_id: story.tool_id,
          content_id: story.content_id,
          sort_order: story.sort_order,
          is_default: false
        });
      });

      // Add deleted stories
      if ((window as any)._deletedStoryIds && Array.isArray((window as any)._deletedStoryIds)) {
        for (const deletedId of (window as any)._deletedStoryIds) {
          operations.push({
            action: 'delete',
            tool_id: 0, // Will be ignored for delete operations
            content_id: deletedId,
            sort_order: 0
          });
        }
      }

      await bulkUpdateDigitalTwinStories(digitalTwinId, { operations });

      // Mark all stories as no longer new
      storiesWithDetails.forEach((story) => {
        story.isNew = false;
      });

      // Clear deleted story IDs
      if ((window as any)._deletedStoryIds) {
        (window as any)._deletedStoryIds = [];
      }

      hasChanges = false;
      originalData = deepClone(storiesWithDetails);

      await fetchAllData();
      successBanner?.show();
    } catch (error) {
      console.error('Failed to save changes:', error);
      errorBanner?.show();
    } finally {
      isSaving = false;
    }
  }

  function resetChanges() {
    storiesWithDetails = deepClone(originalData);
    hasChanges = false;
  }

  function confirmDeleteStory(story: StoryWithAssociation) {
    storyToDelete = story;
    if (sessionStorage.getItem('skipDeleteStoryConfirm') === 'true') {
      actuallyDeleteStory(story);
    } else {
      deleteStoryModalShow = true;
    }
  }

  async function actuallyDeleteStory(story: StoryWithAssociation) {
    // Remove from storiesWithDetails
    storiesWithDetails = storiesWithDetails.filter(s => s.content_id !== story.content_id);

    // Track deleted story for bulk API call (only if it's not a new story)
    if (!story.isNew) {
      if (!(window as any)._deletedStoryIds) {
        (window as any)._deletedStoryIds = [];
      }
      (window as any)._deletedStoryIds.push(story.content_id);
    }

    // Update sort orders
    updateSortOrders();
    storiesWithDetails = [...storiesWithDetails];
    hasChanges = true;
  }

  function handleDeleteStoryModalConfirm(detail: { doNotAskAgain: boolean }) {
    if (storyToDelete) {
      actuallyDeleteStory(storyToDelete);
      if (detail.doNotAskAgain) {
        skipDeleteStoryConfirm = true;
        sessionStorage.setItem('skipDeleteStoryConfirm', 'true');
      }
    }
    deleteStoryModalShow = false;
    storyToDelete = null;
  }

  function handleDeleteStoryModalCancel() {
    deleteStoryModalShow = false;
    storyToDelete = null;
  }

  function handleStoryCreated(event: CustomEvent<Story>) {
    const newStory = event.detail;
    // Refresh the catalog to include the new story
    allStories = [...allStories, newStory];
    catalogStories = [...catalogStories, newStory];
  }

  function toggleLayerInfo(storyId: number) {
    showLayerInfo[storyId] = !showLayerInfo[storyId];
  }
</script>

<CreateStoryModal
  bind:this={createStoryModalRef}
  on:created={handleStoryCreated}
/>

<DeleteModal
  show={deleteStoryModalShow}
  title="Story verwijderen"
  message="Weet je zeker dat je deze story wilt verwijderen uit de digital twin?"
  confirmLabel="Verwijder"
  cancelLabel="Annuleer"
  showCheckbox={true}
  checkboxLabel="Niet meer vragen deze sessie"
  onconfirm={handleDeleteStoryModalConfirm}
  oncancel={handleDeleteStoryModalCancel}
/>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Stories succesvol opgeslagen!"
/>

<AlertBanner
  bind:this={errorBanner}
  type="error"
  message="Er is een fout opgetreden bij het opslaan van de stories."
/>

<div class="flex h-full gap-4">
  <!-- Main content -->
  <div class="flex-1 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold">Stories</h2>
        <p class="text-base-content/70">Beheer stories voor deze digital twin.</p>
      </div>
      
      <div class="flex gap-4">
        <!-- Create action - separate group -->
        <button 
          class="btn btn-primary"
          onclick={() => createStoryModalRef.showModal()}
        >
          <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
          Nieuwe Story
        </button>
        
        <!-- Save/Reset actions - grouped together -->
        <div class="flex gap-2">
          {#if hasChanges}
            <button class="btn btn-ghost" onclick={resetChanges}>
              <img src="/icons/rotate-ccw.svg" alt="Reset" class="h-4 w-4" />
              Reset
            </button>
          {:else}
            <div class="btn btn-ghost invisible">
              <img src="/icons/rotate-ccw.svg" alt="Reset" class="h-4 w-4" />
              Reset
            </div>
          {/if}
          
          <button class="btn btn-primary" onclick={saveChanges} disabled={isSaving || !hasChanges}>
            {#if isSaving}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              <img src="/icons/save.svg" alt="Opslaan" class="h-4 w-4" />
            {/if}
            Opslaan
          </button>
        </div>
      </div>
    </div>

    {#if isLoading}
      <div class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
    {:else if error}
      <div class="alert alert-error">
        <span>{error}</span>
      </div>
    {:else}
      <div class="card bg-base-100 border-base-300 border">
        <div class="card-body">
          <h3 class="card-title">Actieve Stories</h3>
          
          {#if storiesWithDetails.length === 0}
            <div 
              class="border-2 border-dashed border-base-300 rounded-lg p-8 text-center text-base-content/50 transition-colors {draggedItem?.type === 'catalog-story' ? 'border-primary bg-primary/5' : ''}"
              role="region"
              ondragover={(e) => {
                e.preventDefault();
                // Try to set draggedItem from catalog data if not already set
                if (!draggedItem && (window as any).catalogDragData) {
                  const catalogData = (window as any).catalogDragData;
                  draggedItem = { type: 'catalog-story', id: catalogData.id, story: catalogData };
                }
              }}
              ondrop={handleEmptyStateDrop}
            >
              <p>Geen stories gevonden. Sleep een story hierheen uit de catalogus.</p>
            </div>
          {:else}
            <div class="space-y-2">
              {#each storiesWithDetails as story, index (story.content_id)}
                {@const fullStory = allStories.find(s => s.id === story.content_id)}
                {@const validation = fullStory ? validateStoryLayers(fullStory) : { canAdd: true, missingLayers: [] }}
                <div class="relative">
                  <div 
                    class="flex items-center gap-3 p-3 border rounded-lg hover:bg-base-50 transition-colors"
                    class:border-base-300={validation.canAdd}
                    class:border-error={!validation.canAdd}
                    class:bg-red-50={!validation.canAdd}
                    class:opacity-50={draggedItem?.type === 'story' && draggedItem?.id === story.content_id}
                    draggable="true"
                    role="listitem"
                    ondragstart={() => handleDragStart(story)}
                    ondragend={handleDragEnd}
                    ondragover={(e) => handleDragOver(e, index)}
                    ondragleave={handleDragLeave}
                    ondrop={(e) => handleDrop(e, index)}
                  >
                    <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                    
                    <img 
                      src="/icons/book.svg" 
                      alt="Story" 
                      class="h-5 w-5 flex-shrink-0 text-blue-600" 
                      class:text-error={!validation.canAdd}
                    />
                    
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2">
                        <div class="font-medium text-sm" class:text-error={!validation.canAdd}>{story.name}</div>
                        {#if story.isNew}
                          <span class="badge badge-success badge-xs">nieuw</span>
                        {/if}
                        {#if !validation.canAdd}
                          <span class="badge badge-error badge-xs">Ontbrekende lagen</span>
                        {/if}
                      </div>
                      {#if story.description}
                        <div class="text-xs text-base-content/70">{story.description}</div>
                      {/if}
                    </div>
                    
                    <div class="text-xs text-base-content/50">
                      #{story.sort_order}
                    </div>
                    
                    <!-- Actions -->
                    <div class="flex gap-2">
                      <!-- Layer info button -->
                      {#if fullStory}
                        <button
                          class="btn btn-xs"
                          class:btn-error={!validation.canAdd}
                          class:btn-success={validation.canAdd}
                          onclick={() => toggleLayerInfo(story.content_id)}
                          title={validation.canAdd ? 'Bekijk vereiste lagen' : 'Bekijk ontbrekende lagen'}
                        >
                          {#if !validation.canAdd}
                            <img src="/icons/circle-alert.svg" alt="Lijst ontbrekende lagen" class="h-3 w-3" />
                          {:else}
                            <img src="/icons/check.svg" alt="Lijst vereiste lagen" class="h-3 w-3" />
                          {/if}
                        </button>
                      {/if}
                      
                      <button
                        class="btn btn-ghost btn-xs text-error hover:bg-error/10"
                        onclick={() => confirmDeleteStory(story)}
                        title="Verwijder story"
                        aria-label="Verwijder story"
                      >
                        <img src="/icons/trash-2.svg" alt="Verwijder" class="h-5 w-5" />
                      </button>
                    </div>
                  </div>

                  <!-- Layer info display -->
                  <!-- DEBUG MARKER: Before layer info -->
                  {#if showLayerInfo[story.content_id] && fullStory}
                    {#if !validation.canAdd}
                      <div class="mt-2 p-2 bg-error/10 border border-error/30 rounded text-xs">
                        <div class="font-medium text-error mb-1">Ontbrekende lagen:</div>
                        <div class="text-error font-medium">
                          {validation.missingLayers.join(', ')}
                        </div>
                      </div>
                    {:else}
                      <!-- Show required layers if story has layer requirements -->
                      {@const requiredLayerTitles: string[] = []}
                      {#each fullStory.content?.chapters || [] as chapter}
                        {#each chapter.steps || [] as step}
                          {#each step.layers || [] as layer}
                            {#if layer.id}
                              {@const foundLayer = allLayers.find(l => l.id === parseInt(layer.id))}
                              {#if foundLayer && foundLayer.title && !requiredLayerTitles.includes(foundLayer.title)}
                                {@const _ = requiredLayerTitles.push(foundLayer.title)}
                              {/if}
                            {/if}
                          {/each}
                        {/each}
                      {/each}
                      {#if requiredLayerTitles.length > 0}
                        <div class="mt-2 p-2 bg-success/10 border border-success/30 rounded text-xs">
                          <div class="font-medium text-success mb-1">Vereiste lagen aanwezig:</div>
                          <div class="text-success font-medium">
                            {requiredLayerTitles.join(', ')}
                          </div>
                        </div>
                      {:else}
                        <div class="mt-2 p-2 bg-info/10 border border-info/30 rounded text-xs">
                          <div class="font-medium text-info">Deze story heeft geen laagvereisten.</div>
                        </div>
                      {/if}
                    {/if}
                  {/if}

                  <!-- Absolute positioned drop indicators -->
                  {#if getDropIndicatorStyle('story', story.content_id).show}
                    {@const indicator = getDropIndicatorStyle('story', story.content_id)}
                    {#if indicator.zone === 'top'}
                      <div class="bg-primary absolute top-0 right-0 left-0 z-10 h-1 -translate-y-0.5 rounded-full"></div>
                    {:else if indicator.zone === 'bottom'}
                      <div class="bg-primary absolute right-0 bottom-0 left-0 z-10 h-1 translate-y-0.5 rounded-full"></div>
                    {:else if indicator.zone === 'middle'}
                      <div class="border-primary bg-primary/10 pointer-events-none absolute inset-0 z-10 rounded border-2"></div>
                    {/if}
                  {/if}
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>

  <!-- Catalog sidebar -->
  <div class="w-80 space-y-4">
    <div class="card bg-base-100 border-base-300 border">
      <div class="card-body">
        <h3 class="card-title">Story Catalogus</h3>
        
        <!-- Search -->
        <input 
          class="input input-bordered input-sm w-full" 
          placeholder="Zoek stories..."
          bind:value={catalogSearchTerm}
        />

        {#if catalogIsLoading}
          <div class="flex justify-center py-4">
            <span class="loading loading-spinner"></span>
          </div>
        {:else if catalogError}
          <div class="alert alert-error alert-sm">
            <span>{catalogError}</span>
          </div>
        {:else}
          <div class="space-y-2 max-h-96 overflow-y-auto">
            {#each filteredCatalogStories as story (story.id)}
              {@const validation = validateStoryLayers(story)}
              <div 
                class="p-2 border rounded transition-colors"
                class:border-base-300={validation.canAdd}
                class:bg-base-50={validation.canAdd}
                class:hover:bg-base-100={validation.canAdd}
                class:border-error={!validation.canAdd}
                class:bg-red-100={!validation.canAdd}
                class:opacity-60={!validation.canAdd}
                class:cursor-move={validation.canAdd}
                class:cursor-not-allowed={!validation.canAdd}
                draggable={validation.canAdd}
                use:dragStartAction={{
                  item: { type: 'catalog-story' as 'catalog-story', id: story.id, story },
                  type: 'catalog-story' as 'catalog-story',
                  dataKey: 'application/json',
                  effectAllowed: 'copy',
                  globalKey: 'catalogDragData',
                  onDragStart: (item) => {
                    if (validation.canAdd) {
                      draggedItem = item;
                    }
                  }
                }}
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="font-medium text-sm">{story.name}</div>
                    {#if story.description}
                      <div class="text-xs text-base-content/70">{story.description}</div>
                    {/if}
                  </div>
                  
                  {#if !validation.canAdd || (story.content?.chapters && story.content.chapters.some((ch: any) => ch.steps?.some((step: any) => step.layers?.length > 0)))}
                    <button
                      class="btn btn-circle btn-xs ml-2 flex-shrink-0"
                      class:btn-error={!validation.canAdd}
                      class:btn-success={validation.canAdd}
                      onclick={() => toggleLayerInfo(story.id)}
                      title={validation.canAdd ? 'Bekijk vereiste lagen' : 'Bekijk ontbrekende lagen'}
                    >
                      {#if !validation.canAdd}
                        <img src="/icons/circle-alert.svg" alt="Lijst ontbrekende lagen" class="h-3 w-3" />
                      {:else}
                        <img src="/icons/check.svg" alt="Lijst vereiste lagen" class="h-3 w-3" />
                      {/if}
                    </button>
                  {/if}
                </div>
                
                {#if showLayerInfo[story.id]}
                  {#if !validation.canAdd}
                    <div class="mt-2 p-2 bg-error/10 border border-error/30 rounded text-xs">
                      <div class="font-medium text-error mb-1">Ontbrekende lagen:</div>
                      <div class="text-error font-medium">
                        {validation.missingLayers.join(', ')}
                      </div>
                    </div>
                  {:else if story.content?.chapters}
                    {@const requiredLayerTitles: string[] = []}
                    {#each story.content.chapters as chapter}
                      {#each chapter.steps || [] as step}
                        {#each step.layers || [] as layer}
                          {#if layer.id}
                            {@const foundLayer = allLayers.find(l => l.id === parseInt(layer.id))}
                            {#if foundLayer && foundLayer.title && !requiredLayerTitles.includes(foundLayer.title)}
                              {@const _ = requiredLayerTitles.push(foundLayer.title)}
                            {/if}
                          {/if}
                        {/each}
                      {/each}
                    {/each}
                    {#if requiredLayerTitles.length > 0}
                      <div class="mt-2 p-2 bg-success/10 border border-success/30 rounded text-xs">
                        <div class="font-medium text-success mb-1">Vereiste lagen aanwezig:</div>
                        <div class="text-success font-medium">
                          {requiredLayerTitles.join(', ')}
                        </div>
                      </div>
                    {/if}
                  {/if}
                {/if}
              </div>
            {:else}
              <div class="text-center py-4 text-base-content/50">
                <p>Geen stories beschikbaar</p>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
