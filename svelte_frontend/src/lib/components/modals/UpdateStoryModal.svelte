<script lang="ts">
  import type { Story, TerrainProvider } from '$lib/types/tool';
  import type { Layer } from '$lib/types/layer';
  import { createEventDispatcher, onMount } from 'svelte';
  import { updateStory, fetchTerrainProviders, fetchLayers } from '$lib/api';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

    import PositionSelector from '$lib/components/PositionSelector.svelte';

  export let story: Story | null = null;
  let modalRef: HTMLDialogElement;

  // Basic story fields
  let name = '';
  let description = '';
  let width = '600px';
  let force2DMode = false;
  let requestPolygonArea = false;
  let baseLayerId = '';

  // Available options
  let availableTerrainProviders: TerrainProvider[] = [];
  let availableLayers: Layer[] = [];

  // Story structure
  interface StoryStep {
    title: string;
    html: string;
    globeOpacity: number;
    terrain: string;
    camera: {
      x: number;
      y: number;
      z: number;
      heading: number;
      pitch: number;
      duration: number;
    };
    layers: string[];
  }

  interface StoryChapter {
    id: string;
    steps: StoryStep[];
  }

  let chapters: StoryChapter[] = [];
  let activeChapterIndex = 0;
  let activeStepIndex = 0;

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  const dispatch = createEventDispatcher();

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
    // Parse content structure
    if (s.content) {
      width = s.content.width || '600px';
      force2DMode = s.content.force2DMode ?? false;
      requestPolygonArea = s.content.requestPolygonArea ?? false;
      baseLayerId = s.content.baseLayerId ?? '';
      if (s.content.chapters && Array.isArray(s.content.chapters)) {
        chapters = s.content.chapters.map((chapter: any, index: number) => ({
          id: chapter.id && !chapter.id.toString().includes('1755') ? chapter.id : (index + 1).toString(), // Keep existing clean IDs, fix timestamp IDs
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
            layers: step.layers ? step.layers.map((layer: any) => layer.id || layer).filter(Boolean) : []
          })) : [createNewStep()]
        }));
      } else {
        chapters = [createNewChapter(0)];
      }
    } else {
      width = '600px';
      force2DMode = false;
      requestPolygonArea = false;
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
      layers: []
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

  function handleLayerChange(layerId: string, checked: boolean) {
    const currentStep = chapters[activeChapterIndex].steps[activeStepIndex];
    if (checked) {
      currentStep.layers = [...currentStep.layers, layerId];
    } else {
      currentStep.layers = currentStep.layers.filter(l => l !== layerId);
    }
    chapters = [...chapters]; // Trigger reactivity
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!story) return;

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
          layers: step.layers.map(layerId => ({ id: layerId }))
        }))
      }))
    };

    const payload = {
      name,
      description,
      content
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
    <h3 class="col-span-12 mb-4 text-lg font-bold">Story bewerken</h3>

    <!-- Basic Story Information -->
    <div class="col-span-12 grid grid-cols-4 gap-4 items-center">
      <label for="name" class="text-right font-semibold">Naam:</label>
      <input id="name" class="input input-bordered col-span-3 w-full" bind:value={name} required />

      <label for="description" class="text-right font-semibold">Beschrijving:</label>
      <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

      <label for="width" class="text-right font-semibold">Breedte:</label>
      <input id="width" class="input input-bordered col-span-3 w-full" bind:value={width} />

      <label for="force-2d-mode" class="text-right font-semibold">Force 2D Mode:</label>
      <input id="force-2d-mode" type="checkbox" class="checkbox checkbox-primary" bind:checked={force2DMode} />

      <label for="request-polygon-area" class="text-right font-semibold">Request Polygon Area:</label>
      <input id="request-polygon-area" type="checkbox" class="checkbox checkbox-primary" bind:checked={requestPolygonArea} />

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
              Hoofdstuk {chapterIndex + 1}
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

          <!-- Step Content -->
          {#if currentStep}
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

              <!-- Stap positie row: label left, PositionSelector button right -->
              <label for="step-position-btn" class="text-right font-semibold">Stap positie</label>
              <div class="col-span-3 mb-2">
                <PositionSelector
                  title="Selecteer stap positie"
                  buttonText="Selecteer stap positie op kaart"
                  initialPosition={currentStep.camera}
                  on:coordinatesSelected={(e) => {
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

              <!-- X/Y/Z row: empty col left, fields right -->
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

              <!-- Heading/Pitch/Duration row: empty col left, fields right -->
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

              <!-- Layers -->
              <div class="text-right font-semibold">Lagen:</div>
              <div class="col-span-3 max-h-32 overflow-y-auto border border-base-300 rounded-lg p-2">
                {#each availableLayers as layer}
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      class="checkbox checkbox-primary"
                      checked={currentStep.layers.includes(layer.id.toString())}
                      onchange={(e) => handleLayerChange(layer.id.toString(), e.currentTarget.checked)}
                    />
                    <span class="text-sm">{layer.title}</span>
                  </label>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <div class="col-span-12 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" onclick={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>