<script lang="ts">
  import { onMount } from 'svelte';
  import {
    fetchStories,
    fetchDigitalTwinStories,
    bulkUpdateDigitalTwinStories
  } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { Story } from '$lib/types/tool';
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

  // Get used story IDs for filtering catalog
  let usedStoryIds = $derived(storiesWithDetails.map((s) => s.content_id));

  // Filter catalog stories
  const filteredCatalogStories = $derived.by(() => {
    if (catalogSearchTerm.trim() === '') {
      return catalogStories.filter((story) => !usedStoryIds.includes(story.id));
    } else {
      const term = catalogSearchTerm.toLowerCase();
      return catalogStories.filter(
        (story) =>
          !usedStoryIds.includes(story.id) &&
          (story.name.toLowerCase().includes(term) ||
            (story.description && story.description.toLowerCase().includes(term)))
      );
    }
  });

  onMount(() => {
    const stored = sessionStorage.getItem('skipDeleteStoryConfirm');
    skipDeleteStoryConfirm = stored === 'true';
  });

  async function fetchAllData() {
    isLoading = true;
    try {
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

    const sourceStory = draggedItem.story;
    if (!sourceStory) return;

    const existingStory = allStories.find(s => s.id === sourceStory.id);
    if (!existingStory) return;

    const zone = draggedOverItem?.zone || 'middle';
    let insertIndex = targetIndex;
    
    if (zone === 'bottom') {
      insertIndex = targetIndex + 1;
    }

    // Check if story is already in the list
    const existingIndex = storiesWithDetails.findIndex(s => s.content_id === sourceStory.id);
    
    if (existingIndex !== -1 && draggedItem.type === 'story') {
      // Move existing story
      moveStoryInList(existingIndex, insertIndex);
    } else if (draggedItem.type === 'catalog-story') {
      // Add new story from catalog
      const newStory = createStoryAssociation(sourceStory, insertIndex);

      storiesWithDetails.splice(insertIndex, 0, newStory);
      
      // Update sort_order for all items
      updateSortOrders();
      storiesWithDetails = [...storiesWithDetails];
      
      hasChanges = true;
    }

    draggedItem = null;
    draggedOverItem = null;
  }

  function moveStoryInList(fromIndex: number, toIndex: number) {
    const item = storiesWithDetails[fromIndex];
    storiesWithDetails.splice(fromIndex, 1);
    storiesWithDetails.splice(toIndex, 0, item);
    
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
      
      <div class="flex gap-2">
        <button 
          class="btn btn-primary btn-sm"
          onclick={() => createStoryModalRef.showModal()}
        >
          <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
          Nieuwe Story
        </button>
        
        {#if hasChanges}
          <button class="btn btn-success btn-sm" onclick={saveChanges} disabled={isSaving}>
            {#if isSaving}
              <span class="loading loading-spinner loading-sm"></span>
            {:else}
              <img src="/icons/save.svg" alt="Opslaan" class="h-4 w-4" />
            {/if}
            Opslaan
          </button>
          <button class="btn btn-ghost btn-sm" onclick={resetChanges}>
            <img src="/icons/rotate-ccw.svg" alt="Reset" class="h-4 w-4" />
            Reset
          </button>
        {/if}
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
                <div class="relative">
                  <div 
                    class="flex items-center gap-3 p-3 border border-base-300 rounded-lg hover:bg-base-50 transition-colors {draggedItem?.type === 'story' && draggedItem?.id === story.content_id ? 'opacity-50' : ''}"
                    use:dragStartAction={{
                      item: { type: 'story' as 'story', id: story.content_id },
                      type: 'story' as 'story',
                      dataKey: 'application/json',
                      effectAllowed: 'move',
                      onDragStart: (item) => { draggedItem = item; }
                    }}
                    draggable="true"
                    ondragover={(e) => handleDragOver(e, index)}
                    ondragleave={handleDragLeave}
                    ondrop={(e) => handleDrop(e, index)}
                    role="listitem"
                  >
                    <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                    
                    <img src="/icons/book.svg" alt="Story" class="h-5 w-5 flex-shrink-0 text-blue-600" />
                    
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2">
                        <div class="font-medium text-sm">{story.name}</div>
                        {#if story.isNew}
                          <span class="badge badge-success badge-xs">nieuw</span>
                        {/if}
                      </div>
                      {#if story.description}
                        <div class="text-xs text-base-content/70">{story.description}</div>
                      {/if}
                    </div>
                    
                    <div class="text-xs text-base-content/50">
                      #{story.sort_order}
                    </div>
                    
                    <button
                      class="btn btn-ghost btn-xs text-error hover:bg-error/10"
                      onclick={() => confirmDeleteStory(story)}
                      title="Verwijder story"
                      aria-label="Verwijder story"
                    >
                      <img src="/icons/trash-2.svg" alt="Verwijder" class="h-5 w-5" />
                    </button>
                  </div>

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
              <div 
                class="p-2 border border-base-300 rounded cursor-move hover:bg-base-50 transition-colors"
                draggable="true"
                use:dragStartAction={{
                  item: { type: 'catalog-story' as 'catalog-story', id: story.id, story },
                  type: 'catalog-story' as 'catalog-story',
                  dataKey: 'application/json',
                  effectAllowed: 'copy',
                  globalKey: 'catalogDragData',
                  onDragStart: (item) => {
                    console.log('Dragging:', item);
                    draggedItem = item;
                  }
                }}
              >
                <div class="font-medium text-sm">{story.name}</div>
                {#if story.description}
                  <div class="text-xs text-base-content/70">{story.description}</div>
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
