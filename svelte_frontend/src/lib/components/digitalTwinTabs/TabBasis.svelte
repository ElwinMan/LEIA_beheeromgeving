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
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';
  import ToolSettings from '$lib/components/ToolSettings.svelte';

  export let digitalTwinId: string;

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

  // Calculate tools with settings
  $: toolsWithSettings = allTools.filter(tool => {
    if (!tool.enabled) return false;
    
    // Check if tool has configurable settings
    if (!tool.content?.settings) {
      // Special case for featureinfo tool
      return tool.name?.toLowerCase() === 'featureinfo';
    }
    
    const hasConfigurableSettings = Object.values(tool.content.settings).some(value => 
      typeof value === 'boolean' || typeof value === 'string'
    );
    
    return hasConfigurableSettings || tool.name?.toLowerCase() === 'featureinfo';
  });

  // Set active tab when tools with settings change
  $: if (toolsWithSettings.length > 0) {
    if (activeToolSettingsTab === null || !toolsWithSettings.some(tool => tool.id === activeToolSettingsTab)) {
      activeToolSettingsTab = toolsWithSettings[0].id;
    }
  } else {
    activeToolSettingsTab = null;
  }

  // Tool setting tooltips lookup
  const toolSettingTooltips: Record<string, string> = {
    // LayerLibrary tool
    'useTags': "Optioneel: Als dit is ingesteld op 'true', is het mogelijk om datasets in de Bibliotheek te filteren op basis van hun tags.",

    // Info tool
    "title": "Titel van de digital twin.",
    "description": "Beschrijving van de digital twin.",

    // Help tool
    "showOnStart": "Toon het help tool bij het openen van de viewer.",
    "intro": "Introductie tekst voor het help tool, waarbij gebruik van html elementen mogelijk is.",

    // Geocoder tool
    "name": "Geocoder-tool, geplaatst in de rechterhoek van de header in plaats van de werkbalk, hiermee kan de gebruiker locaties opzoeken en er naartoe inzoomen.",

    // Flooding tool
    "scenariosBaseUrl": "Basis URL voor het scenario.",
    "breachUrl": "Basis URL voor de overstroming.",
    "roadsUrl": "Basis URL voor de wegen.",
    "floodedRoadsUrl": "Basis URL voor de overstroomde wegen.",

    // Config switcher tool
    "fullReload": "Of de volledige pagina opnieuw wordt geladen bij het wisselen van configuraties, wat de URL van de pagina zal veranderen. Indien false, worden alleen bepaalde componenten opnieuw geladen.",

  };

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
      allTools = [...allTools];
    }
  }

  // Event handlers for ToolSettings component
  function handleToggleSetting(event: CustomEvent) {
    const { toolId, settingKey } = event.detail;
    const tool = allTools.find((t) => t.id === toolId);
    if (tool && tool.settings) {
      tool.settings[settingKey] = !tool.settings[settingKey];
      allTools = [...allTools];
    }
  }

  function handleUpdateTextSetting(event: CustomEvent) {
    const { toolId, settingKey, value } = event.detail;
    const tool = allTools.find((t) => t.id === toolId);
    if (tool && tool.settings) {
      tool.settings[settingKey] = value;
      allTools = [...allTools];
    }
  }

  function handleUpdateFeatureInfoFields(event: CustomEvent) {
    const { fields } = event.detail;
    const featureInfoTool = allTools.find(t => t.name?.toLowerCase() === 'featureinfo');
    if (featureInfoTool && featureInfoTool.enabled) {
      featureInfoTool.settings = featureInfoTool.settings || {};
      featureInfoTool.settings.fields = fields.map((f: any) => ({ field: f.field, handler: f.handler }));
      allTools = [...allTools];
    }
  }

  function handleUpdateConnectors(event: CustomEvent) {
    const { toolId, connectors } = event.detail;
    const tool = allTools.find((t) => t.id === toolId);
    if (tool && tool.settings) {
      tool.settings.connectors = JSON.parse(JSON.stringify(connectors));
      allTools = [...allTools];
    }
  }

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
          <label for="logo-url" class="font-medium flex items-center gap-2">
            Logo URL
            <HelpTooltip tip="URL van het logo dat wordt weergegeven in de viewer." />
          </label>
          <input id="logo-url" type="text" bind:value={logo} class="input input-bordered w-full" />
        </div>

        <!-- Thumbnail -->
        <div>
          <label for="thumbnail-url" class="font-medium flex items-center gap-2">
            Thumbnail URL
            <HelpTooltip tip="URL van de thumbnail-afbeelding voor deze digital twin." />
          </label>
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
              <label for="start-x" class="font-medium flex items-center gap-2">
                X
                <HelpTooltip tip="X-coördinaat van de startpositie." />
              </label>
              <input
                id="start-x"
                type="number"
                step="any"
                bind:value={startPosition.x}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-y" class="font-medium flex items-center gap-2">
                Y
                <HelpTooltip tip="Y-coördinaat van de startpositie." />
              </label>
              <input
                id="start-y"
                type="number"
                step="any"
                bind:value={startPosition.y}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-z" class="font-medium flex items-center gap-2">
                Z
                <HelpTooltip tip="Z-coördinaat (hoogte) van de startpositie." />
              </label>
              <input
                id="start-z"
                type="number"
                step="any"
                bind:value={startPosition.z}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-heading" class="font-medium flex items-center gap-2">
                Heading
                <HelpTooltip tip="Kijkrichting (in graden) van de camera bij het starten." />
              </label>
              <input
                id="start-heading"
                type="number"
                step="any"
                bind:value={startPosition.heading}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-pitch" class="font-medium flex items-center gap-2">
                Pitch
                <HelpTooltip tip="Kantelhoek van de camera bij het starten." />
              </label>
              <input
                id="start-pitch"
                type="number"
                step="any"
                bind:value={startPosition.pitch}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-duration" class="font-medium flex items-center gap-2">
                Duration
                <HelpTooltip tip="Duur van de overgang naar de startpositie (in seconden)." />
              </label>
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
          <legend class="mb-2 font-semibold">Tools
            <HelpTooltip tip="Selecteer de tools die je wilt gebruiken voor deze digital twin." />
          </legend>
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
            
            <!-- Tool Settings with Tabs -->
            {#if toolsWithSettings.length > 0}
              <div class="bg-base-50 rounded-lg p-4">
                <h3 class="font-semibold text-base mb-4">Tool Settings
                  <HelpTooltip tip="Tool instellingen voor de geselecteerde tool." />
                </h3>

                <!-- Tool Settings Tabs -->
                <div class="tabs tabs-border">
                  {#each toolsWithSettings as tool, index (tool.id)}
                    <input 
                      type="radio" 
                      name="tool_settings_tabs" 
                      class="tab" 
                      aria-label={tool.name}
                      checked={activeToolSettingsTab === tool.id}
                      on:change={() => {activeToolSettingsTab = tool.id}}
                    />
                    <div class="tab-content border-base-300 bg-base-100 p-6">
                      <ToolSettings 
                        {tool}
                        {toolSettingTooltips}
                        on:toggleSetting={handleToggleSetting}
                        on:updateTextSetting={handleUpdateTextSetting}
                        on:updateFeatureInfoFields={handleUpdateFeatureInfoFields}
                        on:updateConnectors={handleUpdateConnectors}
                      />
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
            <span>Colors
              <HelpTooltip tip="Kleurinstellingen voor de digital twin." />
            </span>
          </button>

          {#if colorsOpen}
            <div class="mt-2 grid grid-cols-5 gap-4">
              {#each Object.entries(colors) as [key, value]}
                <div>
                  <label for={'color-' + key} class="truncate font-medium flex items-center gap-2">
                    {key}
                  </label>
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
