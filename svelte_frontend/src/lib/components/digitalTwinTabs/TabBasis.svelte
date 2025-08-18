<script lang="ts">
  import { onMount } from 'svelte';
  import {
    fetchDigitalTwin,
    fetchDigitalTwinViewer,
    updateDigitalTwinViewer,
    fetchTools,
    bulkModifyToolAssociations
  } from '$lib/api';
  import type { DigitalTwin, DigitalTwinViewerResponse } from '$lib/types/digitalTwin';
  import type { BulkToolOperation } from '$lib/types/digitalTwinAssociation';
  import type { Tool } from '$lib/types/tool';

  export let digitalTwinId: string;

  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  let colorsOpen = false;
  let viewerData: DigitalTwinViewerResponse | null = null;
  let digitalTwinData: DigitalTwin | null = null;
  let error: string | null = null;

  // Local editable copies of fields
  let logo = '';
  let thumbnail = '';
  let startPosition = {
    x: 0,
    y: 0,
    z: 0,
    heading: 0,
    pitch: 0,
    duration: 0
  };
  let colors: Record<string, string> = {};
  let allTools: (Tool & { enabled: boolean; settings?: Record<string, any> })[] = [];
  let activeToolSettingsTab: number | null = null;

  // Reactive statement to calculate tools with settings
  $: toolsWithSettings = allTools.filter(tool => {
    if (!tool.enabled) return false;
    const booleanSettings = getConfigurableBooleanSettings(tool);
    const textSettings = getConfigurableTextSettings(tool);
    return booleanSettings.length > 0 || textSettings.length > 0;
  });

  // Reactive statement to initialize active tab
  $: {
    if (activeToolSettingsTab === null && toolsWithSettings.length > 0) {
      activeToolSettingsTab = toolsWithSettings[0].id;
    }
    
    // Reset if current active tab is no longer available
    if (activeToolSettingsTab !== null && !toolsWithSettings.some(tool => tool.id === activeToolSettingsTab)) {
      activeToolSettingsTab = toolsWithSettings.length > 0 ? toolsWithSettings[0].id : null;
    }
  }

  function toggleTool(toolId: number) {
    const tool = allTools.find((t) => t.id === toolId);
    if (tool) {
      tool.enabled = !tool.enabled;
      
      // Initialize settings if tool is being enabled and has default settings
      if (tool.enabled && tool.content?.settings) {
        tool.settings = { ...tool.content.settings };
      } else if (!tool.enabled) {
        // Clear settings when tool is disabled
        tool.settings = undefined;
      }
      
      // Trigger reactivity
      allTools = allTools;
    }
  }

  function toggleToolSetting(toolId: number, settingKey: string) {
    const tool = allTools.find((t) => t.id === toolId);
    if (tool && tool.settings) {
      tool.settings[settingKey] = !tool.settings[settingKey];
      // Trigger reactivity
      allTools = allTools;
    }
  }

  function updateToolTextSetting(toolId: number, settingKey: string, value: string) {
    const tool = allTools.find((t) => t.id === toolId);
    if (tool && tool.settings) {
      tool.settings[settingKey] = value;
      // Trigger reactivity
      allTools = allTools;
    }
  }

  // Helper function to get configurable boolean settings for a tool
  function getConfigurableBooleanSettings(tool: Tool) {
    if (!tool.content?.settings) return [];
    const currentTool = allTools.find(t => t.id === tool.id);
    return Object.entries(tool.content.settings)
      .filter(([_, value]) => typeof value === 'boolean')
      .map(([key, value]) => ({
        key,
        value: currentTool?.settings?.[key] ?? value,
        label: key // You may want to map key to a user-friendly label
      }));
  }

  // Helper function to get configurable text settings for a tool
  function getConfigurableTextSettings(tool: Tool) {
    if (!tool.content?.settings) return [];
    const currentTool = allTools.find(t => t.id === tool.id);
    return Object.entries(tool.content.settings)
      .filter(([_, value]) => typeof value === 'string')
      .map(([key, value]) => ({
        key,
        value: currentTool?.settings?.[key] ?? value,
        label: key, // Map to user-friendly label if needed
        multiline: key === 'description' // Or use a config for which fields are multiline
      }));
  }

  onMount(async () => {
    try {
      digitalTwinData = await fetchDigitalTwin(digitalTwinId);
      viewerData = await fetchDigitalTwinViewer(digitalTwinId);

      // Initialize local copies with safe defaults
      logo = viewerData.content.logo ?? '';
      thumbnail = viewerData.content.thumbnail ?? '';
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
        (digitalTwinData?.tool_associations ?? []).map((t) => t.tool_id)
      );

      // Combine tools with enabled info and settings
      allTools = toolsFromApi.map((tool: Tool) => {
        const enabled = enabledToolIds.has(tool.id);
        // Get existing settings from tool association if available
        const existingAssociation = digitalTwinData?.tool_associations?.find(assoc => assoc.tool_id === tool.id);
        const existingSettings = existingAssociation?.content || {};
        
        return {
          ...tool,
          enabled,
          settings: enabled ? { 
            ...tool.content?.settings, // Default settings from tool definition
            ...existingSettings // Override with saved settings
          } : undefined
        };
      });
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : String(e);
    }
  });

  async function handleSubmit() {
    try {
      // Get current enabled tools from state
      const currentlyEnabled = new Set(allTools.filter((t) => t.enabled).map((t) => t.id));

      // Get originally enabled tool IDs from viewer data
      const originallyEnabled = new Set(
        (digitalTwinData?.tool_associations ?? []).map((t) => t.tool_id)
      );

      // Tools to add and delete
      const toolsToAdd = [...currentlyEnabled].filter((id) => !originallyEnabled.has(id));
      const toolsToRemove = [...originallyEnabled].filter((id) => !currentlyEnabled.has(id));

      // Prepare operations for bulk API
      const operations: BulkToolOperation[] = [
        ...toolsToAdd.map((id) => {
          const tool = allTools.find(t => t.id === id);
          return {
            tool_id: id,
            action: 'create' as const,
            content: tool?.settings || {}
          };
        }),
        ...toolsToRemove.map((id) => ({ 
          tool_id: id, 
          action: 'delete' as const 
        }))
      ];

      // Add update operations for tools with changed settings
      for (const tool of allTools.filter(t => t.enabled && originallyEnabled.has(t.id))) {
        const originalAssociation = digitalTwinData?.tool_associations?.find(assoc => assoc.tool_id === tool.id);
        const originalSettings = originalAssociation?.content || {};
        
        // Check if settings have changed
        if (JSON.stringify(tool.settings) !== JSON.stringify(originalSettings)) {
          operations.push({
            tool_id: tool.id,
            action: 'update',
            content: tool.settings || {}
          });
        }
      }

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
      errorBanner?.show;
    }
  }
