<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { updateStory, fetchTerrainProviders, fetchLayers } from '$lib/api';
  import type { Story, TerrainProvider, StoryStep, RequiredLayer, StoryChapter } from '$lib/types/tool';
  import type { Layer } from '$lib/types/layer';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  export let story: Story | null = null;
  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ updated: Story }>();

  // Basic story fields
  let name = '';
  let description = '';
  let width = '600px';
  let force2DMode = false;
  let staticCamera = true;
  let requestPolygonArea = {
    enabled: false,
    statisticsApi: ''
  };
  let baseLayerId = '';
  let missingFields: string[] = [];
  function resetModal() {
    name = '';
    description = '';
    width = '600px';
    force2DMode = false;
    staticCamera = true;
    requestPolygonArea = { enabled: false, statisticsApi: '' };
    baseLayerId = '';
    chapters = [createNewChapter(0)];
    activeChapterIndex = 0;
    activeStepIndex = 0;
    missingFields = [];
    errorBanner?.hide?.();
    successBanner?.hide?.();
  }

  // Available options
  let availableTerrainProviders: TerrainProvider[] = [];
  let availableLayers: Layer[] = [];
  let stepPositionOpen = false;

  // Base layer selection
  let baseLayerType: 'background' | 'feature' = 'background';
  let baseLayerSearchTerm = '';
  let showBaseLayerSelector = false;

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

  export function showModal(s: Story) {
    story = s;
    name = s.name || '';
    description = s.description || '';
    if (s.content) {
      width = s.content.width || '600px';
      force2DMode = s.content.force2DMode ?? false;
      staticCamera = s.content.staticCamera ?? false;
      requestPolygonArea = typeof s.content.requestPolygonArea === 'object'
        ? s.content.requestPolygonArea
        : { enabled: !!s.content.requestPolygonArea, statisticsApi: '' };
      baseLayerId = s.content.baseLayerId ?? '';
      if (s.content.chapters && Array.isArray(s.content.chapters)) {
        chapters = s.content.chapters.map((chapter: any, index: number) => ({
          id: chapter.id && !chapter.id.toString().includes('1755') ? chapter.id : (index + 1).toString(),
          title: chapter.title || '',
          buttonText: chapter.buttonText || '',
          steps: chapter.steps ? chapter.steps.map((step: any) => ({
            title: step.title || '',
            html: step.html || '',
            globeOpacity: step.globeOpacity || 100,
            terrain: step.terrain || (availableTerrainProviders[0]?.title || ''),
            camera: {
              x: step.camera?.x || 0,
              y: step.camera?.y || 0,
              z: step.camera?.z || 0,
              heading: step.camera?.heading || 0,
              pitch: step.camera?.pitch || 0,
              duration: step.camera?.duration || 1.5
            },
            layers: step.layers ? step.layers.filter((layer: any) => typeof layer === 'string' || !layer.title).map((layer: any) => layer.id || layer).filter(Boolean) : [],
            requiredLayers: step.layers ? step.layers.filter((layer: any) => typeof layer === 'object' && layer.title).map((l: any) => ({
              id: l.id,
              title: l.title,
              opacity: l.opacity ?? 100,
              style: l.style ?? ''
            })) : [],
            _activeTab: 0
          })) : [createNewStep()]
        }));
      } else {
        chapters = [createNewChapter(0)];
      }
    } else {
      width = '600px';
      force2DMode = false;
      staticCamera = false;
      requestPolygonArea = { enabled: false, statisticsApi: '' };
      baseLayerId = '';
      chapters = [createNewChapter(0)];
    }
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
    chapters = [...chapters];
  }

  function removeStep(chapterIndex: number, stepIndex: number) {
    if (chapters[chapterIndex].steps.length <= 1) return;
    chapters[chapterIndex].steps = chapters[chapterIndex].steps.filter((_, i) => i !== stepIndex);
    if (activeStepIndex >= chapters[chapterIndex].steps.length) {
      activeStepIndex = chapters[chapterIndex].steps.length - 1;
    }
    chapters = [...chapters];
  }

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

  // Base layer selection functions
  function selectBaseLayer(layer: Layer, type: 'background' | 'feature') {
    baseLayerId = layer.id.toString();
    baseLayerType = type;
    showBaseLayerSelector = false;
    baseLayerSearchTerm = '';
  }

  // Reactive variable for selected base layer name
  $: selectedBaseLayerName = (() => {
    if (!baseLayerId) {
      return 'Geen laag geselecteerd';
    }
    
    const layer = availableLayers.find(l => l.id.toString() === baseLayerId || l.id === parseInt(baseLayerId));
    return layer ? layer.title : 'Onbekende laag';
  })();

  $: availableBackgroundLayers = availableLayers.filter(layer => layer.isBackground === true);
  $: availableFeatureLayers = availableLayers.filter(layer => layer.isBackground !== true);

  $: filteredBaseLayers = baseLayerType === 'background' 
    ? availableBackgroundLayers.filter(layer => 
        baseLayerSearchTerm.trim() === '' || 
        layer.title.toLowerCase().includes(baseLayerSearchTerm.trim().toLowerCase())
      )
    : availableFeatureLayers.filter(layer => 
        baseLayerSearchTerm.trim() === '' || 
        layer.title.toLowerCase().includes(baseLayerSearchTerm.trim().toLowerCase())
      );

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

  function handleLayerChange(layerId: string, checked: boolean) {
    if (!currentStep) return;
    if (checked) {
      currentStep.layers = [...currentStep.layers, layerId];
    } else {
      currentStep.layers = currentStep.layers.filter(l => l !== layerId);
    }
    chapters = [...chapters];
  }

  function getMissingRequiredFields(): string[] {
    const fields: { label: string; value: any }[] = [
      { label: 'Naam', value: name }
    ];
    return fields.filter(f => !f.value || (typeof f.value === 'string' && !f.value.trim())).map(f => f.label);
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!story) return;

    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) {
      errorBanner?.show();
      return;
    }

    const content = {
      width,
      force2DMode,
      staticCamera,
      requestPolygonArea,
      baseLayerId,
      chapters: chapters.map(chapter => ({
        id: chapter.id,
        title: chapter.title,
        buttonText: chapter.buttonText,
        steps: chapter.steps.map(step => {
          // Merge requiredLayers into layers, preserving all layer info
          const mergedLayers = [
            ...step.layers.map(layerId => ({ id: layerId })),
            ...((step.requiredLayers && step.requiredLayers.length > 0)
              ? step.requiredLayers.map((l: RequiredLayer) => ({
                  id: l.id,
                  title: l.title,
                  opacity: l.opacity,
                  style: l.style
                }))
              : [])
          ];
          return {
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
            layers: mergedLayers
          };
        })
      }))
    };

    const payload = {
      name,
      description,
      content,
      last_updated: new Date().toISOString()
    };

    try {
      const updated = await updateStory(String(story.id), payload);
      dispatch('updated', updated);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Update failed', error);
    }
  }

  $: currentStep = chapters[activeChapterIndex]?.steps[activeStepIndex];
  $: if (currentStep && typeof currentStep._activeTab !== 'number') currentStep._activeTab = 0;
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Story succesvol bijgewerkt!"
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
  <div class="form-control mb2 col-span-12">
    <h3 class="mb-4 text-lg font-bold">Story bewerken</h3>
    <MissingRequiredFields {missingFields} />
  </div>

    <!-- Basic Story Information -->
    <div class="col-span-12 grid grid-cols-4 gap-4 items-center">
      <label for="name" class="text-right font-semibold">
        Naam <span class="text-error">*</span>:
        <HelpTooltip tip="De naam van de story. Dit is verplicht." position="right" />
      </label>
      <input id="name" class="input input-bordered col-span-3 w-full" bind:value={name} />

      <label for="description" class="text-right font-semibold">
        Beschrijving:
        <HelpTooltip tip="Een optionele beschrijving van de story." position="right" />
      </label>
      <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

      <label for="width" class="text-right font-semibold">
        Breedte:
        <HelpTooltip tip="De breedte van de story viewer (bijv. 600px)." position="right" />
      </label>
      <input id="width" class="input input-bordered col-span-3 w-full" bind:value={width} />

      <!-- Checkbox rows -->
      <label for="force-2d-mode" class="text-right font-semibold">
        Force 2D Mode:
        <HelpTooltip tip="Dwingt de viewer om in 2D modus te werken." position="right" />
      </label>
      <input id="force-2d-mode" type="checkbox" class="checkbox checkbox-primary" bind:checked={force2DMode} />
      <div class="col-span-2"></div>

      <label for="static-camera" class="text-right font-semibold">
        Static Camera:
        <HelpTooltip tip="Houdt de cameralocatie hetzelfde na het tekenen en tussen stappen" position="right" />
      </label>
      <input id="static-camera" type="checkbox" class="checkbox checkbox-primary" bind:checked={staticCamera} />
      <div class="col-span-2"></div>

      <label for="request-polygon-area-enabled" class="text-right font-semibold">
        Request Polygon Area:
        <HelpTooltip tip="Voegt een polygoontekenhulpmiddel toe dat in elke stap van het verhaal gegevens opvraagt uit een WMS-laag, indien er een WCS-laag met dezelfde naam bestaat. Bepaal of het hulpmiddel is ingeschakeld en welke API moet worden gebruikt (indien ingeschakeld)." />
      </label>
      <input id="request-polygon-area-enabled" type="checkbox" class="checkbox checkbox-primary" bind:checked={requestPolygonArea.enabled} />
      <div class="col-span-2"></div>

      <label for="request-polygon-area-api" class="text-right font-semibold">
        Statistics API:
        <HelpTooltip tip="De URL van de API die wordt gebruikt voor polygoon statistieken." position="right" />
      </label>
      <input id="request-polygon-area-api" class="input input-bordered col-span-3 w-full" bind:value={requestPolygonArea.statisticsApi} placeholder="https://..." />

      <label for="base-layer" class="text-right font-semibold">
        Base Layer:
        <HelpTooltip tip="De basis laag die standaard wordt getoond in de story." position="right" />
      </label>
      <div class="col-span-3 relative">
        <div class="flex gap-2 items-center">
          <!-- Layer type selector -->
          <select class="select select-bordered w-32" bind:value={baseLayerType} onchange={() => { baseLayerId = ''; }}>
            <option value="background">Achtergrond</option>
            <option value="feature">Feature</option>
          </select>
          
          <!-- Selected layer display / selector button -->
          <button 
            type="button" 
            class="btn btn-outline flex-1 justify-start"
            onclick={() => { showBaseLayerSelector = !showBaseLayerSelector; }}
          >
            {selectedBaseLayerName}
            <img src="/icons/chevron-down.svg" alt="Open" class="h-4 w-4 ml-auto" />
          </button>
        </div>

        <!-- Layer selector dropdown -->
        {#if showBaseLayerSelector}
          <div class="absolute top-full left-0 right-0 mt-1 bg-base-100 border border-base-300 rounded-lg shadow-lg z-50 max-h-64 overflow-hidden">
            <div class="p-2 border-b border-base-300">
              <input
                type="text"
                class="input input-bordered input-sm w-full"
                placeholder={`Zoek ${baseLayerType === 'background' ? 'achtergrond' : 'feature'} laag...`}
                bind:value={baseLayerSearchTerm}
              />
            </div>
            <div class="max-h-48 overflow-y-auto">
              <button 
                type="button" 
                class="w-full text-left p-2 hover:bg-base-200 border-b border-base-300"
                onclick={() => { baseLayerId = ''; showBaseLayerSelector = false; }}
              >
                <div class="font-medium text-gray-500">Geen laag geselecteerd</div>
              </button>
              {#each filteredBaseLayers as layer}
                <button 
                  type="button" 
                  class="w-full text-left p-2 hover:bg-base-200 border-b border-base-300 {baseLayerId === layer.id.toString() ? 'bg-primary text-primary-content' : ''}"
                  onclick={() => selectBaseLayer(layer, baseLayerType)}
                >
                  <div class="font-medium">{layer.title}</div>
                </button>
              {/each}
              {#if filteredBaseLayers.length === 0}
                <div class="p-4 text-center text-gray-500">Geen lagen gevonden</div>
              {/if}
            </div>
          </div>
        {/if}
      </div>
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
              class="btn {activeChapterIndex === chapterIndex ? 'btn-secondary' : 'btn-accent-content'} btn-sm h-10 px-4"
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
            <label for="chapter-title" class="text-right font-semibold">
              Hoofdstuk Titel:
              <HelpTooltip tip="De titel van dit hoofdstuk in de story." position="right" />
            </label>
            <input id="chapter-title" class="input input-bordered col-span-3 w-full" bind:value={chapters[activeChapterIndex].title} placeholder="Titel van hoofdstuk" />
            <label for="chapter-buttontext" class="text-right font-semibold">
              Button Text:
              <HelpTooltip tip="De tekst die wordt getoond op de knop voor dit hoofdstuk." position="right" />
            </label>
            <input id="chapter-buttontext" class="input input-bordered col-span-3 w-full" bind:value={chapters[activeChapterIndex].buttonText} placeholder="Button tekst" />
          </div>
        {/if}
      </div>

      <!-- Steps for Active Chapter -->
      {#if chapters[activeChapterIndex]}
        <div class="border border-base-300 rounded-lg p-4">
          <div class="flex items-center justify-between mb-4">
            <h5 class="font-semibold">Stappen voor Hoofdstuk {activeChapterIndex + 1}</h5>
            <button type="button" class="btn btn-primary btn-sm" onclick={addStep}>
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
                  class="btn {activeStepIndex === stepIndex ? 'btn-accent' : 'btn-accent-content'} btn-sm h-10 px-4"
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

          <!-- Step Content -->
          {#if currentStep}
            <div class="mb-4 flex gap-2">
              <button type="button" class="btn btn-sm {currentStep._activeTab === 0 ? 'btn-outline' : 'btn-accent-content'}" onclick={() => { currentStep._activeTab = 0; chapters = [...chapters]; }}>Details</button>
              <button type="button" class="btn btn-sm {currentStep._activeTab === 1 ? 'btn-outline' : 'btn-accent-content'}" onclick={() => { currentStep._activeTab = 1; chapters = [...chapters]; }}>Benodigde lagen</button>
            </div>
            {#if currentStep._activeTab === 0}
              <div class="grid grid-cols-4 gap-4 items-start">
                <!-- Step Title -->
                <label for="step-title" class="text-right font-semibold">
                  Titel:
                  <HelpTooltip tip="De titel van deze stap in de story." position="right" />
                </label>
                <input 
                  id="step-title"
                  class="input input-bordered col-span-3 w-full" 
                  bind:value={currentStep.title} 
                  placeholder="Stap titel"
                />

                <!-- HTML Content -->
                <label for="step-html" class="text-right font-semibold">
                  HTML Content:
                  <HelpTooltip tip="De tekstinhoud die wordt weergegeven in deze stap. Kan HTML elementen bevatten." position="right" />
                </label>
                <textarea 
                  id="step-html"
                  class="textarea textarea-bordered col-span-3 h-32 w-full" 
                  bind:value={currentStep.html}
                  placeholder="HTML content voor deze stap"
                ></textarea>

                <!-- Globe Opacity -->
                <label for="step-opacity" class="text-right font-semibold">
                  Globe Opacity:
                  <HelpTooltip tip="De transparantie van de globe (0-100). Lagere waarden maken de globe transparanter." position="right" />
                </label>
                <input 
                  id="step-opacity"
                  type="number" 
                  class="input input-bordered col-span-3 w-full" 
                  bind:value={currentStep.globeOpacity}
                  min="0" 
                  max="100"
                />

                <!-- Terrain -->
                <label for="step-terrain" class="text-right font-semibold">
                  Terrain:
                  <HelpTooltip tip="De terrain provider die wordt gebruikt voor deze stap." position="right" />
                </label>
                <select id="step-terrain" class="select select-bordered col-span-3 w-full" bind:value={currentStep.terrain}>
                  {#each availableTerrainProviders as provider}
                    <option value={provider.title}>{provider.title}</option>
                  {/each}
                </select>

                <!-- Camera Position -->
                <label for="step-position-btn" class="text-right font-semibold">
                  Stap positie:
                  <HelpTooltip tip="Selecteer de camera positie voor deze stap. Dit bepaalt waar de gebruiker naar kijkt." position="right" />
                </label>
                <div class="col-span-3">
                  <fieldset>
                    <button
                      type="button"
                      class="m-0 flex w-full cursor-pointer items-center space-x-2 border-0 bg-transparent p-0 text-left font-semibold select-none mb-2"
                      onclick={() => (stepPositionOpen = !stepPositionOpen)}
                      aria-expanded={stepPositionOpen}
                    >
                      {#if stepPositionOpen}
                        <img src="/icons/chevron-down.svg" alt="Open" class="h-5 w-5" />
                      {:else}
                        <img src="/icons/chevron-right.svg" alt="Closed" class="h-5 w-5" />
                      {/if}
                      <span>Stap positie instellingen</span>
                    </button>

                    <!-- Position Selector Button -->
                    <div class="mb-4">
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

                    <!-- Duration field (always visible) -->
                    {#if !stepPositionOpen}
                      <div class="mb-4">
                        <label for="step-duration-collapsed" class="font-medium flex items-center gap-2">
                          Duration
                          <HelpTooltip tip="De duur van de camera animatie in seconden." />
                        </label>
                        <input
                          id="step-duration-collapsed"
                          type="number"
                          step="any"
                          bind:value={currentStep.camera.duration}
                          class="input input-bordered w-full"
                        />
                      </div>
                    {/if}

                    {#if stepPositionOpen}
                      <div class="grid grid-cols-3 gap-4 mb-4">
                        <div>
                          <label for="step-x" class="font-medium flex items-center gap-2">
                            X
                            <HelpTooltip tip="X-coördinaat (longitude) van de camera positie." />
                          </label>
                          <input
                            id="step-x"
                            type="number"
                            step="any"
                            bind:value={currentStep.camera.x}
                            class="input input-bordered w-full"
                          />
                        </div>

                        <div>
                          <label for="step-y" class="font-medium flex items-center gap-2">
                            Y
                            <HelpTooltip tip="Y-coördinaat (latitude) van de camera positie." />
                          </label>
                          <input
                            id="step-y"
                            type="number"
                            step="any"
                            bind:value={currentStep.camera.y}
                            class="input input-bordered w-full"
                          />
                        </div>

                        <div>
                          <label for="step-z" class="font-medium flex items-center gap-2">
                            Z
                            <HelpTooltip tip="Z-coördinaat (hoogte) van de camera positie." />
                          </label>
                          <input
                            id="step-z"
                            type="number"
                            step="any"
                            bind:value={currentStep.camera.z}
                            class="input input-bordered w-full"
                          />
                        </div>

                        <div>
                          <label for="step-heading" class="font-medium flex items-center gap-2">
                            Heading
                            <HelpTooltip tip="De richting waarin de camera kijkt (in graden)." />
                          </label>
                          <input
                            id="step-heading"
                            type="number"
                            step="any"
                            bind:value={currentStep.camera.heading}
                            class="input input-bordered w-full"
                          />
                        </div>

                        <div>
                          <label for="step-pitch" class="font-medium flex items-center gap-2">
                            Pitch
                            <HelpTooltip tip="De kantelhoek van de camera (omhoog/omlaag in graden)." />
                          </label>
                          <input
                            id="step-pitch"
                            type="number"
                            step="any"
                            bind:value={currentStep.camera.pitch}
                            class="input input-bordered w-full"
                          />
                        </div>

                        <!-- Duration field (visible when dropdown is open, positioned to the right of pitch) -->
                        <div>
                          <label for="step-duration-expanded" class="font-medium flex items-center gap-2">
                            Duration
                            <HelpTooltip tip="De duur van de camera animatie in seconden." />
                          </label>
                          <input
                            id="step-duration-expanded"
                            type="number"
                            step="any"
                            bind:value={currentStep.camera.duration}
                            class="input input-bordered w-full"
                          />
                        </div>
                      </div>
                    {/if}
                  </fieldset>
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
                    {#each availableFeatureLayers.filter(layer =>
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
      <button type="button" class="btn btn-ghost" onclick={() => { modalRef.close(); resetModal(); }}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>