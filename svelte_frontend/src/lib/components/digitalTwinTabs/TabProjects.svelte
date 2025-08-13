<script lang="ts">
  import { onMount } from 'svelte';
  import {
    bulkUpdateDigitalTwinProjects,
    fetchDigitalTwinProjects,
    fetchProjects,
    fetchLayers,
    fetchDigitalTwin
  } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { Project } from '$lib/types/tool';
  import type { Layer } from '$lib/types/layer';
  import type { ProjectWithAssociation, ProjectBulkOperation, ProjectAssociationResponse } from '$lib/types/digitalTwinAssociation';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import DeleteModal from '$lib/components/modals/DeleteModal.svelte';
  import CreateProjectModal from '$lib/components/modals/CreateProjectModal.svelte';
  import { dragStartAction } from '$lib/utils/dragStartAction';
  import { getDropZone } from '$lib/utils/dropZoneUtils';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();

  // State for local digital twin data (can be updated independently)
  let localDigitalTwin = $state<DigitalTwin | null>(digitalTwin);

  // Deep clone function
  function deepClone<T>(obj: T): T {
    return JSON.parse(JSON.stringify(obj));
  }

  // State
  let allProjects = $state<Project[]>([]);
  let projectsWithDetails = $state<ProjectWithAssociation[]>([]);
  let hasChanges = $state(false);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let originalData: ProjectWithAssociation[] = [];
  let isSaving = $state(false);

  // Delete modal state
  let deleteProjectModalShow = $state(false);
  let projectToDelete: ProjectWithAssociation | null = null;
  let skipDeleteProjectConfirm = $state(false);

  // Drag and drop state
  let draggedItem = $state<{
    type: 'project' | 'catalog-project';
    id: number;
    project?: Project;
  } | null>(null);
  let draggedOverItem = $state<{
    type: 'project';
    id: number;
    zone: 'top' | 'middle' | 'bottom';
  } | null>(null);

  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let createProjectModalRef: InstanceType<typeof CreateProjectModal>;

  // Catalog state
  let catalogProjects = $state<Project[]>([]);
  let catalogSearchTerm = $state('');
  let catalogIsLoading = $state(true);
  let catalogError = $state<string | null>(null);
  
  // Layer info tooltip state
  let showLayerInfo: { [key: number]: boolean } = $state({});

  // Get used project IDs for filtering catalog
  let usedProjectIds = $derived(projectsWithDetails.map((p) => p.content_id));

  // Get digital twin layer titles for validation
  let digitalTwinLayerTitles = $derived(
    digitalTwin?.layer_associations.map(assoc => {
      // Find the layer details from allLayers if we have them loaded
      // For now we'll need to track this separately or load layers
      return null; // We'll implement this after loading layers
    }).filter(Boolean) || []
  );

  // Layer validation state
  let allLayers = $state<Layer[]>([]);
  let digitalTwinLayers = $derived(
    localDigitalTwin?.layer_associations.map(assoc => 
      allLayers.find(layer => layer.id === assoc.layer_id)
    ).filter(Boolean) || []
  );
  let digitalTwinLayerTitles_computed = $derived(
    digitalTwinLayers.map(layer => layer?.title).filter(Boolean) || []
  );

  // Check if project can be added (has all required layers)
  function validateProjectLayers(project: Project): { canAdd: boolean; missingLayers: string[] } {
    if (!project.content?.layers || !Array.isArray(project.content.layers)) {
      return { canAdd: true, missingLayers: [] }; // No layer requirements
    }

    const requiredLayers = project.content.layers as string[];
    const missingLayers = requiredLayers.filter(
      layerTitle => !digitalTwinLayerTitles_computed.includes(layerTitle)
    );

    return {
      canAdd: missingLayers.length === 0,
      missingLayers
    };
  }

  onMount(async () => {
    const stored = localStorage.getItem('skipDeleteProjectConfirm');
    skipDeleteProjectConfirm = stored === 'true';
    
    // Load all layers first for validation
    await loadAllLayers();
    // Load digital twin data to get current layer associations
    await loadDigitalTwin();
    // Load catalog projects first, then load associations
    await loadCatalogProjects();
    await loadProjects();
  });

  // Filter catalog projects
  let filteredCatalogProjects = $derived(
    catalogProjects
      .filter(project => 
        !usedProjectIds.includes(project.id) &&
        (catalogSearchTerm === '' || 
         project.name.toLowerCase().includes(catalogSearchTerm.toLowerCase()) ||
         (project.description && project.description.toLowerCase().includes(catalogSearchTerm.toLowerCase()))
        )
      )
      .sort((a, b) => {
        const validationA = validateProjectLayers(a);
        const validationB = validateProjectLayers(b);
        
        // Sort by compatibility first (compatible projects on top)
        if (validationA.canAdd && !validationB.canAdd) return -1;
        if (!validationA.canAdd && validationB.canAdd) return 1;
        
        // Then sort alphabetically by name
        return a.name.localeCompare(b.name);
      })
  );

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

  async function loadProjects() {
    isLoading = true;
    error = null;
    try {
      // Fetch project associations using the API
      const projectAssociations = await fetchDigitalTwinProjects(digitalTwinId);

      if (projectAssociations && projectAssociations.length > 0) {
        projectsWithDetails = projectAssociations
          .sort((a: any, b: any) => a.sort_order - b.sort_order)
          .map((association: any) => {
            const projectDetails = allProjects.find((project) => project.id === association.content_id);
            return {
              tool_id: association.tool_id,
              content_type_id: association.content_type_id,
              content_id: association.content_id,
              sort_order: association.sort_order,
              is_default: association.is_default || false,
              name: projectDetails?.name || `Project ${association.content_id}`,
              description: projectDetails?.description || '',
              content: projectDetails?.content,
              isNew: false
            };
          });
      } else {
        projectsWithDetails = [];
      }
      
      originalData = deepClone(projectsWithDetails);
      hasChanges = false;
    } catch (err) {
      error = 'Failed to load projects';
      console.error('Error loading projects:', err);
    } finally {
      isLoading = false;
    }
  }

  async function loadCatalogProjects() {
    catalogIsLoading = true;
    catalogError = null;
    try {
      const projects = await fetchProjects();
      allProjects = projects;
      catalogProjects = projects;
    } catch (err) {
      catalogError = 'Failed to load project catalog';
      console.error('Error loading catalog projects:', err);
    } finally {
      catalogIsLoading = false;
    }
  }

  function handleDefaultToggle(project: ProjectWithAssociation) {
    // Clear default from all other projects
    projectsWithDetails.forEach(p => {
      if (p.content_id !== project.content_id) {
        p.is_default = false;
      }
    });
    
    // Toggle this project's default status
    project.is_default = !project.is_default;
    
    // Mark data as changed
    hasChanges = true;
  }

  function moveProjectInList(fromIndex: number, toIndex: number) {
    const item = projectsWithDetails[fromIndex];
    
    // Adjust target index if moving forward (to account for removal shifting indices)
    let adjustedToIndex = toIndex;
    if (fromIndex < toIndex) {
      adjustedToIndex = toIndex - 1;
    }
    
    projectsWithDetails.splice(fromIndex, 1);
    projectsWithDetails.splice(adjustedToIndex, 0, item);
    
    // Update sort_order for all items
    projectsWithDetails.forEach((project, index) => {
      project.sort_order = index;
    });
    
    hasChanges = true;
  }

  function handleDragStart(project: Project) {
    draggedItem = { type: 'project', id: project.id, project };
  }

  function handleDragEnd() {
    draggedItem = null;
    draggedOverItem = null;
  }

  function handleDragOver(e: DragEvent, index: number) {
    e.preventDefault();
    if (!draggedItem) return;

    const project = projectsWithDetails[index];
    const listItem = (e.currentTarget as HTMLElement);
    const zone = getDropZone(e, listItem);
    draggedOverItem = { type: 'project', id: project.content_id, zone };
  }

  function handleDragLeave() {
    draggedOverItem = null;
  }

  function getDropIndicatorStyle(type: 'project', id: number) {
    if (!draggedOverItem || draggedOverItem.type !== type || draggedOverItem.id !== id) {
      return { show: false, zone: null };
    }

    return { show: true, zone: draggedOverItem.zone };
  }

    function handleDrop(e: DragEvent, targetIndex: number) {
    e.preventDefault();
    
    if (!draggedItem) return;

    const sourceProject = draggedItem.project;
    if (!sourceProject) return;

    // Validate project layers before allowing drop
    if (draggedItem.type === 'catalog-project') {
      const validation = validateProjectLayers(sourceProject);
      if (!validation.canAdd) {
        // Show error message or prevent drop
        alert(`Dit project kan niet worden toegevoegd. Ontbrekende lagen: ${validation.missingLayers.join(', ')}`);
        handleDragEnd();
        return;
      }
    }

    const existingProject = allProjects.find(p => p.id === sourceProject.id);
    if (!existingProject) return;

    const zone = draggedOverItem?.zone || 'middle';
    let insertIndex = targetIndex;
    
    // Check if project is already in the list to determine direction
    const existingIndex = projectsWithDetails.findIndex(p => p.content_id === sourceProject.id);
    
    if (zone === 'bottom') {
      insertIndex += 1;
    } else if (zone === 'middle' && existingIndex !== -1) {
      // For middle drops of existing items, adjust based on direction
      if (existingIndex < targetIndex) {
        // Moving down: place item below target (target moves up)
        insertIndex = targetIndex + 1;
      }
      // Moving up: place item above target (use targetIndex as-is)
    }

    if (existingIndex !== -1 && draggedItem.type === 'project') {
      // Moving existing project within the list
      moveProjectInList(existingIndex, insertIndex);
    } else if (draggedItem.type === 'catalog-project') {
      // Adding new project from catalog
      const newProject: ProjectWithAssociation = {
        tool_id: parseInt(digitalTwinId),
        content_type_id: 0, // Will be set by backend
        content_id: sourceProject.id,
        sort_order: insertIndex,
        is_default: false,
        name: sourceProject.name,
        description: sourceProject.description,
        content: sourceProject.content,
        isNew: true
      };

      // Insert at the correct position
      projectsWithDetails.splice(insertIndex, 0, newProject);
      
      // Update sort_order for all items after insertion
      projectsWithDetails.forEach((project, index) => {
        project.sort_order = index;
      });
      
      hasChanges = true;
    }

    handleDragEnd();
  }

  function handleCatalogDrop(e: DragEvent) {
    e.preventDefault();
    
    const dragData = (window as any).catalogDragData;
    if (!dragData) return;

    const project = dragData as Project;
    
    // Validate project layers before allowing drop
    const validation = validateProjectLayers(project);
    if (!validation.canAdd) {
      alert(`Dit project kan niet worden toegevoegd. Ontbrekende lagen: ${validation.missingLayers.join(', ')}`);
      delete (window as any).catalogDragData;
      return;
    }

    const existingProject = allProjects.find(p => p.id === project.id);
    if (!existingProject) return;

    const newProject: ProjectWithAssociation = {
      tool_id: 0, // Will be set by backend
      content_type_id: 0, // Will be set by backend
      content_id: project.id,
      sort_order: projectsWithDetails.length,
      is_default: false,
      name: project.name,
      description: project.description,
      content: project.content,
      isNew: true
    };

    projectsWithDetails.push(newProject);
    hasChanges = true;
    
    // Clean up
    delete (window as any).catalogDragData;
  }

  function showDeleteConfirmation(project: ProjectWithAssociation) {
    if (skipDeleteProjectConfirm) {
      removeProject(project);
      return;
    }
    
    projectToDelete = project;
    deleteProjectModalShow = true;
  }

  function handleDeleteProjectModalCancel() {
    deleteProjectModalShow = false;
    projectToDelete = null;
  }

  function handleDeleteProjectModalConfirm(detail: { doNotAskAgain: boolean }) {
    if (detail.doNotAskAgain) {
      skipDeleteProjectConfirm = true;
      localStorage.setItem('skipDeleteProjectConfirm', 'true');
    }
    
    if (projectToDelete) {
      removeProject(projectToDelete);
    }
    deleteProjectModalShow = false;
    projectToDelete = null;
  }

  function removeProject(project: ProjectWithAssociation) {
    const index = projectsWithDetails.findIndex(p => p.content_id === project.content_id);
    if (index > -1) {
      projectsWithDetails.splice(index, 1);
      
      // Update sort_order for remaining items
      projectsWithDetails.forEach((proj, idx) => {
        proj.sort_order = idx;
      });
      
      hasChanges = true;
    }
  }

  async function saveChanges() {
    if (!hasChanges) return;

    isSaving = true;
    try {
      const operations: ProjectBulkOperation[] = [];

      // Handle new projects (create)
      const newProjects = projectsWithDetails.filter(p => p.isNew);
      for (const project of newProjects) {
        operations.push({
          action: 'create',
          tool_id: 1, // Assuming projects tool has ID 1
          content_id: project.content_id,
          sort_order: project.sort_order,
          is_default: project.is_default
        });
      }

      // Handle existing projects (update)
      const existingProjects = projectsWithDetails.filter(p => !p.isNew);
      for (const project of existingProjects) {
        const original = originalData.find(o => o.content_id === project.content_id);
        if (original && (
          original.sort_order !== project.sort_order ||
          original.is_default !== project.is_default
        )) {
          operations.push({
            action: 'update',
            tool_id: project.tool_id,
            content_id: project.content_id,
            sort_order: project.sort_order,
            is_default: project.is_default
          });
        }
      }

      // Handle deleted projects
      for (const original of originalData) {
        const exists = projectsWithDetails.find(p => p.content_id === original.content_id);
        if (!exists) {
          operations.push({
            action: 'delete',
            tool_id: original.tool_id,
            content_id: original.content_id
          });
        }
      }

      if (operations.length > 0) {
        await bulkUpdateDigitalTwinProjects(digitalTwinId, { operations });
      }

      // Reload to get fresh data
      await loadProjects();
      
      successBanner?.show();
      setTimeout(() => successBanner?.hide(), 3000);
      
    } catch (err) {
      console.error('Failed to save projects:', err);
      errorBanner?.show();
      setTimeout(() => errorBanner?.hide(), 5000);
    } finally {
      isSaving = false;
    }
  }

  function resetChanges() {
    projectsWithDetails = deepClone(originalData);
    hasChanges = false;
  }

  function handleProjectCreated(event: CustomEvent<Project>) {
    const newProject = event.detail;
    loadCatalogProjects(); // Refresh catalog
    
    // Optionally add to current list
    const projectWithAssociation: ProjectWithAssociation = {
      tool_id: 0,
      content_type_id: 0,
      content_id: newProject.id,
      sort_order: projectsWithDetails.length,
      is_default: false,
      name: newProject.name,
      description: newProject.description,
      content: newProject.content,
      isNew: true
    };
    
    projectsWithDetails.push(projectWithAssociation);
    hasChanges = true;
  }

  function toggleLayerInfo(projectId: number) {
    showLayerInfo[projectId] = !showLayerInfo[projectId];
  }