</script>

<!-- AlertBanners that are only visable after the submit button is pressed -->
<AlertBanner bind:this={successBanner} type="success" message="Digital Twin Viewer bijgewerkt!" />
<AlertBanner bind:this={errorBanner} type="error" message="Fout bij het opslaan!" />

{#if error}
  <div class="alert alert-error">{error}</div>
{:else if !viewerData}
  <div>Loading...</div>
{:else}
  <div class="space-y-6">
    <h2 class="text-2xl font-bold">Basis Instellingen</h2>
    <p class="text-base-content/70">Basis configuratie voor deze digital twin.</p>

    <div class="card bg-base-100 border-base-300 border">
      <div class="card-body space-y-4">
        <!-- Logo -->
        <div>
          <label for="logo-url" class="block font-medium">Logo URL</label>
          <input id="logo-url" type="text" bind:value={logo} class="input input-bordered w-full" />
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
          <legend class="font-semibold mb-2">Start positie</legend>
          
          <!-- Position Selector Button -->
          <div class="mb-4">
            <PositionSelector 
              title="Selecteer start positie"
              buttonText="Selecteer start positie op kaart"
              initialPosition={startPosition}
              on:coordinatesSelected={(e) => {
                startPosition = e.detail;
              }}
            />
          </div>

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
          <legend class="mb-2 font-semibold">Tools</legend>
          <div class="space-y-3">
            <div
              class="grid max-h-48 grid-cols-3 gap-2 overflow-auto rounded border border-gray-300 p-2"
            >
              {#each allTools as tool (tool.id)}
                <label class="flex cursor-pointer items-center space-x-2 select-none">
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
            
            <!-- Tool Settings -->
            {#if toolsWithSettings.length > 0}
              <div class="bg-base-50 rounded-lg">
                <h3 class="font-semibold text-base">Tool Settings</h3>
                <!-- Tool Settings Tabs -->
                <div class="tabs tabs-border">
                  {#each toolsWithSettings as tool, index (tool.id)}
                    {@const configurableBooleanSettings = getConfigurableBooleanSettings(tool)}
                    {@const configurableTextSettings = getConfigurableTextSettings(tool)}
                    <input 
                      type="radio" 
                      name="tool_settings_tabs" 
                      class="tab" 
                      aria-label={tool.name}
                      checked={activeToolSettingsTab === tool.id}
                      on:change={() => activeToolSettingsTab = tool.id}
                    />
                    <div class="tab-content border-base-300 bg-base-100 p-6">
                      <div class="space-y-4">
                        <!-- Boolean Settings -->
                        {#if configurableBooleanSettings.length > 0}
                          <div class="space-y-3">
                            <div class="flex items-center space-x-2">
                              <div class="w-1 h-4 bg-secondary rounded"></div>
                              <h5 class="font-semibold text-sm text-base-content uppercase tracking-wide">Opties</h5>
                            </div>
                            <div class="space-y-2 pl-3">
                              {#each configurableBooleanSettings as setting}
                                <label class="flex cursor-pointer items-center space-x-3 p-2 rounded-md hover:bg-base-50 transition-colors select-none">
                                  <input
                                    type="checkbox"
                                    checked={setting.value}
                                    on:change={() => toggleToolSetting(tool.id, setting.key)}
                                    class="checkbox checkbox-sm checkbox-secondary"
                                  />
                                  <span class="text-sm font-medium">{setting.label}</span>
                                </label>
                              {/each}
                            </div>
                          </div>
                        {/if}
                        
                        <!-- Text Settings -->
                        {#if configurableTextSettings.length > 0}
                          <div class="space-y-3">
                            <div class="flex items-center space-x-2">
                              <div class="w-1 h-4 bg-primary rounded"></div>
                              <h5 class="font-semibold text-sm text-base-content uppercase tracking-wide">Tekst instellingen</h5>
                            </div>
                            <div class="space-y-3 pl-3">
                              {#each configurableTextSettings as setting}
                                <div class="form-control">
                                  <label class="label" for="tool-{tool.id}-{setting.key}">
                                    <span class="label-text text-sm font-medium">{setting.label}</span>
                                  </label>
                                  {#if setting.multiline}
                                    <textarea
                                      id="tool-{tool.id}-{setting.key}"
                                      class="textarea textarea-bordered textarea-sm w-full focus:border-primary"
                                      rows="3"
                                      value={setting.value}
                                      on:input={(e) => updateToolTextSetting(tool.id, setting.key, (e.target as HTMLTextAreaElement)?.value || '')}
                                      placeholder={setting.label}
                                    ></textarea>
                                  {:else}
                                    <input
                                      id="tool-{tool.id}-{setting.key}"
                                      type="text"
                                      class="input input-bordered input-sm w-full focus:border-primary"
                                      value={setting.value}
                                      on:input={(e) => updateToolTextSetting(tool.id, setting.key, (e.target as HTMLInputElement)?.value || '')}
                                      placeholder={setting.label}
                                    />
                                  {/if}
                                </div>
                              {/each}
                            </div>
                          </div>
                        {/if}
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </fieldset>

        <!-- Colors with color pickers in 5 columns grid (defined by class grid-cols-5) -->
        <fieldset>
          <button
            type="button"
            class="m-0 flex w-full cursor-pointer items-center space-x-2 border-0 bg-transparent p-0 text-left font-semibold select-none"
            on:click={() => (colorsOpen = !colorsOpen)}
            aria-expanded={colorsOpen}
          >
            {#if colorsOpen}
              <img src="/icons/chevron-down.svg" alt="Open" class="h-5 w-5" />
            {:else}
              <img src="/icons/chevron-right.svg" alt="Closed" class="h-5 w-5" />
            {/if}
            <span>Colors</span>
          </button>

          {#if colorsOpen}
            <div class="mt-2 grid grid-cols-5 gap-4">
              {#each Object.entries(colors) as [key, value]}
                <div>
                  <label for={'color-' + key} class="block truncate font-medium">{key}</label>
                  <input
                    id={'color-' + key}
                    type="color"
                    bind:value={colors[key]}
                    class="h-8 w-12 rounded border border-gray-300 p-0"
                  />
                  <input
                    type="text"
                    bind:value={colors[key]}
                    class="input input-bordered mt-1 w-full"
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
