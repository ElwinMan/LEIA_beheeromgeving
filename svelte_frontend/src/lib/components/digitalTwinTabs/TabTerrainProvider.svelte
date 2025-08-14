<script lang="ts">
  import { onMount } from 'svelte';
  import {
    fetchDigitalTwin,
    fetchTerrainProviders,
    fetchDigitalTwinTerrainProviders,
    bulkUpdateDigitalTwinTerrainProviders,
    fetchCesiumConfiguration,
    updateCesiumConfiguration
  } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { TerrainProvider } from '$lib/types/tool';
  import type { TerrainProviderWithAssociation, TerrainProviderBulkOperation, TerrainProviderAssociationResponse, CesiumConfiguration } from '$lib/types/digitalTwinAssociation';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import DeleteModal from '$lib/components/modals/DeleteModal.svelte';
  import CreateTerrainProviderModal from '$lib/components/modals/CreateTerrainProviderModal.svelte';
  import CesiumConfigModal from '$lib/components/modals/CesiumConfigModal.svelte';
  import { dragStartAction } from '$lib/utils/dragStartAction';
  import { getDropZone } from '$lib/utils/dropZoneUtils';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();

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
  let allTerrainProviders = $state<TerrainProvider[]>([]);
  let terrainProvidersWithDetails = $state<TerrainProviderWithAssociation[]>([]);
  let hasChanges = $state(false);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let originalData: TerrainProviderWithAssociation[] = [];
  let isSaving = $state(false);

  // Delete modal state
  let deleteTerrainProviderModalShow = $state(false);
  let terrainProviderToDelete: TerrainProviderWithAssociation | null = null;
  let skipDeleteTerrainProviderConfirm = false;

  // Drag and drop state
  let draggedItem = $state<{
    type: 'terrain-provider' | 'catalog-terrain-provider';
    id: number;
    terrainProvider?: TerrainProvider;
  } | null>(null);
  let draggedOverItem = $state<{
    type: 'terrain-provider';
    id: number;
    zone: 'top' | 'middle' | 'bottom';
  } | null>(null);

  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let createTerrainProviderModalRef: InstanceType<typeof CreateTerrainProviderModal>;
  let cesiumConfigModalRef: InstanceType<typeof CesiumConfigModal>;

  // Cesium configuration state
  let cesiumConfig = $state<CesiumConfiguration | null>(null);
  let isLoadingConfig = $state(false);

  // Catalog state
  let catalogTerrainProviders = $state<TerrainProvider[]>([]);
  let catalogSearchTerm = $state('');
  let catalogIsLoading = $state(true);
  let catalogError = $state<string | null>(null);

  // Get used terrain provider IDs for filtering catalog
  let usedTerrainProviderIds = $derived(terrainProvidersWithDetails.map((tp) => tp.content_id));

  onMount(async () => {
    const stored = sessionStorage.getItem('skipDeleteTerrainProviderConfirm');
    skipDeleteTerrainProviderConfirm = stored === 'true';
    
    // Load catalog terrain providers first, then load associations and config
    await loadCatalogTerrainProviders();
    await loadTerrainProviders();
    await loadCesiumConfiguration();
  });

  // Filter catalog terrain providers
  let filteredCatalogTerrainProviders = $derived(
    catalogTerrainProviders.filter(terrainProvider => 
      !usedTerrainProviderIds.includes(terrainProvider.id) &&
      (catalogSearchTerm.trim() === '' || 
       terrainProvider.title.toLowerCase().includes(catalogSearchTerm.toLowerCase()) ||
       terrainProvider.url.toLowerCase().includes(catalogSearchTerm.toLowerCase()))
    )
  );

  async function loadTerrainProviders() {
    isLoading = true;
    error = null;
    try {
      const associations: TerrainProviderAssociationResponse[] = await fetchDigitalTwinTerrainProviders(digitalTwinId);
      
      terrainProvidersWithDetails = associations
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((association) => {
          const terrainProviderDetails = allTerrainProviders.find((tp) => tp.id === association.content_id);
          return {
            tool_id: association.tool_id,
            content_type_id: association.content_type_id,
            content_id: association.content_id,
            sort_order: association.sort_order,
            title: terrainProviderDetails?.title || `TerrainProvider ${association.content_id}`,
            url: terrainProviderDetails?.url || '',
            vertexNormals: terrainProviderDetails?.vertexNormals || '',
            isNew: false
          };
        });

      originalData = deepClone(terrainProvidersWithDetails);
      hasChanges = false;
    } catch (err) {
      console.error('Error loading terrain providers:', err);
      error = err instanceof Error ? err.message : 'Unknown error occurred';
    } finally {
      isLoading = false;
    }
  }

  async function loadCatalogTerrainProviders() {
    catalogIsLoading = true;
    catalogError = null;
    try {
      const terrainProviders = await fetchTerrainProviders();
      allTerrainProviders = terrainProviders;
      catalogTerrainProviders = terrainProviders;
    } catch (err) {
      console.error('Error loading catalog terrain providers:', err);
      catalogError = err instanceof Error ? err.message : 'Unknown error occurred';
    } finally {
      catalogIsLoading = false;
    }
  }

  // Helper function to create terrain provider association
  function createTerrainProviderAssociation(terrainProvider: TerrainProvider, sortOrder: number): TerrainProviderWithAssociation {
    return {
      tool_id: 0, // Will be set by the backend
      content_type_id: 0, // Will be set by the backend  
      content_id: terrainProvider.id,
      sort_order: sortOrder,
      title: terrainProvider.title,
      url: terrainProvider.url,
      vertexNormals: terrainProvider.vertexNormals || '',
      isNew: true
    };
  }

  function handleDragStart(terrainProvider: TerrainProvider) {
    draggedItem = { type: 'terrain-provider', id: terrainProvider.id, terrainProvider };
  }

  function handleDragEnd() {
    draggedItem = null;
    draggedOverItem = null;
  }

  function handleDragOver(e: DragEvent, index: number) {
    e.preventDefault();
    if (!draggedItem) return;

    const terrainProvider = terrainProvidersWithDetails[index];
    const listItem = (e.currentTarget as HTMLElement);
    const zone = getDropZone(e, listItem);
    draggedOverItem = { type: 'terrain-provider', id: terrainProvider.content_id, zone };
  }

  function handleDragLeave() {
    draggedOverItem = null;
  }

  function moveTerrainProviderInList(fromIndex: number, toIndex: number) {
    const item = terrainProvidersWithDetails[fromIndex];
    
    // Adjust target index if moving forward (to account for removal shifting indices)
    let adjustedToIndex = toIndex;
    if (fromIndex < toIndex) {
      adjustedToIndex = toIndex - 1;
    }
    
    terrainProvidersWithDetails.splice(fromIndex, 1);
    terrainProvidersWithDetails.splice(adjustedToIndex, 0, item);
    
    // Update sort_order for all items
    terrainProvidersWithDetails.forEach((terrainProvider, index) => {
      terrainProvider.sort_order = index;
    });
    
    hasChanges = true;
  }

  function handleDrop(e: DragEvent, targetIndex: number) {
    e.preventDefault();
    
    if (!draggedItem || !draggedOverItem) return;

    const zone = draggedOverItem.zone;

    if (draggedItem.type === 'catalog-terrain-provider') {
      // Handle catalog terrain provider drop
      if (draggedItem.terrainProvider) {
        const terrainProvider = draggedItem.terrainProvider;
        const newTerrainProviderAssociation = createTerrainProviderAssociation(terrainProvider, 0);
        
        let insertIndex = targetIndex;
        if (zone === 'bottom') {
          insertIndex = targetIndex + 1;
        }
        
        terrainProvidersWithDetails.splice(insertIndex, 0, newTerrainProviderAssociation);
        
        // Update sort orders
        terrainProvidersWithDetails.forEach((tp, index) => {
          tp.sort_order = index;
        });
        
        terrainProvidersWithDetails = [...terrainProvidersWithDetails];
        hasChanges = true;
      }
    } else if (draggedItem.type === 'terrain-provider') {
      // Handle existing terrain provider reordering
      const draggedIndex = terrainProvidersWithDetails.findIndex(tp => tp.content_id === draggedItem!.id);
      if (draggedIndex !== -1) {
        let newIndex = targetIndex;
        if (zone === 'bottom') {
          newIndex = targetIndex + 1;
        }
        moveTerrainProviderInList(draggedIndex, newIndex);
      }
    }

    draggedItem = null;
    draggedOverItem = null;
  }

  function handleCatalogDrop(e: DragEvent) {
    e.preventDefault();
    
    if (!draggedItem || draggedItem.type !== 'catalog-terrain-provider' || !draggedItem.terrainProvider) return;

    const terrainProvider = draggedItem.terrainProvider;
    const newTerrainProviderAssociation = createTerrainProviderAssociation(terrainProvider, terrainProvidersWithDetails.length);
    
    terrainProvidersWithDetails.push(newTerrainProviderAssociation);
    terrainProvidersWithDetails = [...terrainProvidersWithDetails];
    hasChanges = true;

    draggedItem = null;
  }

  function getDropIndicatorStyle(type: 'terrain-provider', id: number) {
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
      const operations: TerrainProviderBulkOperation[] = terrainProvidersWithDetails.map((terrainProvider) => ({
        action: terrainProvider.isNew ? 'create' : 'update',
        tool_id: terrainProvider.tool_id,
        content_id: terrainProvider.content_id,
        sort_order: terrainProvider.sort_order
      }));

      // Add deleted terrain providers
      if ((window as any)._deletedTerrainProviderIds && Array.isArray((window as any)._deletedTerrainProviderIds)) {
        for (const deletedId of (window as any)._deletedTerrainProviderIds) {
          operations.push({
            action: 'delete',
            tool_id: 0, // Will be handled by backend
            content_id: deletedId,
            sort_order: 0
          });
        }
      }

      await bulkUpdateDigitalTwinTerrainProviders(digitalTwinId, { operations });

      // After successful save, mark all terrain providers as no longer new
      terrainProvidersWithDetails.forEach((terrainProvider) => {
        terrainProvider.isNew = false;
      });

      // Clear deleted terrain provider IDs after successful save
      if ((window as any)._deletedTerrainProviderIds) {
        (window as any)._deletedTerrainProviderIds = [];
      }

      hasChanges = false;
      originalData = deepClone(terrainProvidersWithDetails);

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
    terrainProvidersWithDetails = deepClone(originalData);
    hasChanges = false;
  }

  function showDeleteConfirmation(terrainProvider: TerrainProviderWithAssociation) {
    terrainProviderToDelete = terrainProvider;
    if (skipDeleteTerrainProviderConfirm) {
      handleDeleteTerrainProviderModalConfirm({ doNotAskAgain: false });
    } else {
      deleteTerrainProviderModalShow = true;
    }
  }

  function handleDeleteTerrainProviderModalCancel() {
    deleteTerrainProviderModalShow = false;
    terrainProviderToDelete = null;
  }

  function handleDeleteTerrainProviderModalConfirm(detail: { doNotAskAgain: boolean }) {
    if (terrainProviderToDelete) {
      removeTerrainProvider(terrainProviderToDelete);
      if (detail.doNotAskAgain) {
        skipDeleteTerrainProviderConfirm = true;
        sessionStorage.setItem('skipDeleteTerrainProviderConfirm', 'true');
      }
    }
    deleteTerrainProviderModalShow = false;
    terrainProviderToDelete = null;
  }

  function removeTerrainProvider(terrainProvider: TerrainProviderWithAssociation) {
    const index = terrainProvidersWithDetails.findIndex(tp => tp.content_id === terrainProvider.content_id);
    if (index !== -1) {
      terrainProvidersWithDetails.splice(index, 1);
      
      // Update sort orders
      terrainProvidersWithDetails.forEach((tp, i) => {
        tp.sort_order = i;
      });
      
      // Track deleted terrain provider for bulk API call (only if it's not a new terrain provider)
      if (!terrainProvider.isNew) {
        if (!(window as any)._deletedTerrainProviderIds) {
          (window as any)._deletedTerrainProviderIds = [];
        }
        (window as any)._deletedTerrainProviderIds.push(terrainProvider.content_id);
      }
      
      terrainProvidersWithDetails = [...terrainProvidersWithDetails];
      hasChanges = true;
    }
  }

  function handleTerrainProviderCreated(event: CustomEvent<TerrainProvider>) {
    const newTerrainProvider = event.detail;
    // Refresh the catalog to include the new terrain provider
    allTerrainProviders = [...allTerrainProviders, newTerrainProvider];
    catalogTerrainProviders = [...catalogTerrainProviders, newTerrainProvider];
  }

  // Cesium configuration functions
  async function loadCesiumConfiguration() {
    isLoadingConfig = true;
    try {
      const config = await fetchCesiumConfiguration(digitalTwinId);
      cesiumConfig = config;
    } catch (err) {
      console.error('Error loading cesium configuration:', err);
      cesiumConfig = null;
    } finally {
      isLoadingConfig = false;
    }
  }

  function openCesiumConfig() {
    cesiumConfigModalRef.showModal();
  }

  async function handleCesiumConfigSave(event: CustomEvent<CesiumConfiguration>) {
    try {
      await updateCesiumConfiguration(digitalTwinId, event.detail);
      cesiumConfig = event.detail;
      successBanner?.show();
    } catch (error) {
      console.error('Failed to save cesium configuration:', error);
      errorBanner?.show();
    }
  }

  function handleCesiumConfigCancel() {
    // Modal will close automatically
  }
