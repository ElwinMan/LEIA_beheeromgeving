<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { createStory, fetchTerrainProviders, fetchLayers } from '$lib/api';
  import type { Story, TerrainProvider, StoryStep, RequiredLayer, StoryChapter } from '$lib/types/tool';
  import type { Layer } from '$lib/types/layer';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Story }>();

  // Basic story fields
  let name = '';
  let description = '';
  let width = '600px';
  let force2DMode = false;
  let requestPolygonArea = {
    enabled: false,
    statisticsApi: ''
  };
  let baseLayerId = '';

  // Available options
  let availableTerrainProviders: TerrainProvider[] = [];
  let availableLayers: Layer[] = [];

  let chapters: StoryChapter[] = [];
  let activeChapterIndex = 0;
  let activeStepIndex = 0;

  let catalogSearchTerm: string = '';

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  onMount(async () => {
    try {
      availableTerrainProviders = await fetchTerrainProviders();
      availableLayers = await fetchLayers();
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  });

  export function showModal() {
    name = '';
    description = '';
    width = '600px';
    chapters = [createNewChapter(0)];
    activeChapterIndex = 0;
    activeStepIndex = 0;
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef.showModal();
  }

  function createNewChapter(chapterIndex?: number): StoryChapter {
    const index = chapterIndex !== undefined ? chapterIndex : chapters.length;
    return {
      id: (index + 1).toString(),
      title: '',
      buttonText: '',
      steps: [createNewStep()]
    };
  }

  function createNewStep(): StoryStep {
    return {
      title: '',
      html: '',
      globeOpacity: 100,
      terrain: availableTerrainProviders[0]?.title || '',
      camera: {
        x: 0,
        y: 0,
        z: 0,
        heading: 0,
        pitch: 0,
        duration: 1.5
      },
      layers: [],
      requiredLayers: [],
      _activeTab: 0
    };
  }

  function addChapter() {
    chapters = [...chapters, createNewChapter(chapters.length)];
    activeChapterIndex = chapters.length - 1;
    activeStepIndex = 0;
  }

  function removeChapter(index: number) {
    if (chapters.length <= 1) return;
    chapters = chapters.filter((_, i) => i !== index);
    if (activeChapterIndex >= chapters.length) {
      activeChapterIndex = chapters.length - 1;
    }
    activeStepIndex = 0;
  }

  function addStep() {
    chapters[activeChapterIndex].steps = [...chapters[activeChapterIndex].steps, createNewStep()];
    activeStepIndex = chapters[activeChapterIndex].steps.length - 1;
    chapters = [...chapters]; // Trigger reactivity
  }

  function removeStep(chapterIndex: number, stepIndex: number) {
    if (chapters[chapterIndex].steps.length <= 1) return;
    chapters[chapterIndex].steps = chapters[chapterIndex].steps.filter((_, i) => i !== stepIndex);
    if (activeStepIndex >= chapters[chapterIndex].steps.length) {
      activeStepIndex = chapters[chapterIndex].steps.length - 1;
    }
    chapters = [...chapters]; // Trigger reactivity
  }


  // Required layers logic (per step)
  function addRequiredLayerToStep(layer: Layer) {
    if (!currentStep.requiredLayers.find((l: RequiredLayer) => l.id === layer.id.toString())) {
      currentStep.requiredLayers = [
        ...currentStep.requiredLayers,
        {
          id: layer.id.toString(),
          title: layer.title,
          opacity: 100,
          style: ''
        }
      ];
      chapters = [...chapters];
    }
  }

  function removeRequiredLayerFromStep(index: number) {
    currentStep.requiredLayers = currentStep.requiredLayers.filter((_: RequiredLayer, i: number) => i !== index);
    chapters = [...chapters];
  }

  function updateRequiredLayerOpacityInStep(index: number, value: number) {
    currentStep.requiredLayers[index].opacity = value;
    currentStep.requiredLayers = [...currentStep.requiredLayers];
    chapters = [...chapters];
  }

  function updateRequiredLayerStyleInStep(index: number, value: string) {
    currentStep.requiredLayers[index].style = value;
    currentStep.requiredLayers = [...currentStep.requiredLayers];
    chapters = [...chapters];
  }

  // Layer checkbox logic for step
  function handleLayerChange(layerId: string, checked: boolean) {
    if (!currentStep) return;
    if (checked) {
      currentStep.layers = [...currentStep.layers, layerId];
    } else {
      currentStep.layers = currentStep.layers.filter(l => l !== layerId);
    }
    chapters = [...chapters];
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (!name.trim()) {
      errorBanner?.show();
      return;
    }


    const content = {
      width,
      force2DMode,
      requestPolygonArea,
      baseLayerId,
      chapters: chapters.map(chapter => ({
        id: chapter.id,
        title: chapter.title,
        buttonText: chapter.buttonText,
        steps: chapter.steps.map(step => ({
          title: step.title,
          html: step.html,
          globeOpacity: step.globeOpacity,
          terrain: step.terrain,
          camera: {
            x: step.camera.x,
            y: step.camera.y,
            z: step.camera.z,
            heading: step.camera.heading,
            pitch: step.camera.pitch,
            duration: step.camera.duration
          },
          layers: step.layers.map(layerId => ({ id: layerId })),
          requiredLayers: step.requiredLayers ? step.requiredLayers.map((l: RequiredLayer) => ({
            id: l.id,
            title: l.title,
            opacity: l.opacity,
            style: l.style
          })) : []
        }))
      }))
    };

    const payload = {
      name,
      description,
      content
    };

    try {
      const newStory = await createStory(payload);
      dispatch('created', newStory);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Story creation failed', error);
    }
  }

  $: currentStep = chapters[activeChapterIndex]?.steps[activeStepIndex];
  $: if (currentStep && typeof currentStep._activeTab !== 'number') currentStep._activeTab = 0;
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Story succesvol aangemaakt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Naam is verplicht!"
  />

  <form
    onsubmit={handleSubmit}
    class="modal-box w-full max-w-6xl grid grid-cols-12 gap-4"
  >
    <h3 class="col-span-12 mb-4 text-lg font-bold">Nieuwe Story Aanmaken</h3>

    <!-- Basic Story Information (full width) -->
    <div class="col-span-12 grid grid-cols-4 gap-4 items-center">
      <label for="name" class="text-right font-semibold">Naam:</label>
      <input id="name" class="input input-bordered col-span-3 w-full" bind:value={name} required />

      <label for="description" class="text-right font-semibold">Beschrijving:</label>
      <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

      <label for="width" class="text-right font-semibold">Breedte:</label>
      <input id="width" class="input input-bordered col-span-3 w-full" bind:value={width} />

      <label for="force-2d-mode" class="text-right font-semibold">Force 2D Mode:</label>
      <input id="force-2d-mode" type="checkbox" class="checkbox checkbox-primary" bind:checked={force2DMode} />

      <label for="request-polygon-area-enabled" class="text-right font-semibold">Request Polygon Area:</label>
      <input id="request-polygon-area-enabled" type="checkbox" class="checkbox checkbox-primary" bind:checked={requestPolygonArea.enabled} />
      <label for="request-polygon-area-api" class="text-right font-semibold">Statistics API:</label>
      <input id="request-polygon-area-api" class="input input-bordered col-span-3 w-full" bind:value={requestPolygonArea.statisticsApi} placeholder="https://..." />

      <label for="base-layer" class="text-right font-semibold">Base Layer:</label>
      <select id="base-layer" class="select select-bordered col-span-3" bind:value={baseLayerId}>
        <option value="">-- Selecteer een laag --</option>
        {#each availableLayers as layer}
          <option value={layer.id}>{layer.title}</option>
        {/each}
      </select>
    </div>

    <!-- Chapters and Steps Management -->
    <div class="col-span-12 mt-6">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-lg font-semibold">Hoofdstukken & Stappen</h4>
        <button type="button" class="btn btn-primary btn-sm" onclick={addChapter}>
          <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
          Hoofdstuk Toevoegen
        </button>
      </div>

      <!-- Chapter Tabs -->
      <div class="flex flex-wrap gap-2 mb-4">
        {#each chapters as chapter, chapterIndex}
          <div class="relative">
            <button
              type="button"
              class="btn {activeChapterIndex === chapterIndex ? 'btn-primary' : 'btn-outline btn-neutral'} btn-sm h-10 px-4"
              onclick={() => { activeChapterIndex = chapterIndex; activeStepIndex = 0; }}
            >
              <img src="/icons/folder.svg" alt="Hoofdstuk" class="h-4 w-4 mr-2" />
              {chapter.title ? chapter.title : `Hoofdstuk ${chapterIndex + 1}`}
            </button>
            {#if chapters.length > 1}
              <button
                type="button"
                class="btn btn-error btn-xs absolute -top-2 -right-2 rounded-full w-5 h-5 p-0 min-h-0"
                onclick={(e) => { e.stopPropagation(); removeChapter(chapterIndex); }}
                title="Verwijder hoofdstuk"
              >
                <img src="/icons/x.svg" alt="Verwijder" class="h-3 w-3" />
              </button>
            {/if}
          </div>
        {/each}
      </div>

      <!-- Chapter Title/ButtonText Inputs -->
      <div class="mb-4">
        {#if chapters[activeChapterIndex]}
          <div class="grid grid-cols-4 gap-4 items-center">
            <label for="chapter-title" class="text-right font-semibold">Hoofdstuk Titel:</label>
            <input id="chapter-title" class="input input-bordered col-span-3 w-full" bind:value={chapters[activeChapterIndex].title} placeholder="Titel van hoofdstuk" />
            <label for="chapter-buttontext" class="text-right font-semibold">Button Text:</label>
            <input id="chapter-buttontext" class="input input-bordered col-span-3 w-full" bind:value={chapters[activeChapterIndex].buttonText} placeholder="Button tekst" />
          </div>
        {/if}
      </div>

      <!-- Steps for Active Chapter -->
      {#if chapters[activeChapterIndex]}
        <div class="border border-base-300 rounded-lg p-4">
          <div class="flex items-center justify-between mb-4">
            <h5 class="font-semibold">Stappen voor Hoofdstuk {activeChapterIndex + 1}</h5>
            <button type="button" class="btn btn-secondary btn-sm" onclick={addStep}>
              <img src="/icons/plus.svg" alt="Voeg toe" class="h-4 w-4" />
              Stap Toevoegen
            </button>
          </div>

          <!-- Step Tabs -->
          <div class="flex flex-wrap gap-2 mb-4">
            {#each chapters[activeChapterIndex].steps as step, stepIndex}
              <div class="relative">
                <button
                  type="button"
                  class="btn {activeStepIndex === stepIndex ? 'btn-secondary' : 'btn-outline btn-neutral'} btn-sm h-10 px-4"
                  onclick={() => activeStepIndex = stepIndex}
                >
                  <img src="/icons/file-text.svg" alt="Stap" class="h-4 w-4 mr-2" />
                  Stap {stepIndex + 1}
                </button>
                {#if chapters[activeChapterIndex].steps.length > 1}
                  <button
                    type="button"
                    class="btn btn-error btn-xs absolute -top-2 -right-2 rounded-full w-5 h-5 p-0 min-h-0"
                    onclick={(e) => { e.stopPropagation(); removeStep(activeChapterIndex, stepIndex); }}
                    title="Verwijder stap"
                  >
                    <img src="/icons/x.svg" alt="Verwijder" class="h-3 w-3" />
                  </button>
                {/if}
              </div>
            {/each}
          </div>

          <!-- Step Content Tabs -->
          {#if currentStep}
            <div class="mb-4 flex gap-2">
              <button type="button" class="btn btn-sm {currentStep._activeTab === 0 ? 'btn-primary' : 'btn-outline'}" onclick={() => { currentStep._activeTab = 0; chapters = [...chapters]; }}>Details</button>
              <button type="button" class="btn btn-sm {currentStep._activeTab === 1 ? 'btn-primary' : 'btn-outline'}" onclick={() => { currentStep._activeTab = 1; chapters = [...chapters]; }}>Benodigde lagen</button>
            </div>
            {#if currentStep._activeTab === 0}
              <div class="grid grid-cols-4 gap-4 items-start">
                <!-- Step Title -->
                <label for="step-title" class="text-right font-semibold">Titel:</label>
                <input 
                  id="step-title"
                  class="input input-bordered col-span-3" 
                  bind:value={currentStep.title} 
                  placeholder="Stap titel"
                />

                <!-- HTML Content -->
                <label for="step-html" class="text-right font-semibold">HTML Content:</label>
                <textarea 
                  id="step-html"
                  class="textarea textarea-bordered col-span-3 h-32" 
                  bind:value={currentStep.html}
                  placeholder="HTML content voor deze stap"
                ></textarea>

                <!-- Globe Opacity -->
                <label for="step-opacity" class="text-right font-semibold">Globe Opacity:</label>
                <input 
                  id="step-opacity"
                  type="number" 
                  class="input input-bordered col-span-3" 
                  bind:value={currentStep.globeOpacity}
                  min="0" 
                  max="100"
                />

                <!-- Terrain -->
                <label for="step-terrain" class="text-right font-semibold">Terrain:</label>
                <select id="step-terrain" class="select select-bordered col-span-3" bind:value={currentStep.terrain}>
                  {#each availableTerrainProviders as provider}
                    <option value={provider.title}>{provider.title}</option>
                  {/each}
                </select>

                <!-- Camera Position -->
                <label for="step-position-btn" class="text-right font-semibold">Stap positie</label>
                <div class="col-span-3 mb-2">
                  <PositionSelector
                    title="Selecteer stap positie"
                    buttonText="Selecteer stap positie op kaart"
                    initialPosition={currentStep.camera}
                    on:coordinatesSelected={(e: CustomEvent<any>) => {
                      currentStep.camera = {
                        ...currentStep.camera,
                        x: e.detail.x,
                        y: e.detail.y,
                        z: e.detail.z,
                        heading: e.detail.heading,
                        pitch: e.detail.pitch,
                        duration: e.detail.duration
                      };
                      chapters = [...chapters];
                    }}
                  />
                </div>

                <!-- X/Y/Z row: empty left, fields right -->
                <div></div>
                <div class="col-span-3 grid grid-cols-3 gap-2 mb-2">
                  <div>
                    <label for="step-x" class="block text-sm font-medium mb-1">X</label>
                    <input id="step-x" type="number" step="any" class="input input-bordered w-full" bind:value={currentStep.camera.x} />
                  </div>
                  <div>
                    <label for="step-y" class="block text-sm font-medium mb-1">Y</label>
                    <input id="step-y" type="number" step="any" class="input input-bordered w-full" bind:value={currentStep.camera.y} />
                  </div>
                  <div>
                    <label for="step-z" class="block text-sm font-medium mb-1">Z</label>
                    <input id="step-z" type="number" step="any" class="input input-bordered w-full" bind:value={currentStep.camera.z} />
                  </div>
                </div>

                <!-- Heading/Pitch/Duration row: empty left, fields right -->
                <div></div>
                <div class="col-span-3 grid grid-cols-3 gap-2">
                  <div>
                    <label for="step-heading" class="block text-sm font-medium mb-1">Heading</label>
                    <input id="step-heading" type="number" step="any" class="input input-bordered w-full" bind:value={currentStep.camera.heading} />
                  </div>
                  <div>
                    <label for="step-pitch" class="block text-sm font-medium mb-1">Pitch</label>
                    <input id="step-pitch" type="number" step="any" class="input input-bordered w-full" bind:value={currentStep.camera.pitch} />
                  </div>
                  <div>
                    <label for="step-duration" class="block text-sm font-medium mb-1">Duration</label>
                    <input id="step-duration" type="number" step="any" class="input input-bordered w-full" bind:value={currentStep.camera.duration} />
                  </div>
                </div>
              </div>
            {:else}
              <!-- Required Layers Tab: split into left (catalog) and right (added layers) -->
              <div class="grid grid-cols-5 gap-4 items-start">
                <!-- Catalog Section (left, 2/5 width) -->
                <div class="col-span-2">
                  <div class="border border-base-300 rounded-lg p-2 max-h-64 overflow-y-auto">
                    <h5 class="font-semibold mb-2">Catalogus</h5>
                    <input
                      type="text"
                      class="input input-bordered w-full mb-2"
                      placeholder="Zoek laag..."
                      bind:value={catalogSearchTerm}
                    />
                    {#each availableLayers.filter(layer =>
                      !currentStep.requiredLayers.find(l => l.id === layer.id.toString()) &&
                      (catalogSearchTerm.trim() === '' || layer.title.toLowerCase().includes(catalogSearchTerm.trim().toLowerCase()))
                    ) as layer}
                      <div class="flex items-center gap-2 mb-2">
                        <span>{layer.title}</span>
                        <button type="button" class="btn btn-xs btn-primary" onclick={() => addRequiredLayerToStep(layer)} title="Voeg toe">
                          +
                        </button>
                      </div>
                    {/each}
                  </div>
                </div>
                <!-- Added Layers Section (right, 3/5 width) -->
                <div class="col-span-3">
                  <div class="border border-base-300 rounded-lg p-2 min-h-64">
                    <h5 class="font-semibold mb-2">Toegevoegde lagen</h5>
                    {#if !currentStep || !currentStep.requiredLayers || currentStep.requiredLayers.length === 0}
                      <div class="text-sm text-gray-500">Geen lagen toegevoegd.</div>
                    {:else}
                      {#each currentStep.requiredLayers as reqLayer, i}
                        <div class="flex items-center gap-4 mb-2 w-full">
                          <span class="flex-1 truncate font-medium">{reqLayer.title}</span>
                          <label class="text-sm" for={`opacity-step-${activeChapterIndex}-${activeStepIndex}-${i}`}>Opacity:</label>
                          <input id={`opacity-step-${activeChapterIndex}-${activeStepIndex}-${i}`} type="number" min="0" max="100" class="input input-bordered w-16" bind:value={reqLayer.opacity} oninput={(e: Event) => updateRequiredLayerOpacityInStep(i, +(e.target as HTMLInputElement).value)} />
                          <label class="text-sm" for={`style-step-${activeChapterIndex}-${activeStepIndex}-${i}`}>Style:</label>
                          <input id={`style-step-${activeChapterIndex}-${activeStepIndex}-${i}`} type="text" class="input input-bordered w-24" bind:value={reqLayer.style} oninput={(e: Event) => updateRequiredLayerStyleInStep(i, (e.target as HTMLInputElement).value)} />
                          <button type="button" class="btn btn-xs btn-error" onclick={() => removeRequiredLayerFromStep(i)} title="Verwijder">
                            x
                          </button>
                        </div>
                      {/each}
                    {/if}
                  </div>
                </div>
              </div>
            {/if}
          {/if}
        </div>
      {/if}
    </div>

    <div class="col-span-12 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" onclick={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>