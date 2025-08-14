<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { createStory, fetchTerrainProviders, fetchLayers } from '$lib/api';
  import type { Story, TerrainProvider } from '$lib/types/tool';
  import type { Layer } from '$lib/types/layer';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Story }>();

  // Basic story fields
  let name = '';
  let description = '';
  let width = '600px';

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

    if (!name.trim()) {
      errorBanner?.show();
      return;
    }

    const content = {
      width,
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

    <!-- Basic Story Information -->
    <div class="col-span-12 grid grid-cols-4 gap-4 items-center">
      <label for="name" class="text-right font-semibold">Naam:</label>
      <input id="name" class="input input-bordered col-span-3 w-full" bind:value={name} required />

      <label for="description" class="text-right font-semibold">Beschrijving:</label>
      <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

      <label for="width" class="text-right font-semibold">Breedte:</label>
      <input id="width" class="input input-bordered col-span-3 w-full" bind:value={width} />
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

              <!-- Camera Position -->
              <span class="text-right font-semibold">Camera Positie (X, Y, Z):</span>
              <div class="col-span-3 flex gap-2">
                <input 
                  type="number" 
                  step="any" 
                  class="input input-bordered w-full" 
                  bind:value={currentStep.camera.x} 
                  placeholder="X-coördinaat"
                />
                <input 
                  type="number" 
                  step="any" 
                  class="input input-bordered w-full" 
                  bind:value={currentStep.camera.y} 
                  placeholder="Y-coördinaat"
                />
                <input 
                  type="number" 
                  step="any" 
                  class="input input-bordered w-full" 
                  bind:value={currentStep.camera.z} 
                  placeholder="Z-coördinaat"
                />
              </div>

              <!-- Camera Orientation -->
              <span class="text-right font-semibold">Oriëntatie & Duur:</span>
              <div class="col-span-3 flex gap-2">
                <input 
                  type="number" 
                  step="any" 
                  class="input input-bordered w-full" 
                  bind:value={currentStep.camera.heading} 
                  placeholder="Heading (graden)"
                />
                <input 
                  type="number" 
                  step="any" 
                  class="input input-bordered w-full" 
                  bind:value={currentStep.camera.pitch} 
                  placeholder="Pitch (graden)"
                />
                <input 
                  type="number" 
                  step="any" 
                  class="input input-bordered w-full" 
                  bind:value={currentStep.camera.duration} 
                  placeholder="Duur (seconden)"
                />
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
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>