</script>

<DeleteModal
  show={deleteProjectModalShow}
  oncancel={handleDeleteProjectModalCancel}
  onconfirm={handleDeleteProjectModalConfirm}
  title="Project verwijderen"
  message="Weet je zeker dat je dit project wilt verwijderen?"
  showCheckbox={true}
  checkboxLabel="Niet meer vragen"
/>

<CreateProjectModal
  bind:this={createProjectModalRef}
  on:created={handleProjectCreated}
/>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Projecten succesvol opgeslagen!"
/>

<AlertBanner
  bind:this={errorBanner}
  type="error"
  message="Er is een fout opgetreden bij het opslaan van de projecten."
/>

<div class="flex h-full gap-4">
  <!-- Main content -->
  <div class="flex-1 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold">Projecten</h2>
        <p class="text-base-content/70">Beheer projecten voor deze digital twin.</p>
      </div>
      
      <div class="flex gap-2">
        <button 
          class="btn btn-primary btn-sm"
          onclick={() => createProjectModalRef.showModal()}
        >
          <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
          Nieuw Project
        </button>
        
        <button 
          class="btn btn-ghost btn-sm"
          class:invisible={!hasChanges}
          onclick={resetChanges}
        >
          <img src="/icons/rotate-ccw.svg" alt="Reset" class="h-4 w-4" />
          Reset
        </button>
        
        <button 
          class="btn btn-sm"
          class:btn-success={hasChanges}
          class:btn-disabled={!hasChanges}
          onclick={saveChanges} 
          disabled={isSaving || !hasChanges}
        >
          {#if isSaving}
            <span class="loading loading-spinner loading-sm"></span>
          {:else}
            <img src="/icons/save.svg" alt="Opslaan" class="h-4 w-4" />
          {/if}
          Opslaan
        </button>
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
          <h3 class="card-title">Actieve Projecten</h3>
          
          {#if projectsWithDetails.length === 0}
            <div 
              class="border-2 border-dashed border-base-300 rounded-lg p-8 text-center text-base-content/50 transition-colors {draggedItem?.type === 'catalog-project' ? 'border-primary bg-primary/5' : ''}"
              role="region"
              ondragover={(e) => {
                e.preventDefault();
                // Try to set draggedItem from catalog data if not already set
                if (!draggedItem && (window as any).catalogDragData) {
                  const catalogData = (window as any).catalogDragData;
                  draggedItem = { type: 'catalog-project', id: catalogData.id, project: catalogData };
                }
              }}
              ondrop={handleCatalogDrop}
            >
              <p>Geen projecten gevonden. Sleep een project hierheen of maak een nieuw project aan.</p>
            </div>
          {:else}
            <div class="space-y-2">
              {#each projectsWithDetails as project, index (project.content_id)}
                {@const fullProject = allProjects.find(p => p.id === project.content_id)}
                {@const validation = fullProject ? validateProjectLayers(fullProject) : { canAdd: true, missingLayers: [] }}
                <div class="relative">
                  <div 
                    class="flex items-center gap-3 p-3 border rounded-lg hover:bg-base-50 transition-colors {draggedItem?.type === 'project' && draggedItem?.id === project.content_id ? 'opacity-50' : ''}"
                    class:border-base-300={validation.canAdd}
                    class:border-error={!validation.canAdd}
                    class:bg-red-50={!validation.canAdd}
                    draggable="true"
                    role="listitem"
                    ondragstart={() => {
                      const foundProject = allProjects.find(p => p.id === project.content_id);
                      if (foundProject) handleDragStart(foundProject);
                    }}
                    ondragend={handleDragEnd}
                    ondragover={(e) => handleDragOver(e, index)}
                    ondragleave={handleDragLeave}
                    ondrop={(e) => handleDrop(e, index)}
                  >
                  <!-- Drag handle -->
                  <div class="cursor-move text-base-content/40">
                    <img src="/icons/grip-vertical.svg" alt="Grip" class="text-base-content/30 h-4 w-4 flex-shrink-0" />
                  </div>

                  <!-- Project icon -->
                  <img src="/icons/folder.svg" alt="Project" class="h-5 w-5 flex-shrink-0" />

                  <!-- Project info -->
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <div class="font-medium">{project.name}</div>
                      {#if project.isNew}
                        <span class="badge badge-success badge-sm">Nieuw</span>
                      {/if}
                      {#if project.is_default}
                        <span class="badge badge-info badge-xs ml-2">Standaard</span>
                      {/if}
                      <!-- Layer validation indicator -->
                      {#if !validation.canAdd}
                        <span class="badge badge-error badge-xs">Ontbrekende lagen</span>
                      {/if}
                    </div>
                    {#if project.description}
                      <div class="text-sm text-base-content/70">{project.description}</div>
                    {/if}
                  </div>

                  <!-- Sort order -->
                  <span class="text-base-content/50 text-xs">#{project.sort_order}</span>

                  <!-- Default toggle -->
                  <button
                    class="btn btn-sm btn-circle"
                    class:btn-secondary={project.is_default}
                    class:btn-outline={!project.is_default}
                    onclick={() => handleDefaultToggle(project)}
                    title={project.is_default ? 'Standaard project' : 'Instellen als standaard'}
                    aria-label={project.is_default ? 'Standaard project' : 'Instellen als standaard'}
                  >
                    <img src="/icons/eye.svg" alt="Project" class="h-5 w-5 flex-shrink-0 text-green-600" />
                  </button>

                  <!-- Actions -->
                  <div class="flex gap-2">
                    <!-- Layer info button -->
                    {#if fullProject}
                      <button
                        class="btn btn-xs"
                        class:btn-error={!validation.canAdd}
                        class:btn-success={validation.canAdd}
                        onclick={() => toggleLayerInfo(project.content_id)}
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
                      onclick={() => showDeleteConfirmation(project)}
                      title="Project verwijderen"
                      aria-label="Project verwijderen"
                    >
                      <img src="/icons/trash-2.svg" alt="Verwijder" class="h-5 w-5" />
                    </button>
                  </div>
                </div>

                <!-- Layer info display -->
                {#if showLayerInfo[project.content_id] && fullProject}
                  {#if !validation.canAdd}
                    <div class="mt-2 p-2 bg-error/10 border border-error/30 rounded text-xs">
                      <div class="font-medium text-error mb-1">Ontbrekende lagen:</div>
                      <div class="text-error font-medium">
                        {validation.missingLayers.join(', ')}
                      </div>
                    </div>
                  {:else}
                    <!-- Show required layers if project has layer requirements -->
                    {#if fullProject.content?.layers && Array.isArray(fullProject.content.layers)}
                      {@const requiredLayers = fullProject.content.layers}
                      {#if requiredLayers.length > 0}
                        <div class="mt-2 p-2 bg-success/10 border border-success/30 rounded text-xs">
                          <div class="font-medium text-success mb-1">Vereiste lagen aanwezig:</div>
                          <div class="text-success">
                            {requiredLayers.join(', ')}
                          </div>
                        </div>
                      {:else}
                        <div class="mt-2 p-2 bg-info/10 border border-info/30 rounded text-xs">
                          <div class="font-medium text-info">Dit project heeft geen laagvereisten.</div>
                        </div>
                      {/if}
                    {:else}
                      <div class="mt-2 p-2 bg-info/10 border border-info/30 rounded text-xs">
                        <div class="font-medium text-info">Dit project heeft geen laagvereisten.</div>
                      </div>
                    {/if}
                  {/if}
                {/if}

                <!-- Absolute positioned drop indicators -->
                {#if getDropIndicatorStyle('project', project.content_id).show}
                  {@const indicator = getDropIndicatorStyle('project', project.content_id)}
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
          {/if}
        </div>
      </div>
    {/if}
  </div>

  <!-- Catalog sidebar -->
  <div class="w-80 space-y-4">
    <div class="card bg-base-100 border-base-300 border">
      <div class="card-body">
        <h3 class="card-title">Project Catalogus</h3>
        
        <!-- Search -->
        <input 
          class="input input-bordered input-sm w-full" 
          placeholder="Zoek projecten..."
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
            {#each filteredCatalogProjects as project (project.id)}
              {@const validation = validateProjectLayers(project)}
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
                  item: project,
                  type: 'project',
                  globalKey: 'catalogDragData',
                  onDragStart: (catalogProject) => {
                    if (validation.canAdd) {
                      draggedItem = { type: 'catalog-project', id: catalogProject.id, project: catalogProject };
                    }
                  }
                }}
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="font-medium text-sm">{project.name}</div>
                    {#if project.description}
                      <div class="text-xs text-base-content/70">{project.description}</div>
                    {/if}
                  </div>
                  
                  {#if !validation.canAdd || (project.content?.layers && project.content.layers.length > 0)}
                    <button
                      class="btn btn-circle btn-xs ml-2 flex-shrink-0"
                      class:btn-error={!validation.canAdd}
                      class:btn-success={validation.canAdd}
                      onclick={() => toggleLayerInfo(project.id)}
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
                
                {#if showLayerInfo[project.id]}
                  {#if !validation.canAdd}
                    <div class="mt-2 p-2 bg-error/10 border border-error/30 rounded text-xs">
                      <div class="font-medium text-error mb-1">Ontbrekende lagen:</div>
                      <div class="text-error font-medium">
                        {validation.missingLayers.join(', ')}
                      </div>
                    </div>
                  {:else if project.content?.layers && project.content.layers.length > 0}
                    <div class="mt-2 p-2 bg-success/10 border border-success/30 rounded text-xs">
                      <div class="font-medium text-success mb-1">Vereiste lagen aanwezig:</div>
                      <div class="text-success font-medium">
                        {project.content.layers.join(', ')}
                      </div>
                    </div>
                  {/if}
                {/if}
              </div>
            {:else}
              <div class="text-center py-4 text-base-content/50">
                <p>Geen projecten beschikbaar</p>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