</script>

<DeleteModal
  show={deleteTerrainProviderModalShow}
  title="Terrain Provider verwijderen"
  message="Weet je zeker dat je deze terrain provider wilt verwijderen uit de digital twin?"
  confirmLabel="Verwijder"
  cancelLabel="Annuleer"
  showCheckbox={true}
  checkboxLabel="Niet meer vragen deze sessie"
  onconfirm={handleDeleteTerrainProviderModalConfirm}
  oncancel={handleDeleteTerrainProviderModalCancel}
/>

<CreateTerrainProviderModal
  bind:this={createTerrainProviderModalRef}
  on:created={handleTerrainProviderCreated}
/>

<CesiumConfigModal
  bind:this={cesiumConfigModalRef}
  config={cesiumConfig || undefined}
  on:save={handleCesiumConfigSave}
  on:cancel={handleCesiumConfigCancel}
/>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Terrain Providers succesvol opgeslagen!"
/>

<AlertBanner
  bind:this={errorBanner}
  type="error"
  message="Er is een fout opgetreden bij het opslaan van de terrain providers."
/>

<div class="flex h-full gap-4">
  <!-- Main content -->
  <div class="flex-1 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold">Terrain Providers</h2>
        <p class="text-base-content/70 text-sm">
          Sleep terrain providers om ze te herordenen
        </p>
      </div>

      <!-- Actions: Cesium Config + Save/Reset -->
      <div class="flex gap-2">
        <button 
          class="btn btn-secondary" 
          onclick={openCesiumConfig}
          disabled={isLoadingConfig}
          title="Configureer Cesium terrain instellingen"
        >
          {#if isLoadingConfig}
            <span class="loading loading-spinner loading-xs"></span>
          {:else}
            <img src="/icons/settings-white.svg" alt="Configureer" class="h-5 w-5" />
          {/if}
          Cesium Instellingen
          {#if cesiumConfig}
            <div class="badge badge-primary badge-xs ml-1"></div>
          {/if}
        </button>
        
        {#if hasChanges}
          <button class="btn btn-ghost" onclick={resetChanges} disabled={isSaving}>
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

    {#if isLoading}
      <div class="flex items-center justify-center py-12">
        <span class="loading loading-spinner loading-lg"></span>
        <span class="ml-4 text-lg">Laden...</span>
      </div>
    {:else if error}
      <div class="alert alert-error">
        <img src="/icons/circle-alert.svg" alt="Error" class="h-6 w-6" />
        <span>{error}</span>
      </div>
    {:else}
      <div class="bg-base-100 border-base-300 rounded-lg border p-6">
        {#if terrainProvidersWithDetails.length === 0}
          <div 
            class="border-2 border-dashed border-base-300 rounded-lg p-12 text-center text-base-content/50 transition-colors {draggedItem?.type === 'catalog-terrain-provider' ? 'border-primary bg-primary/5' : ''}"
            role="region"
            ondragover={(e) => {
              e.preventDefault();
              if (!draggedItem && (window as any).catalogDragData?.type === 'catalog-terrain-provider') {
                draggedItem = (window as any).catalogDragData;
              }
            }}
            ondrop={handleCatalogDrop}
          >
            <img src="/icons/globe.svg" alt="Geen terrain providers" class="mx-auto mb-4 h-16 w-16 opacity-50" />
            <h3 class="text-lg font-medium mb-2">Geen Terrain Providers</h3>
            <p class="mb-4">Sleep terrain providers vanuit de catalogus hiernaartoe om ze toe te voegen.</p>
            <div class="inline-flex items-center gap-2 text-sm text-base-content/40">
              Sleep & laat los
            </div>
          </div>
        {:else}
          <div class="space-y-2">
            {#each terrainProvidersWithDetails as terrainProvider, index}
              <div
                class="hover:bg-base-200 relative flex cursor-move items-center gap-3 rounded-lg border border-transparent p-3 transition-all {draggedItem?.type === 'terrain-provider' && draggedItem?.id === terrainProvider.content_id ? 'opacity-50' : ''}"
                draggable="true"
                use:dragStartAction={{
                  item: { type: 'catalog-terrain-provider' as 'catalog-terrain-provider', id: terrainProvider.content_id, terrainProvider: { id: terrainProvider.content_id, title: terrainProvider.title, url: terrainProvider.url, vertexNormals: terrainProvider.vertexNormals } },
                  type: 'terrain-provider',
                  dataKey: 'application/json',
                  effectAllowed: 'move',
                  onDragStart: () => {
                    draggedItem = { type: 'terrain-provider', id: terrainProvider.content_id };
                  }
                }}
                ondragover={(e) => handleDragOver(e, index)}
                ondragleave={handleDragLeave}
                ondrop={(e) => handleDrop(e, index)}
                role="listitem"
              >
                <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-5 w-5 flex-shrink-0" />
                <img src="/icons/globe.svg" alt="Terrain Provider" class="h-6 w-6 flex-shrink-0 text-primary" />
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-medium truncate">{terrainProvider.title}</span>
                    {#if terrainProvider.isNew}
                      <span class="badge badge-success badge-xs">nieuw</span>
                    {/if}
                  </div>
                  <div class="text-base-content/60 truncate text-sm">{terrainProvider.url}</div>
                  {#if terrainProvider.vertexNormals}
                    <div class="text-base-content/40 text-xs">Vertex Normals: {terrainProvider.vertexNormals}</div>
                  {/if}
                </div>
                <span class="text-base-content/40 text-xs">#{terrainProvider.sort_order}</span>
                <button
                  class="btn btn-ghost btn-sm"
                  onclick={() => showDeleteConfirmation(terrainProvider)}
                  title="Verwijder terrain provider"
                  aria-label="Verwijder terrain provider"
                >
                  <img src="/icons/trash-2.svg" alt="Verwijder" class="h-4 w-4 text-error" />
                </button>

                <!-- Drop indicators -->
                {#if getDropIndicatorStyle('terrain-provider', terrainProvider.content_id).show}
                  {@const indicator = getDropIndicatorStyle('terrain-provider', terrainProvider.content_id)}
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
    {/if}
  </div>

  <!-- Catalog sidebar -->
  <div class="w-80 space-y-4">
    <div class="bg-base-100 border-base-300 h-full rounded-lg border p-4">
      <div class="space-y-4">
        <!-- Header -->
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold">Terrain Provider Catalogus</h3>
            <p class="text-base-content/70 text-sm">
              Sleep terrain providers naar de digital twin
            </p>
          </div>
          <button
            class="btn btn-primary btn-sm"
            onclick={() => createTerrainProviderModalRef.showModal()}
            title="Nieuwe terrain provider aanmaken"
          >
            <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
            Nieuwe
          </button>
        </div>

        <!-- Search -->
        <div class="relative">
          <img src="/icons/search.svg" alt="Zoeken" class="text-base-content/50 absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 transform" />
          <input
            type="text"
            placeholder="Zoek terrain providers..."
            class="input input-bordered input-sm w-full pl-10"
            bind:value={catalogSearchTerm}
          />
        </div>

        <!-- Terrain Provider List -->
        <div class="max-h-96 space-y-2 overflow-y-auto">
          {#if catalogIsLoading}
            <div class="flex items-center justify-center py-8">
              <span class="loading loading-spinner loading-sm"></span>
              <span class="ml-2 text-sm">Laden...</span>
            </div>
          {:else if catalogError}
            <div class="alert alert-error alert-sm">
              <span class="text-sm">{catalogError}</span>
            </div>
          {:else if filteredCatalogTerrainProviders.length === 0}
            <div class="text-base-content/50 py-8 text-center">
              <img src="/icons/globe.svg" alt="Geen terrain providers" class="mx-auto mb-2 h-8 w-8 opacity-50" />
              <p class="text-sm">
                {catalogSearchTerm
                  ? 'Geen terrain providers gevonden voor deze zoekopdracht'
                  : 'Alle beschikbare terrain providers zijn al toegevoegd'}
              </p>
            </div>
          {:else}
            {#each filteredCatalogTerrainProviders as terrainProvider}
              <div
                class="hover:bg-base-200 hover:border-base-300 group flex cursor-move items-center gap-3 rounded border border-transparent p-3 text-sm transition-colors"
                use:dragStartAction={{
                  item: { type: 'catalog-terrain-provider' as 'catalog-terrain-provider', id: terrainProvider.id, terrainProvider },
                  type: 'catalog-terrain-provider',
                  dataKey: 'application/json',
                  effectAllowed: 'copy',
                  globalKey: 'catalogDragData',
                  onDragStart: (item) => {
                    draggedItem = item;
                  }
                }}
                draggable="true"
                role="listitem"
              >
                <img src="/icons/globe.svg" alt="Terrain Provider" class="h-5 w-5 flex-shrink-0 text-primary" />
                <div class="min-w-0 flex-1">
                  <div class="truncate font-medium">{terrainProvider.title}</div>
                  <div class="text-base-content/60 truncate text-xs">{terrainProvider.url}</div>
                  {#if terrainProvider.vertexNormals}
                    <div class="text-base-content/40 text-xs">Vertex Normals</div>
                  {/if}
                </div>
                <button
                  class="btn btn-ghost btn-xs opacity-0 transition-opacity group-hover:opacity-100 hover:opacity-100"
                  onclick={(e) => {
                    e.stopPropagation();
                    const newTerrainProviderAssociation = createTerrainProviderAssociation(terrainProvider, terrainProvidersWithDetails.length);
                    terrainProvidersWithDetails.push(newTerrainProviderAssociation);
                    terrainProvidersWithDetails = [...terrainProvidersWithDetails];
                    hasChanges = true;
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
            {filteredCatalogTerrainProviders.length} beschikbare terrain providers
            {#if usedTerrainProviderIds.length > 0}
              • {usedTerrainProviderIds.length} al toegevoegd
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
