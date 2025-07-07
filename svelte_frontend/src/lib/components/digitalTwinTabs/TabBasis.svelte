<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchDigitalTwin, fetchDigitalTwinViewer, updateDigitalTwinViewer, fetchTools, bulkModifyToolAssociations } from '$lib/api';
  import type { DigitalTwin, DigitalTwinViewerResponse } from '$lib/types/digitalTwin';
  import type { BulkToolOperation } from '$lib/types/digitalTwinAssociation';
  import type { Tool } from '$lib/types/tool';
  import { ChevronDown, ChevronRight } from 'lucide-svelte';

  export let digitalTwinId: string;

  import AlertBanner from '$lib/components/AlertBanner.svelte';
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  let colorsOpen = false;
  let viewerData: DigitalTwinViewerResponse | null = null;
  let digitalTwinData: DigitalTwin | null = null;
  let error: string | null = null;

  // Local editable copies of fields
  let logo = "";
  let thumbnail = "";
  let startPosition = {
    x: 0,
    y: 0,
    z: 0,
    heading: 0,
    pitch: 0,
    duration: 0
  };
  let colors: Record<string, string> = {};
  let allTools: (Tool & { enabled: boolean })[] = [];


  function toggleTool(toolId: number) {
    const tool = allTools.find(t => t.id === toolId);
    if (tool) {
      tool.enabled = !tool.enabled;
    }
  }

  onMount(async () => {
    try {
      digitalTwinData = await fetchDigitalTwin(digitalTwinId);
      viewerData = await fetchDigitalTwinViewer(digitalTwinId);

      // Initialize local copies with safe defaults
      logo = viewerData.content.logo ?? "";
      thumbnail = viewerData.content.thumbnail ?? "";
      startPosition = {
        x: viewerData.content.startPosition?.x ?? 0,
        y: viewerData.content.startPosition?.y ?? 0,
        z: viewerData.content.startPosition?.z ?? 0,
        heading: viewerData.content.startPosition?.heading ?? 0,
        pitch: viewerData.content.startPosition?.pitch ?? 0,
        duration: viewerData.content.startPosition?.duration ?? 0
      };
      colors = { ...viewerData.content.colors };

      // Fetch tools
      const toolsFromApi = await fetchTools();

      // Get enabled tool IDs from the viewer's tool_associations
      // if tool_associations is undefined, use empty array
      const enabledToolIds = new Set(
        (digitalTwinData?.tool_associations ?? []).map(t => t.tool_id)
      );

      // Combine tools with enabled info
      allTools = toolsFromApi.map((tool: Tool) => ({
        ...tool,
        enabled: enabledToolIds.has(tool.id)
      }));

    } catch (e: unknown) {
      error = e instanceof Error ? e.message : String(e);
    }
  });

  async function handleSubmit() {
    try {
      // Get current enabled tools from state
      const currentlyEnabled = new Set(allTools.filter(t => t.enabled).map(t => t.id));

      // Get originally enabled tool IDs from viewer data
      const originallyEnabled = new Set(
        (digitalTwinData?.tool_associations ?? []).map(t => t.tool_id)
      );

      // Tools to add and delete
      const toolsToAdd = [...currentlyEnabled].filter(id => !originallyEnabled.has(id));
      const toolsToRemove = [...originallyEnabled].filter(id => !currentlyEnabled.has(id));

      // Prepare operations for bulk API
      const operations: BulkToolOperation[] = [
        ...toolsToAdd.map(id => ({ tool_id: id, action: "create" as const })),
        ...toolsToRemove.map(id => ({ tool_id: id, action: "delete" as const })),
      ];

      // Call bulk API only if there are operations
      if (operations.length > 0) {
        await bulkModifyToolAssociations(digitalTwinId, operations);
      }

      // Update viewer content
      await updateDigitalTwinViewer(digitalTwinId, {
        logo,
        thumbnail,
        startPosition,
        colors
      });

      successBanner?.show();
    } catch (err) {
      console.error(err);
      errorBanner?.show
    }
  }
</script>

<!-- AlertBanners that are only visable after the submit button is pressed -->
<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Digital Twin Viewer bijgewerkt!"
/>
<AlertBanner
  bind:this={errorBanner}
  type="error"
  message="Fout bij het opslaan!"
/>

{#if error}
  <div class="alert alert-error">{error}</div>
{:else if !viewerData}
  <div>Loading...</div>
{:else}
  <div class="space-y-6">
    <h2 class="text-2xl font-bold">Basis Instellingen</h2>
    <p class="text-base-content/70">Basis configuratie voor deze digital twin.</p>

    <div class="card bg-base-100 border border-base-300">
      <div class="card-body space-y-4">
        <!-- Logo -->
        <div>
          <label for="logo-url" class="block font-medium">Logo URL</label>
          <input
            id="logo-url"
            type="text"
            bind:value={logo}
            class="input input-bordered w-full"
          />
        </div>

        <!-- Thumbnail -->
        <div>
          <label for="thumbnail-url" class="block font-medium">Thumbnail URL</label>
          <input
            id="thumbnail-url"
            type="text"
            bind:value={thumbnail}
            class="input input-bordered w-full"
          />
        </div>

        <!-- Start Position in 3 columns (defined by grid-cols-3)-->
        <fieldset>
          <legend class="font-semibold">Start positie</legend>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label for="start-x" class="block font-medium">X</label>
              <input
                id="start-x"
                type="number"
                step="any"
                bind:value={startPosition.x}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-y" class="block font-medium">Y</label>
              <input
                id="start-y"
                type="number"
                step="any"
                bind:value={startPosition.y}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-z" class="block font-medium">Z</label>
              <input
                id="start-z"
                type="number"
                step="any"
                bind:value={startPosition.z}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-heading" class="block font-medium">Heading</label>
              <input
                id="start-heading"
                type="number"
                step="any"
                bind:value={startPosition.heading}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-pitch" class="block font-medium">Pitch</label>
              <input
                id="start-pitch"
                type="number"
                step="any"
                bind:value={startPosition.pitch}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-duration" class="block font-medium">Duration</label>
              <input
                id="start-duration"
                type="number"
                step="any"
                bind:value={startPosition.duration}
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </fieldset>

        <!-- Tools checkboxes list in 3 column grid (defined by class grid-cols-3) -->
        <fieldset>
          <legend class="font-semibold mb-2">Tools</legend>
          <div class="max-h-48 overflow-auto border border-gray-300 rounded p-2 grid grid-cols-3 gap-2">
            {#each allTools as tool (tool.id)}
              <label class="flex items-center space-x-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={tool.enabled}
                  on:change={() => toggleTool(tool.id)}
                  class="checkbox checkbox-primary"
                />
                <span>{tool.name}</span>
              </label>
            {/each}
          </div>
        </fieldset>

        <!-- Colors with color pickers in 5 columns grid (defined by class grid-cols-5) -->
        <fieldset>
          <button
            type="button"
            class="w-full text-left font-semibold flex items-center space-x-2 cursor-pointer select-none p-0 m-0 border-0 bg-transparent"
            on:click={() => (colorsOpen = !colorsOpen)}
            aria-expanded={colorsOpen}
          >
            {#if colorsOpen}
              <ChevronDown class="w-5 h-5" />
            {:else}
              <ChevronRight class="w-5 h-5" />
            {/if}
            <span>Colors</span>
          </button>

          {#if colorsOpen}
            <div class="grid grid-cols-5 gap-4 mt-2">
              {#each Object.entries(colors) as [key, value]}
                <div>
                  <label for={"color-" + key} class="block font-medium truncate">{key}</label>
                  <input
                    id={"color-" + key}
                    type="color"
                    bind:value={colors[key]}
                    class="w-12 h-8 p-0 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    bind:value={colors[key]}
                    class="input input-bordered w-full mt-1"
                  />
                </div>
              {/each}
            </div>
          {/if}
        </fieldset>

        <button on:click={handleSubmit} class="btn btn-primary mt-4">Opslaan</button>
      </div>
    </div>
  </div>
{/if}